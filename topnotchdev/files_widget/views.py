from django.http import Http404, HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image

import json

from settings import FILES_DIR, PROJECT_DIR, IMAGE_QUALITY
from controllers import ImagePath


def upload(request):
    if not request.method == 'POST':
        raise Http404

    response_data = {}
    if request.is_ajax():
        if request.FILES:
            files = request.FILES.values()[0]
            path = default_storage.save('{}{}/{}'.format(FILES_DIR,
                                                          request.user.pk,
                                                          files.name), ContentFile(files.read()))
            try:
                full_path = PROJECT_DIR+'/'+path
                img = Image.open(full_path)
                img.save(full_path, quality=IMAGE_QUALITY)
            except:
                pass
                
            try:
                preview_size = request.POST['preview_size']
            except KeyError:
                preview_size = '64'
            response_data['status'] = True
            response_data['imagePath'] = path
            response_data['thumbnail'] = render_to_string('files_widget/includes/thumbnail.html',
                                                          {'MEDIA_URL': settings.MEDIA_URL,
                                                           'STATIC_URL': settings.STATIC_URL,
                                                           'preview_size': preview_size})
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        else:
            response_data['status'] = False
            response_data['message'] = "We're sorry, but something went wrong."
            return HttpResponse(json.dumps(response_data), content_type='application/json')


def thumbnail_url(request):
    if not 'img' in request.GET or not 'preview_size' in request.GET:
        raise Http404
    
    thumbnail_url = ImagePath(request.GET['img']).thumbnail(request.GET['preview_size']).url
    return HttpResponse(thumbnail_url)
