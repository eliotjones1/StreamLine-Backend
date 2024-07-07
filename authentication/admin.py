from django.contrib import admin
from .models import CustomUser
from django.contrib.sessions.models import Session
from django.db import models



admin.site.register(CustomUser)
admin.site.register(Session)
# Register your models here.
