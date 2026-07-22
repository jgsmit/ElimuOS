import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('academics', '0001_initial'),
        ('schools', '0001_initial'),
        ('users', '0002_customuser_school'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('weight', models.DecimalField(decimal_places=2, default=Decimal('100.00'), max_digits=5)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_types', to='schools.school')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='GradingSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('is_default', models.BooleanField(default=False)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grading_systems', to='schools.school')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('exam_date', models.DateField(default=django.utils.timezone.localdate)),
                ('total_marks', models.DecimalField(decimal_places=2, default=Decimal('100.00'), max_digits=7)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_exams', to=settings.AUTH_USER_MODEL)),
                ('exam_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='exams', to='examinations.examtype')),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='exams', to='academics.schoolclass')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='exams', to='academics.academicsession')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='exams', to='academics.subject')),
            ],
            options={'ordering': ['-exam_date', 'title']},
        ),
        migrations.CreateModel(
            name='ContinuousAssessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('marks_obtained', models.DecimalField(decimal_places=2, max_digits=7)),
                ('total_marks', models.DecimalField(decimal_places=2, default=Decimal('100.00'), max_digits=7)),
                ('weight', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('assessment_date', models.DateField(default=django.utils.timezone.localdate)),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='continuous_assessments', to='academics.studentenrollment')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_assessments', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='continuous_assessments', to='academics.academicsession')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='continuous_assessments', to='academics.subject')),
            ],
            options={'ordering': ['subject__name', 'title']},
        ),
        migrations.CreateModel(
            name='GradeBand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(max_length=8)),
                ('min_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('max_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('points', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=4)),
                ('remark', models.CharField(blank=True, max_length=120)),
                ('grading_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bands', to='examinations.gradingsystem')),
            ],
            options={'ordering': ['-min_score']},
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('marks', models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=6)),
                ('order', models.PositiveIntegerField(default=1)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='examinations.exam')),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='ReportCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_results', models.JSONField(default=dict)),
                ('overall_percentage', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('overall_grade', models.CharField(blank=True, max_length=8)),
                ('overall_remark', models.CharField(blank=True, max_length=120)),
                ('generated_at', models.DateTimeField(auto_now=True)),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_cards', to='academics.studentenrollment')),
                ('generated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_report_cards', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_cards', to='academics.academicsession')),
            ],
            options={'ordering': ['-generated_at']},
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks_obtained', models.DecimalField(decimal_places=2, max_digits=7)),
                ('percentage', models.DecimalField(decimal_places=2, default=Decimal('0.00'), editable=False, max_digits=5)),
                ('grade', models.CharField(blank=True, max_length=8)),
                ('points', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=4)),
                ('remark', models.CharField(blank=True, max_length=120)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_results', to='academics.studentenrollment')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='examinations.exam')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_results', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['exam', 'enrollment__roll_number']},
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='examinations.question')),
            ],
            options={'ordering': ['id']},
        ),
        migrations.AddConstraint(model_name='examtype', constraint=models.UniqueConstraint(fields=('school', 'name'), name='unique_exam_type_per_school')),
        migrations.AddConstraint(model_name='gradingsystem', constraint=models.UniqueConstraint(fields=('school', 'name'), name='unique_grading_system_per_school')),
        migrations.AddConstraint(model_name='gradingsystem', constraint=models.UniqueConstraint(condition=Q(('is_default', True)), fields=('school',), name='one_default_grading_system_per_school')),
        migrations.AddConstraint(model_name='exam', constraint=models.UniqueConstraint(fields=('session', 'school_class', 'subject', 'exam_type', 'title'), name='unique_exam_per_class_subject_type')),
        migrations.AddConstraint(model_name='continuousassessment', constraint=models.UniqueConstraint(fields=('enrollment', 'subject', 'session', 'title'), name='unique_ca_per_student_subject_session')),
        migrations.AddConstraint(model_name='gradeband', constraint=models.UniqueConstraint(fields=('grading_system', 'grade'), name='unique_grade_per_system')),
        migrations.AddConstraint(model_name='question', constraint=models.UniqueConstraint(fields=('exam', 'order'), name='unique_question_order_per_exam')),
        migrations.AddConstraint(model_name='reportcard', constraint=models.UniqueConstraint(fields=('enrollment', 'session'), name='unique_report_card_per_enrollment_session')),
        migrations.AddConstraint(model_name='result', constraint=models.UniqueConstraint(fields=('exam', 'enrollment'), name='unique_result_per_exam_enrollment')),
    ]
