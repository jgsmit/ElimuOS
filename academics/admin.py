from django.contrib import admin

from .models import AcademicSession, Attendance, ClassSubject, SchoolClass, StudentEnrollment, Subject, Timetable


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'start_date', 'end_date', 'is_active')
    list_filter = ('school', 'is_active')
    search_fields = ('name', 'school__name')


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'level', 'capacity', 'active_enrollment_count', 'available_capacity')
    list_filter = ('school', 'level')
    search_fields = ('name', 'school__name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'school')
    list_filter = ('school',)
    search_fields = ('code', 'name')


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'subject', 'teacher')
    list_filter = ('school_class__school', 'school_class')
    search_fields = ('school_class__name', 'subject__name', 'subject__code', 'teacher__username')


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'school_class', 'session', 'roll_number', 'is_active')
    list_filter = ('school_class__school', 'session', 'is_active')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'school_class__name')
    readonly_fields = ('roll_number', 'enrolled_at')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'class_subject', 'session', 'weekday', 'start_time', 'end_time', 'room')
    list_filter = ('school_class__school', 'session', 'weekday')
    search_fields = ('school_class__name', 'class_subject__subject__name', 'room')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'subject', 'date', 'status', 'recorded_by')
    list_filter = ('status', 'date', 'enrollment__school_class__school')
    search_fields = ('enrollment__student__username', 'subject__name', 'recorded_by__username')
