from django.contrib import admin

from .models import Announcement, AnnouncementReceipt, Message, MessageReceipt


class MessageReceiptInline(admin.TabularInline):
    model = MessageReceipt
    extra = 0
    readonly_fields = ('recipient', 'delivered_at', 'read_at')
    can_delete = False


class AnnouncementReceiptInline(admin.TabularInline):
    model = AnnouncementReceipt
    extra = 0
    readonly_fields = ('recipient', 'delivered_at', 'read_at')
    can_delete = False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'school', 'sender', 'message_type', 'priority', 'created_at')
    list_filter = ('school', 'message_type', 'priority', 'created_at')
    search_fields = ('subject', 'body', 'sender__username', 'recipient_user__username')
    inlines = [MessageReceiptInline]


@admin.register(MessageReceipt)
class MessageReceiptAdmin(admin.ModelAdmin):
    list_display = ('message', 'recipient', 'delivered_at', 'read_at')
    list_filter = ('delivered_at', 'read_at')
    search_fields = ('message__subject', 'recipient__username')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'target_class', 'target_role', 'priority', 'published_at', 'expires_at')
    list_filter = ('school', 'priority', 'published_at', 'expires_at')
    search_fields = ('title', 'body', 'created_by__username')
    inlines = [AnnouncementReceiptInline]


@admin.register(AnnouncementReceipt)
class AnnouncementReceiptAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'recipient', 'delivered_at', 'read_at')
    list_filter = ('delivered_at', 'read_at')
    search_fields = ('announcement__title', 'recipient__username')
