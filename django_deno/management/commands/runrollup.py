import json
import mimetypes
import os
import posixpath
import requests
import traceback

from requests.exceptions import ConnectionError
from pathlib import Path

from django.http import (
    HttpResponse, FileResponse, Http404, HttpResponseNotModified, StreamingHttpResponse
)
from django.utils._os import safe_join
from django.utils.http import http_date
from django.utils.translation import gettext as _
from django.conf import settings
from django.views.static import directory_index, was_modified_since
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.contrib.staticfiles.management.commands import runserver


rollup_hints = [b'"use rollup"', b"'use rollup'"]
proxy_chunk_size = 256 * 1024


def should_rollup(fullpath):
    with fullpath.open('rb') as f:
        hint = f.read(len(rollup_hints[0]))
        return hint in rollup_hints


def get_rollup_response(fullpath, content_type):
    try:
        rollup_response = requests.post(
            'http://127.0.0.1:8000/rollup/',
            data={'filename': str(fullpath)},
            stream=True
        )
        if rollup_response.status_code == 200:
            return StreamingHttpResponse(
                rollup_response.iter_content(chunk_size=proxy_chunk_size), content_type=content_type
            )
        else:
            response = HttpResponse('throw Error({});'.format(json.dumps(rollup_response.text)))
            response.status_code = rollup_response.status_code
            return response
    except ConnectionError as ex:
        ex_string = json.dumps('\n'.join(
            list(traceback.TracebackException.from_exception(ex).format())
        ))
        return HttpResponse(f'throw Error({ex_string});', content_type=content_type)


# from django.views.static import serve
def serve_rollup(request, path, document_root=None, show_indexes=False):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        from django.views.static import serve

        path('<path:path>', serve, {'document_root': '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """
    path = posixpath.normpath(path).lstrip('/')
    fullpath = Path(safe_join(document_root, path))
    if fullpath.is_dir():
        if show_indexes:
            return directory_index(path, fullpath)
        raise Http404(_("Directory indexes are not allowed here."))
    if not fullpath.exists():
        raise Http404(_('“%(path)s” does not exist') % {'path': fullpath})
    statobj = fullpath.stat()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or 'application/octet-stream'
    if content_type == "application/javascript" and should_rollup(fullpath):
        response = get_rollup_response(fullpath, content_type)
        if not isinstance(response, StreamingHttpResponse):
            # report error
            return response
    else:
        # Respect the If-Modified-Since header.
        if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                                  statobj.st_mtime, statobj.st_size):
            return HttpResponseNotModified()
        response = FileResponse(fullpath.open('rb'), content_type=content_type)
    response["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response["Content-Encoding"] = encoding
    return response


# from django.contrib.staticfiles.views import serve
def serve(request, path, insecure=False, **kwargs):
    """
    Serve static files below a given point in the directory structure or
    from locations inferred from the staticfiles finders.

    To use, put a URL pattern such as::

        from django.contrib.staticfiles import views

        path('<path:path>', views.serve)

    in your URLconf.

    It uses the django.views.static.serve() view to serve the found files.
    """
    if not settings.DEBUG and not insecure:
        raise Http404
    normalized_path = posixpath.normpath(path).lstrip('/')
    absolute_path = finders.find(normalized_path)
    if not absolute_path:
        if path.endswith('/') or path == '':
            raise Http404("Directory indexes are not allowed here.")
        raise Http404("'%s' could not be found" % path)
    document_root, path = os.path.split(absolute_path)
    return serve_rollup(request, path, document_root=document_root, **kwargs)


class RollupFilesHandler(StaticFilesHandler):

    def serve(self, request):
        """Serve the request path."""
        return serve(request, self.file_path(request.path), insecure=True)


class Command(runserver.Command):

    def get_handler(self, *args, **options):
        """
        Return the static files serving handler wrapping the default handler,
        if static files should be served. Otherwise return the default handler.
        """
        handler = super().get_handler(*args, **options)
        use_static_handler = options['use_static_handler']
        insecure_serving = options['insecure_serving']
        if use_static_handler and (settings.DEBUG or insecure_serving):
            return RollupFilesHandler(handler)
        return handler
