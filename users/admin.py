from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, LoginHistory, UserSession


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'school', 'role', 'staff_id', 'student_id', 'is_staff', 'is_active')
    list_filter = ('school', 'role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Shule Yangu Profile', {'fields': ('school', 'role', 'phone', 'address', 'profile_picture', 'staff_id', 'student_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Shule Yangu Profile', {'fields': ('school', 'role', 'phone', 'address', 'profile_picture')}),
    )
    readonly_fields = ('staff_id', 'student_id')


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'logged_in_at')
    search_fields = ('user__username', 'ip_address', 'user_agent')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'logged_in_at')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'created_at', 'last_seen_at', 'ended_at')
    list_filter = ('ended_at',)
    search_fields = ('user__username', 'session_key', 'ip_address')
    readonly_fields = ('user', 'session_key', 'ip_address', 'user_agent', 'created_at', 'last_seen_at', 'ended_at')
