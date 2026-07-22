import django.db.models.deletion
import django.utils.timezone
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
            name='Hostel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hostels', to='schools.school')),
                ('warden', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_hostels', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.CharField(max_length=40)),
                ('floor', models.CharField(blank=True, max_length=40)),
                ('capacity', models.PositiveIntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='hostels.hostel')),
            ],
            options={'ordering': ['hostel__name', 'room_number']},
        ),
        migrations.CreateModel(
            name='HostelExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('expense_date', models.DateField(default=django.utils.timezone.localdate)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='hostels.hostel')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_hostel_expenses', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-expense_date', 'category']},
        ),
        migrations.CreateModel(
            name='RoomAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allocated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('released_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
                ('allocated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_room_allocations', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='allocations', to='hostels.room')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='room_allocations', to='academics.academicsession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_allocations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['room', 'student__username']},
        ),
        migrations.CreateModel(
            name='VisitorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_name', models.CharField(max_length=160)),
                ('visitor_phone', models.CharField(blank=True, max_length=32)),
                ('purpose', models.CharField(max_length=255)),
                ('checked_in_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('checked_out_at', models.DateTimeField(blank=True, null=True)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitor_logs', to='hostels.hostel')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_hostel_visitors', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hostel_visitors', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-checked_in_at']},
        ),
        migrations.AddConstraint(model_name='hostel', constraint=models.UniqueConstraint(fields=('school', 'name'), name='unique_hostel_name_per_school')),
        migrations.AddConstraint(model_name='room', constraint=models.UniqueConstraint(fields=('hostel', 'room_number'), name='unique_room_number_per_hostel')),
        migrations.AddConstraint(model_name='roomallocation', constraint=models.UniqueConstraint(condition=Q(('is_active', True)), fields=('student', 'session'), name='unique_active_room_allocation_per_student_session')),
    ]
