from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from users.models import CustomUser


class Priority(models.TextChoices):
    LOW = 'low', 'Low'
    NORMAL = 'normal', 'Normal'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class Message(models.Model):
    class MessageType(models.TextChoices):
        DIRECT = 'direct', 'Direct Message'
        CLASS = 'class', 'Class Message'
        GROUP = 'group', 'Group Message'

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='sent_messages', blank=True, null=True)
    message_type = models.CharField(max_length=16, choices=MessageType.choices)
    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_direct_messages', blank=True, null=True)
    recipient_class = models.ForeignKey('academics.SchoolClass', on_delete=models.CASCADE, related_name='class_messages', blank=True, null=True)
    recipient_role = models.CharField(max_length=32, choices=CustomUser.Role.choices, blank=True)
    subject = models.CharField(max_length=180)
    body = models.TextField()
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.NORMAL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.sender and self.sender.school_id and self.sender.school_id != self.school_id:
            raise ValidationError({'sender': 'Sender must belong to the same school as the message.'})
        if self.message_type == self.MessageType.DIRECT:
            if not self.recipient_user:
                raise ValidationError({'recipient_user': 'Direct messages require a recipient user.'})
            if self.recipient_user.school_id and self.recipient_user.school_id != self.school_id:
                raise ValidationError({'recipient_user': 'Recipient must belong to the same school as the message.'})
        elif self.message_type == self.MessageType.CLASS:
            if not self.recipient_class:
                raise ValidationError({'recipient_class': 'Class messages require a recipient class.'})
            if self.recipient_class.school_id != self.school_id:
                raise ValidationError({'recipient_class': 'Recipient class must belong to the same school as the message.'})
        elif self.message_type == self.MessageType.GROUP and not self.recipient_role:
            raise ValidationError({'recipient_role': 'Group messages require a recipient role.'})

    def recipients(self):
        if self.message_type == self.MessageType.DIRECT:
            return CustomUser.objects.filter(pk=self.recipient_user_id)
        if self.message_type == self.MessageType.CLASS:
            student_ids = self.recipient_class.enrollments.filter(is_active=True).values_list('student_id', flat=True)
            return CustomUser.objects.filter(pk__in=student_ids)
        if self.message_type == self.MessageType.GROUP:
            return CustomUser.objects.filter(school=self.school, role=self.recipient_role, is_active=True)
        return CustomUser.objects.none()

    def create_receipts(self):
        receipts = []
        for user in self.recipients():
            receipt, _ = MessageReceipt.objects.get_or_create(message=self, recipient=user)
            receipts.append(receipt)
        return receipts

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject


class MessageReceipt(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='receipts')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_receipts')
    delivered_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-delivered_at']
        constraints = [models.UniqueConstraint(fields=['message', 'recipient'], name='unique_message_receipt_per_recipient')]

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])

    def __str__(self):
        return f'{self.message} -> {self.recipient}'


class Announcement(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='announcements')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='created_announcements', blank=True, null=True)
    target_class = models.ForeignKey('academics.SchoolClass', on_delete=models.CASCADE, related_name='announcements', blank=True, null=True)
    target_role = models.CharField(max_length=32, choices=CustomUser.Role.choices, blank=True)
    title = models.CharField(max_length=180)
    body = models.TextField()
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.NORMAL)
    published_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-published_at']

    def clean(self):
        if self.created_by and self.created_by.school_id and self.created_by.school_id != self.school_id:
            raise ValidationError({'created_by': 'Creator must belong to the same school as the announcement.'})
        if self.target_class and self.target_class.school_id != self.school_id:
            raise ValidationError({'target_class': 'Target class must belong to the same school as the announcement.'})
        if self.expires_at and self.expires_at <= self.published_at:
            raise ValidationError({'expires_at': 'Expiry time must be after publish time.'})
        if self.target_class and self.target_role:
            raise ValidationError('Use either a target class or a target role, not both.')

    @property
    def is_active(self):
        return not self.expires_at or self.expires_at > timezone.now()

    def recipients(self):
        if self.target_class:
            student_ids = self.target_class.enrollments.filter(is_active=True).values_list('student_id', flat=True)
            return CustomUser.objects.filter(pk__in=student_ids)
        if self.target_role:
            return CustomUser.objects.filter(school=self.school, role=self.target_role, is_active=True)
        return CustomUser.objects.filter(school=self.school, is_active=True)

    def create_receipts(self):
        receipts = []
        for user in self.recipients():
            receipt, _ = AnnouncementReceipt.objects.get_or_create(announcement=self, recipient=user)
            receipts.append(receipt)
        return receipts

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AnnouncementReceipt(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='receipts')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcement_receipts')
    delivered_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-delivered_at']
        constraints = [models.UniqueConstraint(fields=['announcement', 'recipient'], name='unique_announcement_receipt_per_recipient')]

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])

    def __str__(self):
        return f'{self.announcement} -> {self.recipient}'
