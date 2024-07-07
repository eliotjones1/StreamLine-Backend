import math

import pandas as pd
import sendgrid
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json
import stripe
from sendgrid import Mail

from .models import *
from datetime import datetime
from settings.models import StreamLineSubscription
from .serializers import *
from api.views import isSessionActive
from django.contrib.sessions.models import Session
import ast

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
    print(data)
    # Handle the event
    if event.type == "customer.created":
        if CustomUser.objects.filter(email= data["data"]["object"]["email"]).exists():
            user = CustomUser.objects.get(email = data["data"]["object"]["email"])
            if UserStripeCustomer.objects.filter(user = user).exists():
                temp = UserStripeCustomer.objects.get(user = user)
                temp.stripe_customer_id = data["data"]["object"]["id"]
                temp.save()
                return Response(status=status.HTTP_200_OK)
        user = CustomUser.objects.get(email = data["data"]["object"]["email"])
        new_customer = UserStripeCustomer(user = user, stripe_customer_id = data["data"]["object"]["id"])
        new_customer.save()
        return Response(status=status.HTTP_200_OK)
    elif event.type == "payment_method.attached":
        user = CustomUser.objects.get(email = data["data"]["object"]["billing_details"]["email"])
        customer = UserStripeCustomer.objects.get(user = user, stripe_customer_id = data["data"]["object"]["customer"])
        payment_info = UserPaymentInfo(user = user, stripe_customer_id = customer, stripe_payment_info = data["data"]["object"]["card"])
        payment_info.save()
        return Response(status=status.HTTP_200_OK)
    elif event.type == "customer.subscription.created":
        ## Create new subscription object
    
        customer = UserStripeCustomer.objects.get(stripe_customer_id = data["data"]["object"]["customer"])
        user = CustomUser.objects.get(email = customer.user.email)
        new_subscription = UserStripePayment(user = user, stripe_customer_id = customer, date_of_payment = datetime.now().date(), payment_amount = data["data"]["object"]["plan"]["amount"] / 100, transaction = "StreamLine", transaction_status = data["data"]["object"]["status"])
        new_subscription.save()

        if data["data"]["object"]["items"]["data"][0]["plan"]["id"] == "price_1NPdaQLPNbsO0xpZlJYcZdjo":
            sl_sub = StreamLineSubscription.objects.get(user = user)
            sl_sub.Basic = False
            sl_sub.Basic_Expiration = None
            sl_sub.Premium = True
            sl_sub.Premium_Expiration = datetime.fromtimestamp(data["data"]["object"]["current_period_end"])
            sl_sub.save()
        else:
            sl_sub = StreamLineSubscription.objects.get(user = user)
            sl_sub.Basic = True
            sl_sub.Basic_Expiration = datetime.fromtimestamp(data["data"]["object"]["current_period_end"])
            sl_sub.Premium = False
            sl_sub.Premium_Expiration = None
            sl_sub.save()

        return Response(status=status.HTTP_200_OK)
    elif event.type == "customer.subscription.updated":
        print(data["data"]["object"]["customer"])
        customer = UserStripeCustomer.objects.get(stripe_customer_id = data["data"]["object"]["customer"])
        user = CustomUser.objects.get(email = customer.user.email)
        subscription = UserStripePayment.objects.get(user = user, stripe_customer_id = customer)
        subscription.transaction_status = data["data"]["object"]["status"] 
        subscription.save()
        return Response(status=status.HTTP_200_OK)
    elif event.type == "customer.subscription.deleted":
        customer = UserStripeCustomer.objects.get(stripe_customer_id = data["data"]["object"]["customer"])
        user = CustomUser.objects.get(email = customer.user.email)
        customer.delete()
        sl_sub = StreamLineSubscription.objects.get(user = user)
        sl_sub.Basic = False
        sl_sub.Basic_Expiration = None
        sl_sub.Premium = False
        sl_sub.Premium_Expiration = None
        sl_sub.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

class getPaymentsMade(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        # print(sessionid)
        # Check if session is active
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        # expects user_id at 0, subscription info (name, date, recurring) at 1
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user = CustomUser.objects.get(email=user_email)
        payments = UserStripePayment.objects.filter(user = user).values_list()
        payment_info = UserPaymentInfo.objects.get(user = user)
        card = ast.literal_eval(payment_info.stripe_payment_info) 
        output = []
        df = pd.read_csv('api/random/serviceImages.csv')
        for payment in payments:
            print(payment)
            output.append({
                "img": df.loc[df['service_name'] == payment[5]]['logo_path'].values[0] if payment[5] != "StreamLine" else "",
                "name": payment[5],
                "amount": payment[4],
                "date": payment[3],
                "status": payment[6],
                "account": card["brand"],
                "accountNumber": card["last4"],
                "expiry": str(card["exp_month"]) + "/" + str(card["exp_year"]),
            })
        return_dict = {'payments': output, "numPages": math.ceil(len(payments) / 6)}
        return Response(return_dict, status=status.HTTP_200_OK)

