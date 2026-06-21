from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.utils import timezone

from .models import UserSession


@receiver(user_logged_out)
def mark_session_ended(sender, request, user, **kwargs):
    if user and request and request.session.session_key:
        UserSession.objects.filter(
            user=user,
            session_key=request.session.session_key,
            ended_at__isnull=True,
        ).update(ended_at=timezone.now(), last_seen_at=timezone.now())
