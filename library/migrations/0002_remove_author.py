# Generated by Django 3.2.5 on 2021-09-03 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='introduction',
            field=models.TextField(default='', max_length=4096),
        ),
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(default='', max_length=13),
        ),
        migrations.AlterField(
            model_name='book',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='book',
            name='publisher',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.DeleteModel(
            name='Author',
        ),
    ]