from django.contrib import admin

from .models import School, SchoolBranding


class SchoolBrandingInline(admin.StackedInline):
    model = SchoolBranding
    can_delete = False
    extra = 0


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'hostname', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'hostname')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SchoolBrandingInline]


@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    list_display = ('school', 'display_name', 'primary_color', 'secondary_color', 'accent_color')
    search_fields = ('school__name', 'display_name', 'motto')
