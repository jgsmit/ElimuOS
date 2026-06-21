import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('schools', '0001_initial'),
        ('users', '0002_customuser_school'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=False)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='academic_sessions', to='schools.school')),
            ],
            options={'ordering': ['-start_date']},
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('level', models.PositiveSmallIntegerField()),
                ('capacity', models.PositiveIntegerField(default=40)),
                ('class_teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_classes', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='schools.school')),
            ],
            options={'ordering': ['level', 'name']},
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('code', models.CharField(max_length=20)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='schools.school')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='ClassSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_subjects', to='academics.schoolclass')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_subjects', to='academics.subject')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teaching_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['school_class', 'subject__name']},
        ),
        migrations.CreateModel(
            name='StudentEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roll_number', models.PositiveIntegerField(blank=True, null=True)),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='enrollments', to='academics.schoolclass')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='enrollments', to='academics.academicsession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['school_class', 'roll_number']},
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=16)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('room', models.CharField(blank=True, max_length=80)),
                ('class_subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetable_entries', to='academics.classsubject')),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetable_entries', to='academics.schoolclass')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetable_entries', to='academics.academicsession')),
            ],
            options={'ordering': ['weekday', 'start_time']},
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.localdate)),
                ('status', models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('excused', 'Excused')], default='present', max_length=16)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='academics.studentenrollment')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_attendance', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='attendance_records', to='academics.subject')),
            ],
            options={'ordering': ['-date', 'enrollment__roll_number']},
        ),
        migrations.AddConstraint(model_name='academicsession', constraint=models.UniqueConstraint(condition=Q(('is_active', True)), fields=('school',), name='one_active_session_per_school')),
        migrations.AddConstraint(model_name='academicsession', constraint=models.UniqueConstraint(fields=('school', 'name'), name='unique_session_name_per_school')),
        migrations.AddConstraint(model_name='schoolclass', constraint=models.UniqueConstraint(fields=('school', 'name'), name='unique_class_name_per_school')),
        migrations.AddConstraint(model_name='subject', constraint=models.UniqueConstraint(fields=('school', 'code'), name='unique_subject_code_per_school')),
        migrations.AddConstraint(model_name='classsubject', constraint=models.UniqueConstraint(fields=('school_class', 'subject'), name='unique_subject_per_class')),
        migrations.AddConstraint(model_name='studentenrollment', constraint=models.UniqueConstraint(condition=Q(('is_active', True)), fields=('student', 'session'), name='unique_active_student_enrollment_per_session')),
        migrations.AddConstraint(model_name='studentenrollment', constraint=models.UniqueConstraint(fields=('school_class', 'session', 'roll_number'), name='unique_roll_number_per_class_session')),
        migrations.AddConstraint(model_name='timetable', constraint=models.UniqueConstraint(fields=('school_class', 'session', 'weekday', 'start_time'), name='unique_class_timetable_slot')),
        migrations.AddConstraint(model_name='attendance', constraint=models.UniqueConstraint(condition=Q(('subject__isnull', True)), fields=('enrollment', 'date'), name='unique_daily_attendance_without_subject')),
        migrations.AddConstraint(model_name='attendance', constraint=models.UniqueConstraint(condition=Q(('subject__isnull', False)), fields=('enrollment', 'subject', 'date'), name='unique_subject_attendance_per_day')),
    ]
