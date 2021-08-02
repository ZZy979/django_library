from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Reader, Librarian, Author, Book

admin.site.register(User, UserAdmin)
admin.site.register(Reader)
admin.site.register(Librarian)
admin.site.register(Author)
admin.site.register(Book)
