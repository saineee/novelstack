from django.db import models
from django.conf import settings
from books.models import Book


class UserBook(models.Model):
    STATUS_CHOICES = [
        ('reading', 'Reading'),
        ('finished', 'Finished'),
        ('dropped', 'Dropped'),
        ('hiatus', 'Hiatus'),
        ('to read', 'To read'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    current_chapter = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='to read')
    rating = models.IntegerField(null=True, blank=True)
    date_started = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)