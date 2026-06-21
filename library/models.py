from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class BookCategory(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='book_categories')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['school', 'name'], name='unique_book_category_per_school')]

    def __str__(self):
        return self.name


class Author(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='authors')
    name = models.CharField(max_length=160)
    biography = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['school', 'name'], name='unique_author_per_school')]

    def __str__(self):
        return self.name


class Publisher(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='publishers')
    name = models.CharField(max_length=160)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['school', 'name'], name='unique_publisher_per_school')]

    def __str__(self):
        return self.name


class Book(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(BookCategory, on_delete=models.PROTECT, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, related_name='books', blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books', blank=True)
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=32, blank=True)
    edition = models.CharField(max_length=80, blank=True)
    publication_year = models.PositiveIntegerField(blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        constraints = [models.UniqueConstraint(fields=['school', 'isbn'], condition=~models.Q(isbn=''), name='unique_book_isbn_per_school')]

    @property
    def borrowed_count(self):
        return self.borrowings.filter(returned_at__isnull=True).count()

    @property
    def available_copies(self):
        return max(self.total_copies - self.borrowed_count, 0)

    @property
    def is_available(self):
        return self.available_copies > 0

    def clean(self):
        if self.category.school_id != self.school_id:
            raise ValidationError({'category': 'Category must belong to the same school as the book.'})
        if self.publisher and self.publisher.school_id != self.school_id:
            raise ValidationError({'publisher': 'Publisher must belong to the same school as the book.'})
        if self.total_copies < 1:
            raise ValidationError({'total_copies': 'At least one copy is required.'})
        if self.pk and self.total_copies < self.borrowed_count:
            raise ValidationError({'total_copies': 'Total copies cannot be less than currently borrowed copies.'})

    def __str__(self):
        return self.title


class BookBorrowing(models.Model):
    FINE_PER_DAY = Decimal('10.00')

    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='borrowings')
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_borrowings')
    borrowed_at = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    returned_at = models.DateField(blank=True, null=True)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='issued_book_borrowings', blank=True, null=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='received_book_returns', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-borrowed_at', 'book__title']
        constraints = [models.UniqueConstraint(fields=['book', 'borrower'], condition=models.Q(returned_at__isnull=True), name='unique_active_borrowing_per_book_borrower')]

    @property
    def is_returned(self):
        return self.returned_at is not None

    @property
    def days_overdue(self):
        reference_date = self.returned_at or timezone.localdate()
        if reference_date <= self.due_date:
            return 0
        return (reference_date - self.due_date).days

    def calculate_fine(self):
        return self.FINE_PER_DAY * self.days_overdue

    def mark_returned(self, received_by=None, returned_at=None):
        self.returned_at = returned_at or timezone.localdate()
        self.received_by = received_by
        self.fine_amount = self.calculate_fine()
        self.save(update_fields=['returned_at', 'received_by', 'fine_amount', 'updated_at'])

    def clean(self):
        if self.due_date < self.borrowed_at:
            raise ValidationError({'due_date': 'Due date cannot be before borrow date.'})
        if self.returned_at and self.returned_at < self.borrowed_at:
            raise ValidationError({'returned_at': 'Return date cannot be before borrow date.'})
        if self.borrower.school_id and self.borrower.school_id != self.book.school_id:
            raise ValidationError({'borrower': 'Borrower must belong to the same school as the book.'})
        if not self.pk and not self.book.is_available:
            raise ValidationError({'book': 'No copies are currently available for borrowing.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        self.fine_amount = self.calculate_fine()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.book} borrowed by {self.borrower}'
