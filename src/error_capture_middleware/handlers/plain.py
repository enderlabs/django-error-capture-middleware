from django.http import HttpResponse

from error_capture_middleware import ErrorCaptureHandler


class PlainExceptionsMiddleware(ErrorCaptureHandler):
    def handle(self, request, exception, tb):
        return HttpResponse("\n".join(tb),
                            content_type="text/plain", status=500)