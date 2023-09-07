from django.contrib import admin
from .models import CustomUser
from django.contrib.sessions.models import Session
from django.db import models



admin.site.register(CustomUser)
class SessionAdmin(models.Model):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']
admin.site.register(Session, SessionAdmin)
# Register your models here.
