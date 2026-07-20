from django.core.validators import MinValueValidator, MaxValueValidator

from django.db.models.query_utils import Q
from django.db.models.expressions import F
from django.db import models
from django.conf import settings
from books.models import Book


class UserBook(models.Model):
    STATUS_CHOICES = [
        ('reading', 'Reading'),
        ('finished', 'Finished'),
        ('dropped', 'Dropped'),
        ('hiatus', 'Hiatus'),
        ('to_read', 'To Read'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    current_chapter = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='to_read')
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    date_started = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'book'], name='unique_user_book'),
            models.CheckConstraint(
                condition=Q(date_ended__gte=F('date_started')),
                name = "date_ended_after_date_started")]

    @property
    def progress_percent(self):
        if self.book.chapters and self.current_chapter:
            return int(self.current_chapter / self.book.chapters * 100)
        return 0