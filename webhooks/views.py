from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json
import stripe
from .models import *
from datetime import datetime
from settings.models import StreamLineSubscription
stripe.api_key = "sk_test_51NPcYzLPNbsO0xpZ3ypmarjukmXpUaySegVecBCiZEcfbiUrBxeuXBQU8QiafXpARoIUKdU2uqzdifzly9DlWedt00aO6ZevFh"

# Create your views here.
@csrf_exempt
@api_view(['POST'])
def recieveStripeWebhook(request):
    payload = request.body
    event = None
    try:
        event = stripe.Event.construct_from(
        json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    data = json.loads(payload)
    # Handle the event
    if event.type == "customer.created":
        user = CustomUser.objects.get(user_email = data["data"]["object"]["email"])
        new_customer = UserStripeCustomer(user = user, stripe_customer_id = data["data"]["object"]["id"])
        new_customer.save()
        return Response(status=status.HTTP_200_OK)
    elif event.type == "payment_method.attached":
        user = CustomUser.objects.get(user_email = data["data"]["object"]["billing_details"]["email"])
        customer = UserStripeCustomer.objects.get(user = user, stripe_customer_id = data["data"]["object"]["customer"])
        payment_info = UserPaymentInfo(user = user, stripe_customer_id = customer, stripe_payment_info = data["data"]["card"])
        payment_info.save()
        return Response(status=status.HTTP_200_OK)
    elif event.type == "customer.subscription.created":
        ## Create new subscription object
    
        customer = UserStripeCustomer.objects.get(stripe_customer_id = data["data"]["object"]["customer"])
        user = CustomUser.objects.get(user_email = customer.user.user_email)
        new_subscription = UserStripePayment(user = user, stripe_customer_id = customer, date_of_payment = datetime.fromtimestamp(data["data"]["object"]["created"]), payment_amount = data["data"]["object"]["plan"]["amount"] / 10, transaction = "StreamLine", transaction_status = data["data"]["object"]["status"])
        new_subscription.save()

        if data["object"]["items"]["data"][0]["plan"]["id"] == "price_1NPdaQLPNbsO0xpZlJYcZdjo":
            sl_sub = StreamLineSubscription.objects.get(user = user)
            sl_sub.Basic = False
            sl_sub.Basic_Expiration = None
            sl_sub.Premium = True
            sl_sub.Premium_Expiration = datetime.fromtimestamp(data["data"]["object"]["current_period_end"])
        else:
            sl_sub = StreamLineSubscription.objects.get(user = user)
            sl_sub.Basic = True
            sl_sub.Basic_Expiration = datetime.fromtimestamp(data["data"]["object"]["current_period_end"])
            sl_sub.Premium = False
            sl_sub.Premium_Expiration = None
        return Response(status=status.HTTP_200_OK)
    elif event.type == "customer.subscription.updated":
        customer = UserStripeCustomer.objects.get(stripe_customer_id = data["data"]["object"]["customer"])
        user = CustomUser.objects.get(user_email = customer.user.user_email)
        subscription = UserStripePayment.objects.get(user = user, stripe_customer_id = customer)
        subscription.transaction_status = data["data"]["object"]["status"] 
        subscription.save()
        return Response(status=status.HTTP_200_OK)
    elif event.type == "customer.subscription.deleted":
        customer = UserStripeCustomer.objects.get(stripe_customer_id = data["data"]["object"]["customer"])
        user = CustomUser.objects.get(user_email = customer.user.user_email)
        subscription = UserStripePayment.objects.get(user = user, stripe_customer_id = customer)
        subscription.delete()
        customer.delete()
        return Response(status=status.HTTP_200_OK)


