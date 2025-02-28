from django.contrib import admin

from .models import Book, BorrowRecord, Category


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'quantity', 'category']
    list_filter = ['category']
    search_fields = ['title', 'author', 'isbn']


class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrow_date', 'return_date']
    list_filter = ['borrow_date', 'return_date']


admin.site.register(Category)
admin.site.register(Book, BookAdmin)
admin.site.register(BorrowRecord, BorrowRecordAdmin)
