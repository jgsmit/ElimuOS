from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'school', 'method', 'path', 'ip_address', 'created_at')
    list_filter = ('school', 'method', 'action', 'created_at')
    search_fields = ('action', 'user__username', 'path', 'ip_address')
    readonly_fields = ('school', 'user', 'action', 'method', 'path', 'ip_address', 'user_agent', 'metadata', 'created_at')
