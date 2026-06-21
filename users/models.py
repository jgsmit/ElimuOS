from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """Application user with Phase 2 role and profile foundations."""

    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        SCHOOL_ADMIN = 'school_admin', 'School Admin'
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'
        PARENT = 'parent', 'Parent'
        COUNSELOR = 'counselor', 'Counselor'
        LIBRARIAN = 'librarian', 'Librarian'
        HOSTEL_STAFF = 'hostel_staff', 'Hostel Staff'

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.PROTECT,
        related_name='users',
        blank=True,
        null=True,
        help_text='Tenant school this user belongs to. Super admins may be global.',
    )
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    staff_id = models.CharField(max_length=32, unique=True, blank=True, null=True)
    student_id = models.CharField(max_length=32, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    @property
    def is_staff_role(self):
        return self.role != self.Role.STUDENT

    def save(self, *args, **kwargs):
        if self.role == self.Role.STUDENT and not self.student_id:
            self.student_id = _next_identifier('STU', 'student_id')
        elif self.role != self.Role.STUDENT and not self.staff_id:
            self.staff_id = _next_identifier('STF', 'staff_id')
        super().save(*args, **kwargs)


def _next_identifier(prefix, field_name):
    year = timezone.now().year
    existing_count = CustomUser.objects.filter(**{f'{field_name}__startswith': f'{prefix}-{year}-'}).count()
    return f'{prefix}-{year}-{existing_count + 1:05d}'


class LoginHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    logged_in_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_in_at']
        verbose_name_plural = 'login histories'

    def __str__(self):
        return f'{self.user} at {self.logged_in_at:%Y-%m-%d %H:%M}'


class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tracked_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-last_seen_at']

    @property
    def is_active(self):
        return self.ended_at is None

    def end(self):
        self.ended_at = timezone.now()
        self.save(update_fields=['ended_at', 'last_seen_at'])

    def __str__(self):
        return f'{self.user} session {self.session_key}'
