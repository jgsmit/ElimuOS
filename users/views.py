from django.contrib.auth.views import LoginView
from django.urls import reverse

from .models import LoginHistory, UserSession
from .rbac import dashboard_name_for_role


def _client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class ShuleYanguLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        ip_address = _client_ip(self.request)
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        LoginHistory.objects.create(user=user, ip_address=ip_address, user_agent=user_agent)
        UserSession.objects.update_or_create(
            session_key=self.request.session.session_key,
            defaults={'user': user, 'ip_address': ip_address, 'user_agent': user_agent, 'ended_at': None},
        )
        return response

    def get_success_url(self):
        next_url = self.get_redirect_url()
        if next_url:
            return next_url
        return reverse(dashboard_name_for_role(self.request.user.role))
