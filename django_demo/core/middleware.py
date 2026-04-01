import logging
import time

from django.http import HttpResponse
from django.shortcuts import render

logger = logging.getLogger("core")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.2fms)",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        return response


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "same-origin"
        response["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net"
        return response


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            logger.exception("Unhandled application error at %s", request.path)
            if request.headers.get("Accept") == "application/json":
                return HttpResponse("{\"detail\": \"Server error\"}", status=500, content_type="application/json")
            return render(request, "core/errors/500.html", status=500)
