from django.utils import timezone

from .models import UserSession


class SessionActivityMiddleware:
    """Keep the current authenticated session activity timestamp fresh."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.session.session_key:
            UserSession.objects.filter(
                user=request.user,
                session_key=request.session.session_key,
                ended_at__isnull=True,
            ).update(last_seen_at=timezone.now())
        return response
