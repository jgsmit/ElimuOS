from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CustomUser, LoginHistory, UserSession


class CustomUserTests(TestCase):
    def test_student_id_is_generated_for_students(self):
        user = get_user_model().objects.create_user(username='student', password='test-pass-123')
        self.assertEqual(user.role, CustomUser.Role.STUDENT)
        self.assertTrue(user.student_id.startswith('STU-'))
        self.assertIsNone(user.staff_id)

    def test_staff_id_is_generated_for_non_students(self):
        user = get_user_model().objects.create_user(
            username='teacher',
            password='test-pass-123',
            role=CustomUser.Role.TEACHER,
        )
        self.assertTrue(user.staff_id.startswith('STF-'))
        self.assertIsNone(user.student_id)

    def test_login_redirects_to_role_dashboard_and_tracks_login(self):
        get_user_model().objects.create_user(
            username='teacher',
            password='test-pass-123',
            role=CustomUser.Role.TEACHER,
        )
        response = self.client.post(reverse('login'), {'username': 'teacher', 'password': 'test-pass-123'})
        self.assertRedirects(response, reverse('dashboard_teacher'))
        self.assertEqual(LoginHistory.objects.count(), 1)
        self.assertEqual(UserSession.objects.count(), 1)

    def test_rbac_blocks_other_role_dashboards(self):
        get_user_model().objects.create_user(username='student', password='test-pass-123')
        self.client.login(username='student', password='test-pass-123')
        response = self.client.get(reverse('dashboard_teacher'))
        self.assertEqual(response.status_code, 403)
