from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


PERCENT = Decimal('100.00')


def quantize(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class ExamType(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='exam_types')
    name = models.CharField(max_length=120)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'))

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['school', 'name'], name='unique_exam_type_per_school')]

    def clean(self):
        if self.weight <= 0 or self.weight > 100:
            raise ValidationError({'weight': 'Exam type weight must be between 0 and 100.'})

    def __str__(self):
        return f'{self.school} - {self.name}'


class Exam(models.Model):
    exam_type = models.ForeignKey(ExamType, on_delete=models.PROTECT, related_name='exams')
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.PROTECT, related_name='exams')
    school_class = models.ForeignKey('academics.SchoolClass', on_delete=models.PROTECT, related_name='exams')
    subject = models.ForeignKey('academics.Subject', on_delete=models.PROTECT, related_name='exams')
    title = models.CharField(max_length=160)
    exam_date = models.DateField(default=timezone.localdate)
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('100.00'))
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_exams')

    class Meta:
        ordering = ['-exam_date', 'title']
        constraints = [models.UniqueConstraint(fields=['session', 'school_class', 'subject', 'exam_type', 'title'], name='unique_exam_per_class_subject_type')]

    @property
    def effective_weight(self):
        return self.weight if self.weight is not None else self.exam_type.weight

    def clean(self):
        school_id = self.session.school_id
        if self.school_class.school_id != school_id or self.subject.school_id != school_id or self.exam_type.school_id != school_id:
            raise ValidationError('Exam type, session, class, and subject must belong to the same school.')
        if self.total_marks <= 0:
            raise ValidationError({'total_marks': 'Total marks must be greater than zero.'})
        if self.weight is not None and (self.weight <= 0 or self.weight > 100):
            raise ValidationError({'weight': 'Exam weight must be between 0 and 100.'})

    def __str__(self):
        return f'{self.title} - {self.school_class} - {self.subject}'


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('1.00'))
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
        constraints = [models.UniqueConstraint(fields=['exam', 'order'], name='unique_question_order_per_exam')]

    def clean(self):
        if self.marks <= 0:
            raise ValidationError({'marks': 'Question marks must be greater than zero.'})

    def __str__(self):
        return f'Q{self.order}: {self.exam}'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text


class GradingSystem(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='grading_systems')
    name = models.CharField(max_length=120)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['school', 'name'], name='unique_grading_system_per_school'),
            models.UniqueConstraint(fields=['school'], condition=Q(is_default=True), name='one_default_grading_system_per_school'),
        ]

    def grade_for(self, percentage):
        return self.bands.filter(min_score__lte=percentage, max_score__gte=percentage).order_by('-min_score').first()

    def __str__(self):
        return f'{self.school} - {self.name}'


class GradeBand(models.Model):
    grading_system = models.ForeignKey(GradingSystem, on_delete=models.CASCADE, related_name='bands')
    grade = models.CharField(max_length=8)
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    points = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    remark = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['-min_score']
        constraints = [models.UniqueConstraint(fields=['grading_system', 'grade'], name='unique_grade_per_system')]

    def clean(self):
        if self.min_score < 0 or self.max_score > 100 or self.min_score > self.max_score:
            raise ValidationError('Grade band range must be within 0-100 and min cannot exceed max.')
        overlap = GradeBand.objects.filter(
            grading_system=self.grading_system,
            min_score__lte=self.max_score,
            max_score__gte=self.min_score,
        )
        if self.pk:
            overlap = overlap.exclude(pk=self.pk)
        if overlap.exists():
            raise ValidationError('Grade band overlaps with an existing band.')

    def __str__(self):
        return f'{self.grade} ({self.min_score}-{self.max_score})'


class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    enrollment = models.ForeignKey('academics.StudentEnrollment', on_delete=models.CASCADE, related_name='exam_results')
    marks_obtained = models.DecimalField(max_digits=7, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, editable=False, default=Decimal('0.00'))
    grade = models.CharField(max_length=8, blank=True)
    points = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    remark = models.CharField(max_length=120, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_results')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['exam', 'enrollment__roll_number']
        constraints = [models.UniqueConstraint(fields=['exam', 'enrollment'], name='unique_result_per_exam_enrollment')]

    def clean(self):
        if self.marks_obtained < 0 or self.marks_obtained > self.exam.total_marks:
            raise ValidationError({'marks_obtained': 'Marks must be between 0 and exam total marks.'})
        if self.enrollment.school_class_id != self.exam.school_class_id or self.enrollment.session_id != self.exam.session_id:
            raise ValidationError('Enrollment must match the exam class and academic session.')

    def calculate_grade(self):
        self.percentage = quantize((self.marks_obtained / self.exam.total_marks) * PERCENT)
        grading_system = GradingSystem.objects.filter(school=self.exam.session.school, is_default=True).first()
        band = grading_system.grade_for(self.percentage) if grading_system else None
        if band:
            self.grade = band.grade
            self.points = band.points
            self.remark = band.remark

    def save(self, *args, **kwargs):
        self.full_clean()
        self.calculate_grade()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.enrollment} - {self.exam}: {self.marks_obtained}'


