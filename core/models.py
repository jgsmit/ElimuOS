from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Security audit record for important tenant-scoped user actions."""

    school = models.ForeignKey('schools.School', on_delete=models.SET_NULL, related_name='audit_logs', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='audit_logs', blank=True, null=True)
    action = models.CharField(max_length=120)
    method = models.CharField(max_length=12, blank=True)
    path = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        actor = self.user or 'anonymous'
        return f'{self.action} by {actor} at {self.created_at:%Y-%m-%d %H:%M}'
