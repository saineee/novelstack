from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)


    def __str__(self):
        return self.name


class Book(models.Model):

    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('hiatus', 'Hiatus'),
        ('cancelled', 'Cancelled'),
        ('not_yet_released', 'Not Yet Released')
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    chapters = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    classification = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    anilist_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    anilist_cover_url = models.URLField(null=True, blank=True, max_length=500)

    def __str__(self):
        return self.title