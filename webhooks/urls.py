from django.urls import path
from .views import *

urlpatterns = [
    path('stripe/', recieveStripeWebhook, name='stripe-webhook'),
]
