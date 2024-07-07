from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from .models import *

class UserStripePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStripePayment
        fields = '__all__'