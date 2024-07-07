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
from api.views import isSessionActive

# Create your views here.
stripe.api_key = "sk_test_51NPcYzLPNbsO0xpZ3ypmarjukmXpUaySegVecBCiZEcfbiUrBxeuXBQU8QiafXpARoIUKdU2uqzdifzly9DlWedt00aO6ZevFh"

class ReturnSettings(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        # print(sessionid)
        # Check if session is active
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        # Get user from session
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        output = UserSettings.objects.get(Email=user_email)
        serializer = UserSettingsSerializer(output)
        return Response(serializer.data)

# Update UserSettings
@api_view(['POST'])
def UpdateSettings(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # Get user from session
    data = request.data
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    user = CustomUser.objects.get(email=user_email)
    if user_email != data['Email']:
        # store temp info
        temp_subs = store_temp_subs(StreamLineSubscription.objects.get(user=user))
        temp_data = store_temp_data(UserData.objects.get(user=user))
        # delete old user settings, subs, data
        UserSettings.objects.get(Email=user_email).delete()
        StreamLineSubscription.objects.get(user=user).delete()
        UserData.objects.get(user=user).delete()
        user.email = data['Email']
        user.save()

        # create new user settings, subs, data
        user_settings = UserSettings.objects.create(
            user = user,
            Email=user,
            First_Name=data['First_Name'],
            Last_Name=data['Last_Name'],
            Street_Address=data['Street_Address'],
            City=data['City'],
            State_Province=data['State_Province'],
            Country=data['Country'],
            Postal_Code=data['Postal_Code'],
            Newsletter=data['Newsletter'],
            Promotions=data['Promotions'],
            Push_Notifications=data['Push_Notifications'],
        )
        user_settings.save()
        user_sub = StreamLineSubscription.objects.create(
            user=user,
            Basic=temp_subs['Basic'],
            Basic_Expiration=temp_subs['Basic_Expiration'],
            Premium=temp_subs['Premium'],
            Premium_Expiration=temp_subs['Premium_Expiration'],
        )
        user_sub.save()
        user_data = UserData.objects.create(
            user=user,
            budget=temp_data['budget'],
            bundle=temp_data['bundle'],
            media=temp_data['media'],
        )
        user_data.save()
        print(user_data)
        print(user_settings)
        print(user_sub)
        settings_serializer = UserSettingsSerializer(user_settings)
        user_serializer = AuthUserSerializer(user)
        output = {
            "settings": settings_serializer.data,
            "user": user_serializer.data,
        }
        return Response(output, status=status.HTTP_200_OK)

    user = CustomUser.objects.get(email=data['Email'])
    if user is None:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    user_settings = UserSettings.objects.get(user=user)
    # Check if user_settings
    if user_settings is None:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    # Update user_settings
    user_settings.First_Name = data['First_Name']
    user_settings.Last_Name = data['Last_Name']
    user_settings.Street_Address = data['Street_Address']
    user_settings.City = data['City']
    user_settings.State_Province = data['State_Province']
    user_settings.Country = data['Country']
    user_settings.Postal_Code = data['Postal_Code']
    user_settings.Newsletter = data['Newsletter']
    user_settings.Promotions = data['Promotions']
    user_settings.Push_Notifications = data['Push_Notifications']
    user_settings.save()
    settings_serializer = UserSettingsSerializer(user_settings)
    user_serializer = AuthUserSerializer(user)
    output = {
        "settings": settings_serializer.data,
        "user": user_serializer.data,
    }
    return Response(output, status=status.HTTP_200_OK)

@api_view(['POST'])
def deleteAccount(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # Get user from session
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    user = CustomUser.objects.get(email=user_email)
    user_data = UserData.objects.get(user=user)
    user_settings = UserSettings.objects.get(user=user)
    user_sub = StreamLineSubscription.objects.get(user=user)
    # Check if user_settings
    if user_settings is None:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    # Update user_settings
    session = Session.objects.get(session_key=sessionid)
    session.delete()
    user_settings.delete()
    user.delete()
    user_data.delete()
    user_sub.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def ContactFormSub(request):
    data = request.data
    user_email = data['email']
    user_first_name = data['first-name']
    user_last_name = data['last-name']
    user_phone = data['phone-number']
    user_message = data['message']

    new_contact_sub = UserContactRequest(user_email = user_email, user_first_name = user_first_name, user_last_name = user_last_name, user_message = user_message, user_phone_number = user_phone)
    new_contact_sub.save()
    email_content = f"User {user_first_name} has the following problem: \n\n{user_message}\n\n You can email them with a response at: {user_email}"
    # Send Contact Email
    message = Mail(
    from_email='ekj0512@gmail.com',
    to_emails= ['ekj0512@gmail.com', 'rycdunn01@stanford.edu'], 
    subject = 'Contact Form Submission',
    html_content = HtmlContent(email_content)
    )
    # try:
    #     sg = SendGridAPIClient(api_key='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')  # Replace with your SendGrid API key
    #     response = sg.send(message)
    #     if response.status_code == 202:
    #         return Response(status=status.HTTP_200_OK)
    #     else:
    #         print("fail")
    #         return Response({})
    # except Exception as e:
    #     print(str(e))
    #     return Response(status=status.HTTP_400_BAD_REQUEST)
    sg = SendGridAPIClient(api_key='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')  
    response = sg.send(message)
    print(response)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def agreeTOS(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # expects user_id at 0, subscription info (name, date) at 1. Expect name to be from our list of possible (like a search and drop down type thing, 
    # Needs to be exact string
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    user = CustomUser.objects.get(email=user_email)
    tos = TOSChecked.objects.get(user=user)
    tos.TOS_Checked = True
    tos.save()
    return Response(status=status.HTTP_200_OK)

class checkTOSStatus(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        print("TOS")
        print(sessionid)
        # Check if session is active
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user = CustomUser.objects.get(email=user_email)
        tos = TOSChecked.objects.get(user=user)
        if tos.TOS_Checked == True:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("not ok", status=status.HTTP_200_OK)

class isAuthenticated(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"Status": "OK"})