from django.contrib.auth.models import User
from django.db import models
from django.db.models import ForeignKey
from django.utils import timezone


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

    def return_book(self):
        if self.return_date is not None:
            return
        self.return_date = timezone.now()
        self.book.quantity += 1
        self.book.save()
        self.save()

    def __str__(self):
        return f'{self.user.username} borrowed {self.book.title}'
