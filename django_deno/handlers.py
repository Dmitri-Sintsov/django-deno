from django.contrib.staticfiles.handlers import StaticFilesHandler

from .views import serve


class RollupFilesHandler(StaticFilesHandler):

    def serve(self, request):
        """Serve the request path."""
        return serve(request, self.file_path(request.path), insecure=True)
