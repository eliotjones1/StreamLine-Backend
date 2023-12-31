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

class SubStatus(generics.ListAPIView):
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

        user = CustomUser.objects.get(email=user_email)
        output = StreamLineSubscription.objects.get(user=user)
        serializer = UserSubscriptionSerializer(output)
        return Response(serializer.data)