class ContinuousAssessment(models.Model):
    enrollment = models.ForeignKey('academics.StudentEnrollment', on_delete=models.CASCADE, related_name='continuous_assessments')
    subject = models.ForeignKey('academics.Subject', on_delete=models.PROTECT, related_name='continuous_assessments')
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.PROTECT, related_name='continuous_assessments')
    title = models.CharField(max_length=160)
    marks_obtained = models.DecimalField(max_digits=7, decimal_places=2)
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('100.00'))
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    assessment_date = models.DateField(default=timezone.localdate)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_assessments')

    class Meta:
        ordering = ['subject__name', 'title']
        constraints = [models.UniqueConstraint(fields=['enrollment', 'subject', 'session', 'title'], name='unique_ca_per_student_subject_session')]

    @property
    def percentage(self):
        return quantize((self.marks_obtained / self.total_marks) * PERCENT)

    def clean(self):
        if self.total_marks <= 0:
            raise ValidationError({'total_marks': 'Total marks must be greater than zero.'})
        if self.marks_obtained < 0 or self.marks_obtained > self.total_marks:
            raise ValidationError({'marks_obtained': 'Marks must be between 0 and total marks.'})
        if self.weight < 0 or self.weight > 100:
            raise ValidationError({'weight': 'Assessment weight must be between 0 and 100.'})
        if self.enrollment.session_id != self.session_id or self.subject.school_id != self.session.school_id:
            raise ValidationError('Assessment must match the enrollment session and school.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.enrollment} - {self.subject} - {self.title}'


class ReportCard(models.Model):
    enrollment = models.ForeignKey('academics.StudentEnrollment', on_delete=models.CASCADE, related_name='report_cards')
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.CASCADE, related_name='report_cards')
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='generated_report_cards')
    subject_results = models.JSONField(default=dict)
    overall_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    overall_grade = models.CharField(max_length=8, blank=True)
    overall_remark = models.CharField(max_length=120, blank=True)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-generated_at']
        constraints = [models.UniqueConstraint(fields=['enrollment', 'session'], name='unique_report_card_per_enrollment_session')]

    @classmethod
    def generate_for_enrollment(cls, enrollment, generated_by=None):
        subject_rows = {}
        subjects = enrollment.school_class.class_subjects.select_related('subject')
        grading_system = GradingSystem.objects.filter(school=enrollment.school_class.school, is_default=True).first()

        for class_subject in subjects:
            subject = class_subject.subject
            weighted_score, total_weight = Decimal('0.00'), Decimal('0.00')
            for result in enrollment.exam_results.filter(exam__subject=subject, exam__session=enrollment.session).select_related('exam'):
                weight = Decimal(result.exam.effective_weight)
                weighted_score += Decimal(result.percentage) * weight
                total_weight += weight
            for assessment in enrollment.continuous_assessments.filter(subject=subject, session=enrollment.session):
                weight = Decimal(assessment.weight)
                weighted_score += assessment.percentage * weight
                total_weight += weight
            final_percentage = quantize(weighted_score / total_weight) if total_weight else Decimal('0.00')
            band = grading_system.grade_for(final_percentage) if grading_system else None
            subject_rows[str(subject.id)] = {
                'subject': subject.name,
                'code': subject.code,
                'percentage': str(final_percentage),
                'grade': band.grade if band else '',
                'remark': band.remark if band else '',
            }

        scored = [Decimal(row['percentage']) for row in subject_rows.values()]
        overall = quantize(sum(scored) / len(scored)) if scored else Decimal('0.00')
        overall_band = grading_system.grade_for(overall) if grading_system else None
        report, _ = cls.objects.update_or_create(
            enrollment=enrollment,
            session=enrollment.session,
            defaults={
                'generated_by': generated_by,
                'subject_results': subject_rows,
                'overall_percentage': overall,
                'overall_grade': overall_band.grade if overall_band else '',
                'overall_remark': overall_band.remark if overall_band else '',
            },
        )
        return report

    def __str__(self):
        return f'Report card for {self.enrollment}'
