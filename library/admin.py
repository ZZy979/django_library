from django.contrib import admin

from .models import Book, BorrowRecord

admin.site.register(Book)
admin.site.register(BorrowRecord)
