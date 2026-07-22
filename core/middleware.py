from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import AuditLog
from .privacy import redact_mapping


class SessionTimeoutMiddleware:
    """Expire authenticated sessions after a configurable idle period."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout_seconds = getattr(settings, 'SESSION_TIMEOUT_SECONDS', 1800)

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now().timestamp()
            last_activity = request.session.get('last_activity_at')
            if last_activity and now - float(last_activity) > self.timeout_seconds:
                logout(request)
                return redirect(reverse('login'))
            request.session['last_activity_at'] = now
        return self.get_response(request)


class AuditLogMiddleware:
    """Capture audited write requests with privacy-safe metadata."""

    AUDITED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method in self.AUDITED_METHODS and getattr(request, 'user', None) and request.user.is_authenticated:
            AuditLog.objects.create(
                school=getattr(request, 'school', None) or getattr(request.user, 'school', None),
                user=request.user,
                action=f'{request.method} {request.resolver_match.view_name if request.resolver_match else request.path}',
                method=request.method,
                path=request.path[:255],
                ip_address=self._client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata=redact_mapping(request.POST.dict()),
            )
        return response

    @staticmethod
    def _client_ip(request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
