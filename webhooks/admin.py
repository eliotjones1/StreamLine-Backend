from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserStripeCustomer)
admin.site.register(UserPaymentInfo)
admin.site.register(UserStripePayment)
