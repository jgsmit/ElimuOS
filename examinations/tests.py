from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import AcademicSession, ClassSubject, SchoolClass, StudentEnrollment, Subject
from schools.models import School
from users.models import CustomUser
from .models import ContinuousAssessment, Exam, ExamType, GradeBand, GradingSystem, ReportCard, Result


class ExaminationCoreTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Demo School', slug='demo', hostname='demo.testserver')
        self.session = AcademicSession.objects.create(
            school=self.school,
            name='2026',
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_active=True,
        )
        self.school_class = SchoolClass.objects.create(school=self.school, name='Grade 1', level=1, capacity=40)
        self.subject = Subject.objects.create(school=self.school, name='Mathematics', code='MATH')
        ClassSubject.objects.create(school_class=self.school_class, subject=self.subject)
        self.student = get_user_model().objects.create_user(username='student', password='test-pass-123', role=CustomUser.Role.STUDENT, school=self.school)
        self.enrollment = StudentEnrollment.objects.create(student=self.student, school_class=self.school_class, session=self.session)
        self.exam_type = ExamType.objects.create(school=self.school, name='Final Exam', weight=Decimal('70.00'))
        self.exam = Exam.objects.create(
            exam_type=self.exam_type,
            session=self.session,
            school_class=self.school_class,
            subject=self.subject,
            title='Term 1 Final',
            total_marks=Decimal('100.00'),
        )
        grading = GradingSystem.objects.create(school=self.school, name='Default', is_default=True)
        GradeBand.objects.create(grading_system=grading, grade='A', min_score=80, max_score=100, points=4, remark='Excellent')
        GradeBand.objects.create(grading_system=grading, grade='B', min_score=60, max_score=79.99, points=3, remark='Good')
        GradeBand.objects.create(grading_system=grading, grade='C', min_score=0, max_score=59.99, points=2, remark='Needs improvement')

    def test_result_auto_calculates_percentage_and_grade(self):
        result = Result.objects.create(exam=self.exam, enrollment=self.enrollment, marks_obtained=Decimal('85.00'))
        self.assertEqual(result.percentage, Decimal('85.00'))
        self.assertEqual(result.grade, 'A')
        self.assertEqual(result.remark, 'Excellent')

    def test_result_rejects_marks_above_total(self):
        with self.assertRaises(ValidationError):
            Result.objects.create(exam=self.exam, enrollment=self.enrollment, marks_obtained=Decimal('101.00'))

    def test_continuous_assessment_validates_marks_and_weight(self):
        assessment = ContinuousAssessment.objects.create(
            enrollment=self.enrollment,
            subject=self.subject,
            session=self.session,
            title='Project',
            marks_obtained=Decimal('18.00'),
            total_marks=Decimal('20.00'),
            weight=Decimal('30.00'),
        )
        self.assertEqual(assessment.percentage, Decimal('90.00'))

    def test_report_card_generates_weighted_grade(self):
        Result.objects.create(exam=self.exam, enrollment=self.enrollment, marks_obtained=Decimal('80.00'))
        ContinuousAssessment.objects.create(
            enrollment=self.enrollment,
            subject=self.subject,
            session=self.session,
            title='Project',
            marks_obtained=Decimal('90.00'),
            total_marks=Decimal('100.00'),
            weight=Decimal('30.00'),
        )
        report = ReportCard.generate_for_enrollment(self.enrollment)
        self.assertEqual(report.overall_percentage, Decimal('83.00'))
        self.assertEqual(report.overall_grade, 'A')
