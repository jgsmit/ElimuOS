import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
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
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160)),
                ('biography', models.TextField(blank=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authors', to='schools.school')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='BookCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_categories', to='schools.school')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160)),
                ('website', models.URLField(blank=True)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publishers', to='schools.school')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('isbn', models.CharField(blank=True, max_length=32)),
                ('edition', models.CharField(blank=True, max_length=80)),
                ('publication_year', models.PositiveIntegerField(blank=True, null=True)),
                ('total_copies', models.PositiveIntegerField(default=1)),
                ('shelf_location', models.CharField(blank=True, max_length=80)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('authors', models.ManyToManyField(blank=True, related_name='books', to='library.author')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='books', to='library.bookcategory')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='library.publisher')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='books', to='schools.school')),
            ],
            options={'ordering': ['title']},
        ),
        migrations.CreateModel(
            name='BookBorrowing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrowed_at', models.DateField(default=django.utils.timezone.localdate)),
                ('due_date', models.DateField()),
                ('returned_at', models.DateField(blank=True, null=True)),
                ('fine_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='borrowings', to='library.book')),
                ('borrower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_borrowings', to=settings.AUTH_USER_MODEL)),
                ('issued_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issued_book_borrowings', to=settings.AUTH_USER_MODEL)),
                ('received_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_book_returns', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-borrowed_at', 'book__title']},
        ),
        migrations.AddConstraint(model_name='author', constraint=models.UniqueConstraint(fields=('school', 'name'), name='unique_author_per_school')),
        migrations.AddConstraint(model_name='bookcategory', constraint=models.UniqueConstraint(fields=('school', 'name'), name='unique_book_category_per_school')),
        migrations.AddConstraint(model_name='publisher', constraint=models.UniqueConstraint(fields=('school', 'name'), name='unique_publisher_per_school')),
        migrations.AddConstraint(model_name='book', constraint=models.UniqueConstraint(condition=~Q(('isbn', '')), fields=('school', 'isbn'), name='unique_book_isbn_per_school')),
        migrations.AddConstraint(model_name='bookborrowing', constraint=models.UniqueConstraint(condition=Q(('returned_at__isnull', True)), fields=('book', 'borrower'), name='unique_active_borrowing_per_book_borrower')),
    ]
