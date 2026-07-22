from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class AcademicSession(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='academic_sessions')
    name = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(fields=['school'], condition=Q(is_active=True), name='one_active_session_per_school'),
            models.UniqueConstraint(fields=['school', 'name'], name='unique_session_name_per_school'),
        ]

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'End date must be after start date.'})

    def __str__(self):
        return f'{self.school} - {self.name}'


class SchoolClass(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=80)
    level = models.PositiveSmallIntegerField()
    capacity = models.PositiveIntegerField(default=40)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='managed_classes',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['level', 'name']
        constraints = [models.UniqueConstraint(fields=['school', 'name'], name='unique_class_name_per_school')]

    @property
    def active_enrollment_count(self):
        return self.enrollments.filter(session__is_active=True, is_active=True).count()

    @property
    def available_capacity(self):
        return max(self.capacity - self.active_enrollment_count, 0)

    @property
    def is_full(self):
        return self.available_capacity == 0

    def __str__(self):
        return f'{self.school} - {self.name}'


class Subject(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20)

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['school', 'code'], name='unique_subject_code_per_school')]

    def __str__(self):
        return f'{self.code} - {self.name}'


class ClassSubject(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='teaching_assignments',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['school_class', 'subject__name']
        constraints = [models.UniqueConstraint(fields=['school_class', 'subject'], name='unique_subject_per_class')]

    def clean(self):
        if self.school_class.school_id != self.subject.school_id:
            raise ValidationError('Class and subject must belong to the same school.')

    def __str__(self):
        return f'{self.school_class} - {self.subject}'


class StudentEnrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='enrollments')
    session = models.ForeignKey(AcademicSession, on_delete=models.PROTECT, related_name='enrollments')
    roll_number = models.PositiveIntegerField(blank=True, null=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['school_class', 'roll_number']
        constraints = [
            models.UniqueConstraint(fields=['student', 'session'], condition=Q(is_active=True), name='unique_active_student_enrollment_per_session'),
            models.UniqueConstraint(fields=['school_class', 'session', 'roll_number'], name='unique_roll_number_per_class_session'),
        ]

    def clean(self):
        if self.student.role != self.student.Role.STUDENT:
            raise ValidationError({'student': 'Only users with the student role can be enrolled.'})
        if self.school_class.school_id != self.session.school_id:
            raise ValidationError('Class and academic session must belong to the same school.')
        if self.student.school_id and self.student.school_id != self.school_class.school_id:
            raise ValidationError({'student': 'Student must belong to the same school as the class.'})
        if self.is_active and self.school_class.is_full and not self.pk:
            raise ValidationError({'school_class': 'Class capacity has been reached.'})

    def save(self, *args, **kwargs):
        if self.roll_number is None:
            last_roll = StudentEnrollment.objects.filter(
                school_class=self.school_class,
                session=self.session,
            ).aggregate(models.Max('roll_number'))['roll_number__max'] or 0
            self.roll_number = last_roll + 1
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student} - {self.school_class} ({self.session})'


class Timetable(models.Model):
    class Weekday(models.TextChoices):
        MONDAY = 'monday', 'Monday'
        TUESDAY = 'tuesday', 'Tuesday'
        WEDNESDAY = 'wednesday', 'Wednesday'
        THURSDAY = 'thursday', 'Thursday'
        FRIDAY = 'friday', 'Friday'
        SATURDAY = 'saturday', 'Saturday'
        SUNDAY = 'sunday', 'Sunday'

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='timetable_entries')
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='timetable_entries')
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='timetable_entries')
    weekday = models.CharField(max_length=16, choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ['weekday', 'start_time']
        constraints = [
            models.UniqueConstraint(fields=['school_class', 'session', 'weekday', 'start_time'], name='unique_class_timetable_slot'),
        ]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'End time must be after start time.'})
        if self.class_subject.school_class_id != self.school_class_id:
            raise ValidationError('Class subject must belong to the timetable class.')
        if self.session.school_id != self.school_class.school_id:
            raise ValidationError('Session and class must belong to the same school.')

    def __str__(self):
        return f'{self.school_class} {self.weekday} {self.start_time}'


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'
        EXCUSED = 'excused', 'Excused'

    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='attendance_records', blank=True, null=True)
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PRESENT)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='recorded_attendance',
        blank=True,
        null=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'enrollment__roll_number']
        constraints = [
            models.UniqueConstraint(fields=['enrollment', 'date'], condition=Q(subject__isnull=True), name='unique_daily_attendance_without_subject'),
            models.UniqueConstraint(fields=['enrollment', 'subject', 'date'], condition=Q(subject__isnull=False), name='unique_subject_attendance_per_day'),
        ]

    def clean(self):
        if self.subject and self.subject.school_id != self.enrollment.school_class.school_id:
            raise ValidationError({'subject': 'Subject must belong to the enrolled school.'})

    def __str__(self):
        return f'{self.enrollment} - {self.date} - {self.status}'
