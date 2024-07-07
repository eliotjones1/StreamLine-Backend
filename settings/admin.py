from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserData)
admin.site.register(TOSChecked)
admin.site.register(UserSettings)
admin.site.register(StreamLineSubscription)
admin.site.register(ThirdPartySubscription)
admin.site.register(UserContactRequest)
