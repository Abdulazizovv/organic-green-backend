from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore

class CustomSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_key = request.headers.get("X-Session-Key")
        if session_key:
            request.session = SessionStore(session_key=session_key)
        response = self.get_response(request)
        return response