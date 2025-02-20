from django.contrib.auth.models import User
from django.db import models
from django.db.models import ForeignKey


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    book = ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} borrowed {self.book.title}'
