import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ForeignKey
from django.utils import timezone


class User(AbstractUser):
    def is_admin(self):
        return self.groups.filter(name='Librarian').exists()


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=100, blank=True)
    pub_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    book = ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + datetime.timedelta(days=14)
        super().save(*args, **kwargs)

    def renew(self):
        if self.return_date is not None:
            return
        self.due_date += datetime.timedelta(days=14)
        self.save()

    def return_book(self):
        if self.return_date is not None:
            return
        self.return_date = timezone.now().date()
        self.book.quantity += 1
        self.book.save()
        self.save()

    def __str__(self):
        return f'{self.user.username} borrowed {self.book.title}'
