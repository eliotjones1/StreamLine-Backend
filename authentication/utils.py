from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model

def get_and_authenticate_user(email, password):
    user = authenticate(username=email, password=password)
    if user is None:
        raise serializers.ValidationError("Invalid username/password. Please try again!")
    return user

def create_user_account(email, password, first_name="",
                        last_name="", **extra_fields):
    User = get_user_model()
    user = User(
        email=email, first_name=first_name, last_name=last_name, **extra_fields
    )
    user.set_password(password)
    user.is_active = True
    user.save()
    return user
    # user = get_user_model().objects.create_user(
    #     email=email, password=password, first_name=first_name,
    #     last_name=last_name, **extra_fields)
    # return user



