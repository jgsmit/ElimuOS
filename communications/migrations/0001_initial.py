import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('academics', '0001_initial'),
        ('schools', '0001_initial'),
        ('users', '0002_customuser_school'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_role', models.CharField(blank=True, choices=[('super_admin', 'Super Admin'), ('school_admin', 'School Admin'), ('teacher', 'Teacher'), ('student', 'Student'), ('parent', 'Parent'), ('counselor', 'Counselor'), ('librarian', 'Librarian'), ('hostel_staff', 'Hostel Staff')], max_length=32)),
                ('title', models.CharField(max_length=180)),
                ('body', models.TextField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('urgent', 'Urgent')], default='normal', max_length=16)),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_announcements', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='schools.school')),
                ('target_class', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='academics.schoolclass')),
            ],
            options={'ordering': ['-published_at']},
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_type', models.CharField(choices=[('direct', 'Direct Message'), ('class', 'Class Message'), ('group', 'Group Message')], max_length=16)),
                ('recipient_role', models.CharField(blank=True, choices=[('super_admin', 'Super Admin'), ('school_admin', 'School Admin'), ('teacher', 'Teacher'), ('student', 'Student'), ('parent', 'Parent'), ('counselor', 'Counselor'), ('librarian', 'Librarian'), ('hostel_staff', 'Hostel Staff')], max_length=32)),
                ('subject', models.CharField(max_length=180)),
                ('body', models.TextField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('urgent', 'Urgent')], default='normal', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient_class', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='class_messages', to='academics.schoolclass')),
                ('recipient_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_direct_messages', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='schools.school')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='AnnouncementReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivered_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('announcement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='communications.announcement')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcement_receipts', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-delivered_at']},
        ),
        migrations.CreateModel(
            name='MessageReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivered_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='communications.message')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_receipts', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-delivered_at']},
        ),
        migrations.AddConstraint(model_name='announcementreceipt', constraint=models.UniqueConstraint(fields=('announcement', 'recipient'), name='unique_announcement_receipt_per_recipient')),
        migrations.AddConstraint(model_name='messagereceipt', constraint=models.UniqueConstraint(fields=('message', 'recipient'), name='unique_message_receipt_per_recipient')),
    ]
