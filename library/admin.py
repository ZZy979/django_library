from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Reader, Librarian, Tag, Book


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher')
    list_filter = ['tag']
    search_fields = ['title']


admin.site.register(User, UserAdmin)
admin.site.register(Reader)
admin.site.register(Librarian)
admin.site.register(Tag)
admin.site.register(Book, BookAdmin)
