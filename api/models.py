from django.db import models

class StaffPick(models.Model):
    TV = 'tv'
    MOVIE = 'movie'

    CHOICES = (
        (TV, 'tv'),
        (MOVIE, 'movie'),
    )

    Staff_Member = models.CharField(max_length=100, primary_key=True)
    Media_ID = models.CharField(max_length=100)
    Media_Type = models.CharField(max_length=20, choices=CHOICES)
    