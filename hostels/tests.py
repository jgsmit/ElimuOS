from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from academics.models import AcademicSession
from schools.models import School
from users.models import CustomUser
from .models import Hostel, HostelExpense, Room, RoomAllocation, VisitorLog


class HostelCoreTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Demo School', slug='demo', hostname='demo.testserver')
        self.session = AcademicSession.objects.create(
            school=self.school,
            name='2026',
            start_date=timezone.localdate(),
            end_date=timezone.localdate().replace(year=timezone.localdate().year + 1),
            is_active=True,
        )
        self.hostel = Hostel.objects.create(school=self.school, name='Main Hostel')
        self.room = Room.objects.create(hostel=self.hostel, room_number='A1', capacity=1)
        self.student = get_user_model().objects.create_user(username='student', password='test-pass-123', role=CustomUser.Role.STUDENT, school=self.school)

    def test_room_allocation_tracks_occupancy(self):
        allocation = RoomAllocation.objects.create(student=self.student, room=self.room, session=self.session)
        self.assertEqual(self.room.occupancy, 1)
        self.assertEqual(self.room.available_spaces, 0)
        allocation.release()
        self.assertEqual(self.room.occupancy, 0)
        self.assertEqual(self.room.available_spaces, 1)

    def test_room_capacity_is_enforced(self):
        RoomAllocation.objects.create(student=self.student, room=self.room, session=self.session)
        other_student = get_user_model().objects.create_user(username='other', password='test-pass-123', role=CustomUser.Role.STUDENT, school=self.school)
        with self.assertRaises(ValidationError):
            RoomAllocation.objects.create(student=other_student, room=self.room, session=self.session)

    def test_one_active_room_allocation_per_student_session(self):
        second_room = Room.objects.create(hostel=self.hostel, room_number='A2', capacity=1)
        RoomAllocation.objects.create(student=self.student, room=self.room, session=self.session)
        with self.assertRaises(ValidationError):
            RoomAllocation.objects.create(student=self.student, room=second_room, session=self.session)

    def test_visitor_log_and_expense_validation(self):
        visitor = VisitorLog.objects.create(hostel=self.hostel, student=self.student, visitor_name='Parent One', purpose='Visit')
        self.assertEqual(visitor.hostel, self.hostel)
        expense = HostelExpense.objects.create(hostel=self.hostel, category='Repairs', amount=Decimal('1500.00'))
        self.assertEqual(expense.amount, Decimal('1500.00'))
        with self.assertRaises(ValidationError):
            HostelExpense.objects.create(hostel=self.hostel, category='Invalid', amount=Decimal('0.00'))
