from django.db import models


# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)
    publisher = models.CharField(max_length=255)
    publish_date = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.title
