from django.test import RequestFactory, TestCase

from .context_processors import tenant
from .middleware import TenantMiddleware
from .models import School, SchoolBranding


class TenantMiddlewareTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Demo School', slug='demo', hostname='demo.testserver')
        self.middleware = TenantMiddleware(lambda request: None)
        self.factory = RequestFactory()

    def test_resolves_school_by_hostname(self):
        request = self.factory.get('/', HTTP_HOST='demo.testserver')
        request.session = {}
        self.middleware(request)
        self.assertEqual(request.school, self.school)

    def test_resolves_school_by_slug_query_and_stores_session(self):
        request = self.factory.get('/?school=demo', HTTP_HOST='localhost')
        request.session = {}
        self.middleware(request)
        self.assertEqual(request.school, self.school)
        self.assertEqual(request.session['school_slug'], 'demo')

    def test_context_processor_exposes_school_branding(self):
        branding = SchoolBranding.objects.create(school=self.school, display_name='Demo Academy')
        request = self.factory.get('/', HTTP_HOST='localhost')
        request.school = self.school
        context = tenant(request)
        self.assertEqual(context['current_school'], self.school)
        self.assertEqual(context['school_branding'], branding)
