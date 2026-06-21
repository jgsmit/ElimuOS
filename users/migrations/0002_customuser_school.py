from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('schools', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='school',
            field=models.ForeignKey(blank=True, help_text='Tenant school this user belongs to. Super admins may be global.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='schools.school'),
        ),
    ]
