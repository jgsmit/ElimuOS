from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import AcademicSession, SchoolClass, StudentEnrollment
from schools.models import School
from users.models import CustomUser
from .models import Announcement, Message, Priority


class CommunicationCoreTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Demo School', slug='demo', hostname='demo.testserver')
        self.admin = get_user_model().objects.create_user(username='admin', password='test-pass-123', role=CustomUser.Role.SCHOOL_ADMIN, school=self.school)
        self.teacher = get_user_model().objects.create_user(username='teacher', password='test-pass-123', role=CustomUser.Role.TEACHER, school=self.school)
        self.student = get_user_model().objects.create_user(username='student', password='test-pass-123', role=CustomUser.Role.STUDENT, school=self.school)
        self.session = AcademicSession.objects.create(school=self.school, name='2026', start_date='2026-01-01', end_date='2026-12-31', is_active=True)
        self.school_class = SchoolClass.objects.create(school=self.school, name='Grade 1', level=1, capacity=40)
        StudentEnrollment.objects.create(student=self.student, school_class=self.school_class, session=self.session)

    def test_direct_message_creates_receipt_and_read_tracking(self):
        message = Message.objects.create(
            school=self.school,
            sender=self.admin,
            message_type=Message.MessageType.DIRECT,
            recipient_user=self.teacher,
            subject='Meeting',
            body='Please attend the meeting.',
        )
        receipts = message.create_receipts()
        self.assertEqual(len(receipts), 1)
        receipts[0].mark_read()
        self.assertTrue(receipts[0].is_read)

    def test_class_message_targets_active_students(self):
        message = Message.objects.create(
            school=self.school,
            sender=self.teacher,
            message_type=Message.MessageType.CLASS,
            recipient_class=self.school_class,
            subject='Homework',
            body='Complete chapter one.',
        )
        receipts = message.create_receipts()
        self.assertEqual([receipt.recipient for receipt in receipts], [self.student])

    def test_group_announcement_targets_role_and_priority(self):
        announcement = Announcement.objects.create(
            school=self.school,
            created_by=self.admin,
            target_role=CustomUser.Role.TEACHER,
            title='Urgent briefing',
            body='All teachers report to the staff room.',
            priority=Priority.URGENT,
        )
        receipts = announcement.create_receipts()
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0].recipient, self.teacher)
        self.assertEqual(announcement.priority, Priority.URGENT)

    def test_message_requires_matching_recipient_type(self):
        with self.assertRaises(ValidationError):
            Message.objects.create(
                school=self.school,
                sender=self.admin,
                message_type=Message.MessageType.DIRECT,
                subject='Invalid',
                body='Missing recipient.',
            )
