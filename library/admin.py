from django.contrib import admin

from .models import Author, Book, BookBorrowing, BookCategory, Publisher


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'school')
    list_filter = ('school',)
    search_fields = ('name', 'description')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'school')
    list_filter = ('school',)
    search_fields = ('name', 'biography')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'website', 'contact_email')
    list_filter = ('school',)
    search_fields = ('name', 'website', 'contact_email')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'category', 'isbn', 'total_copies', 'borrowed_count', 'available_copies', 'shelf_location')
    list_filter = ('school', 'category', 'publisher')
    search_fields = ('title', 'isbn', 'authors__name')
    filter_horizontal = ('authors',)


@admin.register(BookBorrowing)
class BookBorrowingAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower', 'borrowed_at', 'due_date', 'returned_at', 'fine_amount')
    list_filter = ('book__school', 'borrowed_at', 'due_date', 'returned_at')
    search_fields = ('book__title', 'book__isbn', 'borrower__username')
    readonly_fields = ('fine_amount', 'created_at', 'updated_at')
