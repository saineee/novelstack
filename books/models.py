from django.db import models

class Book(models.Model):

    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('hiatus', 'Hiatus')
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    chapters = models.IntegerField()
    release_date = models.DateField(null=True, blank=True)
    classification = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ongoing')
    wln_series_id = models.CharField(max_length=255, null=True, blank=True)