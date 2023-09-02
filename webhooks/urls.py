from django.urls import path
from .views import *

urlpatterns = [
    path('stripe/', recieveStripeWebhook, name='stripe-webhook'),
    path('user-payments/', getPaymentsMade.as_view(), name='user-payments'),
]
