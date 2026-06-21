from django.db import models


class School(models.Model):
    """Tenant record for a single school in Shule Yangu."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=80, unique=True)
    hostname = models.CharField(max_length=255, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SchoolBranding(models.Model):
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='branding')
    display_name = models.CharField(max_length=255, blank=True)
    motto = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#0d6efd')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    accent_color = models.CharField(max_length=7, default='#198754')

    class Meta:
        verbose_name_plural = 'school branding'

    def __str__(self):
        return f'Branding for {self.school}'

    @property
    def name(self):
        return self.display_name or self.school.name
