from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=80, unique=True)),
                ('hostname', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='SchoolBranding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, max_length=255)),
                ('motto', models.CharField(blank=True, max_length=255)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='school_logos/')),
                ('primary_color', models.CharField(default='#0d6efd', max_length=7)),
                ('secondary_color', models.CharField(default='#6c757d', max_length=7)),
                ('accent_color', models.CharField(default='#198754', max_length=7)),
                ('school', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='branding', to='schools.school')),
            ],
            options={'verbose_name_plural': 'school branding'},
        ),
    ]
