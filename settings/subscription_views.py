import requests
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from rest_framework import viewsets, status
from .models import *
from .serializers import UserSettingsSerializer, UserSubscriptionSerializer
from api.views import isSessionActive
from authentication.models import CustomUser
from authentication.serializers import AuthUserSerializer
from django.contrib.sessions.models import Session
from django.utils import timezone
import stripe
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, HtmlContent
from .functions import *
import json

@api_view(['POST'])
def BasicSubscription(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # Get user from session
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    payment_method = request.query_params.get('payment_method', None)
    
    user_exists = CustomUser.objects.get(email=user_email)
    if user_exists is None:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    subscription = UserSubscription.objects.get(user=user_exists)
    subscription.Basic = True
    # Set expiration to 1 month from now
    subscription.Basic_Expiration = timezone.now() + timezone.timedelta(days=30)
    subscription.Premium = False
    subscription.Premium_Expiration = None
    serializer = UserSubscriptionSerializer(subscription)

    # Stripe customer creation stuff
    if stripe.Customer.list(email=user_email).data:
        customer = stripe.Customer.list(email=user_email).data[0]
    else:
        customer = stripe.Customer.create(
            email=user_email,
            name=user_exists.first_name + " " + user_exists.last_name,
            description="Basic Subscription",
            payment_method=payment_method,
        )
    subscription.stripe_customer_id = customer['id']
    basic_id = "price_1NPcdBLPNbsO0xpZSX7Zrh0V"
    stripe.Subscription.create(
        customer=customer['id'],
        items=[
            {
                "price": basic_id,
            },
        ],
    )
    subscription.stripe_subscription_id = stripe.Subscription.list(
        customer=customer['id']).data[0]['id']
    subscription.save()

    # Send Signup Email
    template_id = "d-57f98ea68557417bbcb5b5a0ee77af46"
    message = Mail(
    from_email='ekj0512@gmail.com',
    to_emails=user_email,
    )
    message.template_id = template_id
    try:
        sg = sendgrid.SendGridAPIClient(api_key='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')  # Replace with your SendGrid API key
        response = sg.send(message)
        print(response)
        if response.status_code == 202:
            pass
        else:
            return Response({})
    except Exception as e:
        print(str(e))
        pass

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def PremiumSubscription(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # Get user from session
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    payment_method = request.query_params.get('payment_method', None)
    
    user_exists = CustomUser.objects.get(email=user_email)
    if user_exists is None:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    subscription = UserSubscription.objects.get(user=user_exists)
    subscription.Premium = True
    subscription.Basic = False
    subscription.Basic_Expiration = None
    # Set expiration to 1 month from now
    subscription.Premium_Expiration = timezone.now() + timezone.timedelta(days=30)
    serializer = UserSubscriptionSerializer(subscription)

    subscription.stripe_customer_id = customer['id']
    # Stripe customer creation stuff
    if stripe.Customer.list(email=user_email).data:
        customer = stripe.Customer.list(email=user_email).data[0]
    else:
        customer = stripe.Customer.create(
            email=user_email,
            name=user_exists.first_name + " " + user_exists.last_name,
            description="Premium Subscription",
            payment_method=payment_method,
        )

    premium_id = "price_1NPccdLPNbsO0xpZgksTl57Y"
    stripe.Subscription.create(
        customer=customer['id'],
        items=[
            {
                "price": premium_id,
            },
        ],
    )
    subscription.stripe_subscription_id = stripe.Subscription.list(
        customer=customer['id']).data[0]['id']
    subscription.save()

     # Send Signup Email
    template_id = "d-57f98ea68557417bbcb5b5a0ee77af46"
    message = Mail(
    from_email='ekj0512@gmail.com',
    to_emails=user_email,
    )
    message.template_id = template_id
    try:
        sg = sendgrid.SendGridAPIClient(api_key='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')  # Replace with your SendGrid API key
        response = sg.send(message)
        print(response)
        if response.status_code == 202:
            pass
        else:
            return Response({})
    except Exception as e:
        print(str(e))
        pass

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def CancelSubscription(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # Get user from session
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


    user_exists = CustomUser.objects.get(email=user_email)
    if user_exists is None:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    subscription = StreamLineSubscription.objects.get(user=user_exists)
    if subscription.Premium == False and subscription.Basic == False:
        return Response({'error': 'User does not have a subscription'}, status=status.HTTP_400_BAD_REQUEST)
    if subscription.Premium == True:
        subscription.Premium = False
        subscription.Premium_Expiration = None
    if subscription.Basic == True:
        subscription.Basic = False
        subscription.Basic_Expiration = None

    subscription.save()
    serializer = UserSubscriptionSerializer(subscription)

    # Stripe customer creation stuff
    if stripe.Customer.list(email=user_email).data:
        customer = stripe.Customer.list(email=user_email).data[0]
    else:
        return Response({'error': 'User does not have a subscription'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.Subscription.delete(subscription.stripe_subscription_id)
     # Send Signup Email
    template_id = "d-3a02207c24d94688a70caf7c168dd96a"
    message = Mail(
    from_email='ekj0512@gmail.com',
    to_emails=user_email,
    )
    message.template_id = template_id
    try:
        sg = sendgrid.SendGridAPIClient(api_key='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')  # Replace with your SendGrid API key
        response = sg.send(message)
        print(response)
        if response.status_code == 202:
            pass
        else:
            return Response({})
    except Exception as e:
        print(str(e))
        pass
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def UpgradeSubscription(request):
    pass
#prob has to be done once we've figured our shit out
