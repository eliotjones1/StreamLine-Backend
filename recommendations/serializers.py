from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from .models import MediaRatings

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaRatings
        fields = '__all__'