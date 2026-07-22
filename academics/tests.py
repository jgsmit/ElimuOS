from datetime import date, time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from schools.models import School
from users.models import CustomUser
from .models import AcademicSession, Attendance, ClassSubject, SchoolClass, StudentEnrollment, Subject, Timetable


class AcademicCoreTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Demo School', slug='demo', hostname='demo.testserver')
        self.session = AcademicSession.objects.create(
            school=self.school,
            name='2026',
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_active=True,
        )
        self.school_class = SchoolClass.objects.create(school=self.school, name='Grade 1', level=1, capacity=2)
        self.subject = Subject.objects.create(school=self.school, name='Mathematics', code='MATH')
        self.class_subject = ClassSubject.objects.create(school_class=self.school_class, subject=self.subject)

    def create_student(self, username):
        return get_user_model().objects.create_user(
            username=username,
            password='test-pass-123',
            role=CustomUser.Role.STUDENT,
            school=self.school,
        )

    def test_auto_roll_number_generation(self):
        first = StudentEnrollment.objects.create(student=self.create_student('student1'), school_class=self.school_class, session=self.session)
        second = StudentEnrollment.objects.create(student=self.create_student('student2'), school_class=self.school_class, session=self.session)
        self.assertEqual(first.roll_number, 1)
        self.assertEqual(second.roll_number, 2)

    def test_class_capacity_is_enforced(self):
        StudentEnrollment.objects.create(student=self.create_student('student1'), school_class=self.school_class, session=self.session)
        StudentEnrollment.objects.create(student=self.create_student('student2'), school_class=self.school_class, session=self.session)
        with self.assertRaises(ValidationError):
            StudentEnrollment.objects.create(student=self.create_student('student3'), school_class=self.school_class, session=self.session)

    def test_timetable_validates_class_subject(self):
        Timetable.objects.create(
            school_class=self.school_class,
            class_subject=self.class_subject,
            session=self.session,
            weekday=Timetable.Weekday.MONDAY,
            start_time=time(8, 0),
            end_time=time(9, 0),
        )
        self.assertEqual(Timetable.objects.count(), 1)

    def test_attendance_record(self):
        enrollment = StudentEnrollment.objects.create(student=self.create_student('student1'), school_class=self.school_class, session=self.session)
        Attendance.objects.create(enrollment=enrollment, subject=self.subject, date=date(2026, 6, 21), status=Attendance.Status.PRESENT)
        self.assertEqual(Attendance.objects.count(), 1)
