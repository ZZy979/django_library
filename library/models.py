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


class Tag(models.Model):
    """图书标签"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, default='')
    publish_date = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    isbn = models.CharField(max_length=13, default='')
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)
    introduction = models.TextField(max_length=4096, default='')

    def __str__(self):
        return self.title


class Copy(models.Model):
    """馆藏图书副本"""

    class Status(models.TextChoices):
        IN_STOCK = 'in stock', '可借'
        ON_LOAN = 'on loan', '借出'

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.IN_STOCK)

    def __str__(self):
        return f'{self.id} - {self.book.title}'


class Borrow(models.Model):
    """借阅记录"""
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    copy = models.ForeignKey(Copy, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    lend_librarian = models.ForeignKey(
        Librarian, on_delete=models.SET_NULL, null=True, related_name='lend_set'
    )
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(blank=True, null=True)
    return_librarian = models.ForeignKey(
        Librarian, on_delete=models.SET_NULL, null=True, related_name='return_set'
    )

    def __str__(self):
        return f'{self.reader.user.get_full_name()} - {self.copy}'
