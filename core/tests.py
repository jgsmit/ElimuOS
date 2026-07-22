from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from academics.models import AcademicSession, Attendance, ClassSubject, SchoolClass, StudentEnrollment, Subject
from communications.models import Message
from core.services import DashboardService
from examinations.models import Exam, ExamType, GradeBand, GradingSystem, Result
from library.models import Book, BookBorrowing, BookCategory
from schools.models import School
from users.models import CustomUser


class DashboardServiceTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Demo School', slug='demo', hostname='demo.testserver')
        self.admin = get_user_model().objects.create_user(username='admin', password='test-pass-123', role=CustomUser.Role.SCHOOL_ADMIN, school=self.school)
        self.teacher = get_user_model().objects.create_user(username='teacher', password='test-pass-123', role=CustomUser.Role.TEACHER, school=self.school)
        self.student = get_user_model().objects.create_user(username='student', password='test-pass-123', role=CustomUser.Role.STUDENT, school=self.school)
        self.session = AcademicSession.objects.create(school=self.school, name='2026', start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), is_active=True)
        self.school_class = SchoolClass.objects.create(school=self.school, name='Grade 1', level=1, capacity=40)
        self.subject = Subject.objects.create(school=self.school, name='Mathematics', code='MATH')
        ClassSubject.objects.create(school_class=self.school_class, subject=self.subject, teacher=self.teacher)
        self.enrollment = StudentEnrollment.objects.create(student=self.student, school_class=self.school_class, session=self.session)
        Attendance.objects.create(enrollment=self.enrollment, subject=self.subject, date=date(2026, 7, 1), status=Attendance.Status.PRESENT)
        exam_type = ExamType.objects.create(school=self.school, name='Final', weight=Decimal('100.00'))
        exam = Exam.objects.create(exam_type=exam_type, session=self.session, school_class=self.school_class, subject=self.subject, title='Final', total_marks=Decimal('100.00'), created_by=self.teacher)
        grading = GradingSystem.objects.create(school=self.school, name='Default', is_default=True)
        GradeBand.objects.create(grading_system=grading, grade='A', min_score=80, max_score=100, points=4)
        Result.objects.create(exam=exam, enrollment=self.enrollment, marks_obtained=Decimal('90.00'))
        category = BookCategory.objects.create(school=self.school, name='Textbooks')
        book = Book.objects.create(school=self.school, category=category, title='Math Book', total_copies=2)
        BookBorrowing.objects.create(book=book, borrower=self.student, borrowed_at=date(2026, 7, 1), due_date=date(2026, 7, 10))
        Message.objects.create(school=self.school, sender=self.admin, message_type=Message.MessageType.DIRECT, recipient_user=self.teacher, subject='Hello', body='Body').create_receipts()

    def test_school_admin_dashboard_counts_school_activity(self):
        data = DashboardService.for_user(self.admin, self.school)
        self.assertEqual(data['title'], 'School Admin Dashboard')
        self.assertEqual(data['metrics'][0]['value'], 1)
        self.assertEqual(data['metrics'][1]['value'], 1)

    def test_teacher_dashboard_counts_assignments_and_results(self):
        data = DashboardService.for_user(self.teacher, self.school)
        self.assertEqual(data['metrics'][0]['value'], 1)
        self.assertEqual(data['metrics'][3]['value'], 1)

    def test_student_dashboard_calculates_attendance_and_average(self):
        data = DashboardService.for_user(self.student, self.school)
        self.assertEqual(data['metrics'][1]['value'], '100.0%')
        self.assertEqual(data['metrics'][2]['value'], '90.00%')

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone

from core.middleware import AuditLogMiddleware, SessionTimeoutMiddleware
from core.models import AuditLog
from core.privacy import redact_mapping


class SecurityPolishTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Security School', slug='security', hostname='security.testserver')
        self.user = get_user_model().objects.create_user(username='secure', password='test-pass-123', role=CustomUser.Role.SCHOOL_ADMIN, school=self.school)
        self.factory = RequestFactory()

    def add_session(self, request):
        SessionMiddleware(lambda req: None).process_request(request)
        request.session.save()

    def test_privacy_redaction_masks_sensitive_values(self):
        redacted = redact_mapping({'email': 'parent@example.com', 'phone': '+254 700 000000', 'password': 'secret'})
        self.assertEqual(redacted['email'], 'p***t@example.com')
        self.assertEqual(redacted['phone'], '***REDACTED_PHONE***')
        self.assertEqual(redacted['password'], '***REDACTED***')

    def test_audit_log_middleware_records_write_request(self):
        request = self.factory.post('/dashboard/', {'password': 'secret', 'note': 'Call +254700000000'}, HTTP_HOST='testserver')
        self.add_session(request)
        request.user = self.user
        request.school = self.school
        request.resolver_match = type('ResolverMatch', (), {'view_name': 'dashboard'})()
        response = AuditLogMiddleware(lambda req: type('Response', (), {'status_code': 200})())(request)
        self.assertEqual(response.status_code, 200)
        log = AuditLog.objects.get()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.metadata['password'], '***REDACTED***')
        self.assertEqual(log.metadata['note'], 'Call ***REDACTED_PHONE***')

    @override_settings(SESSION_TIMEOUT_SECONDS=1)
    def test_session_timeout_logs_out_idle_user(self):
        request = self.factory.get('/dashboard/', HTTP_HOST='testserver')
        self.add_session(request)
        request.user = self.user
        request.session['last_activity_at'] = timezone.now().timestamp() - 10
        response = SessionTimeoutMiddleware(lambda req: None)(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
