from django.db import models
from authentication.models import CustomUser

# Create your models here.
class MediaRatings(models.Model):
    media_id = models.IntegerField()
    user_id = models.JSONField(CustomUser)
    rating = models.FloatField()
    media_type = models.CharField(max_length=10)
    streaming_providers = models.JSONField(default = list)


class UserEmail(models.Model):
   email = models.EmailField(unique = True)
   def __str__(self):
      return self.email
