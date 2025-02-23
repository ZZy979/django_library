from django.contrib import admin

from .models import Book, BorrowRecord, Category

admin.site.register(Category)
admin.site.register(Book)
admin.site.register(BorrowRecord)
