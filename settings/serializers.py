from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from .models import *


class UserDataSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserData
    fields = '__all__'


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = '__all__'

class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamLineSubscription
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThirdPartySubscription
        fields = '__all__'

class UserContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContactRequest
        fields = '__all__'
