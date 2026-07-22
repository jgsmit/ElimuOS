from django.contrib import admin

from .models import Choice, ContinuousAssessment, Exam, ExamType, GradeBand, GradingSystem, Question, ReportCard, Result


class GradeBandInline(admin.TabularInline):
    model = GradeBand
    extra = 1


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'weight')
    list_filter = ('school',)
    search_fields = ('name', 'school__name')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_type', 'school_class', 'subject', 'session', 'total_marks', 'effective_weight')
    list_filter = ('session', 'school_class', 'subject', 'exam_type')
    search_fields = ('title', 'subject__name', 'school_class__name')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'order', 'marks')
    list_filter = ('exam__session', 'exam__school_class', 'exam__subject')
    search_fields = ('text', 'exam__title')
    inlines = [ChoiceInline]


@admin.register(GradingSystem)
class GradingSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'is_default')
    list_filter = ('school', 'is_default')
    search_fields = ('name', 'school__name')
    inlines = [GradeBandInline]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('exam', 'enrollment', 'marks_obtained', 'percentage', 'grade', 'points')
    list_filter = ('exam__session', 'exam__school_class', 'exam__subject', 'grade')
    search_fields = ('exam__title', 'enrollment__student__username')
    readonly_fields = ('percentage', 'grade', 'points', 'remark', 'recorded_at')


@admin.register(ContinuousAssessment)
class ContinuousAssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'enrollment', 'subject', 'session', 'marks_obtained', 'total_marks', 'weight')
    list_filter = ('session', 'subject')
    search_fields = ('title', 'enrollment__student__username', 'subject__name')


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'session', 'overall_percentage', 'overall_grade', 'generated_at')
    list_filter = ('session', 'overall_grade')
    search_fields = ('enrollment__student__username',)
    readonly_fields = ('subject_results', 'overall_percentage', 'overall_grade', 'overall_remark', 'generated_at')
