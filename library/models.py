from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    def is_reader(self):
        return self.groups.filter(name=settings.READER_GROUP).exists()

    def is_librarian(self):
        return self.groups.filter(name=settings.LIBRARIAN_GROUP).exists()

    def can_login(self):
        return self.is_reader() or self.is_librarian()


class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return self.user.username


class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return self.user.username


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, default='')
    publish_date = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    isbn = models.CharField(max_length=13, default='')
    introduction = models.TextField(max_length=4096, default='')

    def __str__(self):
        return self.title
