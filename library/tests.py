from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from schools.models import School
from users.models import CustomUser
from .models import Author, Book, BookBorrowing, BookCategory, Publisher


class LibraryCoreTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Demo School', slug='demo', hostname='demo.testserver')
        self.category = BookCategory.objects.create(school=self.school, name='Textbooks')
        self.author = Author.objects.create(school=self.school, name='Grace Author')
        self.publisher = Publisher.objects.create(school=self.school, name='Demo Publisher')
        self.book = Book.objects.create(
            school=self.school,
            category=self.category,
            publisher=self.publisher,
            title='Mathematics Basics',
            isbn='978000000001',
            total_copies=1,
        )
        self.book.authors.add(self.author)
        self.student = get_user_model().objects.create_user(username='student', password='test-pass-123', role=CustomUser.Role.STUDENT, school=self.school)

    def test_book_availability_changes_when_borrowed_and_returned(self):
        borrowing = BookBorrowing.objects.create(
            book=self.book,
            borrower=self.student,
            borrowed_at=date(2026, 6, 1),
            due_date=date(2026, 6, 10),
        )
        self.assertEqual(self.book.available_copies, 0)
        borrowing.mark_returned(returned_at=date(2026, 6, 10))
        self.assertEqual(self.book.available_copies, 1)

    def test_prevents_borrowing_when_no_copy_is_available(self):
        BookBorrowing.objects.create(book=self.book, borrower=self.student, borrowed_at=date(2026, 6, 1), due_date=date(2026, 6, 10))
        other_student = get_user_model().objects.create_user(username='other', password='test-pass-123', role=CustomUser.Role.STUDENT, school=self.school)
        with self.assertRaises(ValidationError):
            BookBorrowing.objects.create(book=self.book, borrower=other_student, borrowed_at=date(2026, 6, 2), due_date=date(2026, 6, 12))

    def test_fine_is_calculated_on_late_return(self):
        borrowing = BookBorrowing.objects.create(book=self.book, borrower=self.student, borrowed_at=date(2026, 6, 1), due_date=date(2026, 6, 10))
        borrowing.mark_returned(returned_at=date(2026, 6, 13))
        self.assertEqual(borrowing.fine_amount, Decimal('30.00'))
