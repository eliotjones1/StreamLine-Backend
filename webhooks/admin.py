from django.contrib import admin
from .models import *
# Register your models here.
admin.register(UserStripeCustomer)
admin.register(UserPaymentInfo)
admin.register(UserStripePayment)
