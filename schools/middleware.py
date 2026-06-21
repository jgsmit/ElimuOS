from django.http import Http404

from .models import School


class TenantMiddleware:
    """Resolve the active school tenant from hostname or a `school` query slug."""

    RESERVED_HOSTS = {'localhost', '127.0.0.1', 'testserver'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.school = self.resolve_school(request)
        request.tenant = request.school
        return self.get_response(request)

    def resolve_school(self, request):
        slug = request.GET.get('school') or request.session.get('school_slug')
        if slug:
            school = self._get_school(slug=slug)
            request.session['school_slug'] = school.slug
            return school

        hostname = request.get_host().split(':')[0].lower()
        if hostname in self.RESERVED_HOSTS:
            return None
        return self._get_school(hostname=hostname)

    def _get_school(self, **lookup):
        try:
            return School.objects.select_related('branding').get(is_active=True, **lookup)
        except School.DoesNotExist as exc:
            raise Http404('School tenant was not found or is inactive.') from exc
