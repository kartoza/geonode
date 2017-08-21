from django.contrib.auth.decorators import login_required

__author__ = 'Irwan Fathurrahman <irwan@kartoza.com>'
__date__ = '14/06/17'

import json
import os
from django.conf import settings
from django.http import HttpResponse


@login_required
def upload_chunk(request, uuid):
    """Upload chunk handle.
    """
    try:
        if request.method == 'POST':
            _file = request.FILES["file"]
            filename = request.POST["filename"]
            offset = long(request.POST["offset"])
            filesize = request.POST["file_size"]
            # folder for this campaign
            foldername = os.path.join(
                settings.TEMP_FOLDER,
                'chunk',
                uuid
            )
            if not os.path.exists(foldername):
                os.makedirs(foldername)

            # filename
            filename = os.path.join(
                foldername,
                filename
            )

            if offset == 0:
                if os.path.exists(filename):
                    os.remove(filename)
            with open(filename, 'ab') as f:
                f.seek(offset)
                f.write(_file.read())

            # send response with appropriate mime type header
            return HttpResponse(status=200, content=json.dumps({
                "name": filename,
                "size": os.path.getsize(filename),
                "thumbnail_url": None,
                "delete_url": None,
                "delete_type": None
            }))
        else:
            return HttpResponse(content=json.dumps({
                "message": "Get Not Accepted"
            }), status=402)
    except Exception as e:
        return HttpResponse(content=json.dumps({
            "message": "%s" % e
        }), status=500)
