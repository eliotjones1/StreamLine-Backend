# Create your views here.
import sendgrid
from django.contrib.auth import get_user_model, logout
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from sendgrid.helpers.mail import Mail

from settings.models import *
from webhooks.models import *
from . import serializers
from .utils import get_and_authenticate_user, create_user_account

# Create your views here.

User = get_user_model()

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {
        'login': serializers.UserLoginSerializer,
        'register': serializers.UserRegisterSerializer,
        'password_change': serializers.PasswordChangeSerializer,
    }
    queryset = CustomUser.objects.all()

    @action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(**serializer.validated_data)

        # Create a session for the user
        session = SessionStore()
        session['user_email'] = user.email
        session.save()
        data = serializers.AuthUserSerializer(user).data
        response = Response(data=data, status=status.HTTP_200_OK)
        response.set_cookie('sessionid', session.session_key, httponly=True, samesite='None', secure=True)
        return response

    @action(methods=['POST', ], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        user = data["email"]
        user_exists = CustomUser.objects.get(email = user)
        user_data = UserData(user = user_exists, budget = "0", bundle = {"Images":[], "Movies_and_TV_Shows":[]}, media = [])
        user_data.save()
        # create user settings
        user_settings = UserSettings(user = user_exists, Email = user_exists, First_Name = user_exists.first_name, Last_Name = user_exists.last_name, Street_Address = "", City = "", State_Province = "", Country = "", Postal_Code = "", Newsletter = True, Promotions = True, Push_Notifications = "Everything")
        user_settings.save()
        # create user tos check
        user_tos = TOSChecked(user = user_exists, TOS_Checked = False)
        user_tos.save()
        # create user subscription
        user_subscription = StreamLineSubscription(user = user_exists, Premium = False, Basic = False, Premium_Expiration = None, Basic_Expiration = None, stripe_customer_id = None, stripe_subscription_id = None)
        user_subscription.save()


        user_stripe = UserStripeCustomer(user = user_exists, stripe_customer_id = "")
        user_stripe.save()

        session = SessionStore()
        session['user'] = user
        session.save()
        print(user)
        # Send Welcome Email
        template_id = "d-65eff9edfd4f47e493b649f54bb336f6"
        message = Mail(
            from_email='ekj0512@gmail.com',
            to_emails=user,
        )
        message.template_id = template_id
        try:
            sg = sendgrid.SendGridAPIClient(api_key='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')
            response = sg.send(message)
            print(response)
            if response.status_code == 202:
                pass
            else:
                return Response({})
        except Exception as e:
            print(str(e))
            pass
        response = Response(data=data, status=status.HTTP_201_CREATED)
        response.set_cookie('sessionid', session.session_key, httponly=True, samesite='None', secure=True)
        print(response.cookies)
        return response

    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        # Delete the session
        session_key = request.COOKIES.get('sessionid')
        print(session_key)
        session = Session.objects.get(session_key=session_key)
        session.delete()
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ])
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

# @api_view(['POST'])
# @permission_classes([AllowAny, ])
# def login(request):
#     serializer = serializers.UserLoginSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     user = get_and_authenticate_user(**serializer.validated_data)
#     # Create a session for the user
#     session = SessionStore()
#     session['user_email'] = user.email
#     session.save()
#     data = serializers.AuthUserSerializer(user).data
#     response = Response(data=data, status=status.HTTP_200_OK)
#     response.set_cookie('sessionid', session.session_key, httponly=True, samesite='None', secure=True)
#     return response

# @api_view(['POST'])
# @permission_classes([AllowAny, ])
# def register(request):
#     serializer = serializers.UserRegisterSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     user = create_user_account(**serializer.validated_data)
#     data = serializers.AuthUserSerializer(user).data
#     user = data["email"]
#     user_exists = CustomUser.objects.get(email = user)
#     user_data = UserData(user = user_exists, budget = "0", bundle = {"Images":[], "Movies_and_TV_Shows":[]}, media = [])
#     user_data.save()
#     # create user settings
#     user_settings = UserSettings(user = user_exists, Email = user_exists, First_Name = user_exists.first_name, Last_Name = user_exists.last_name, Street_Address = "", City = "", State_Province = "", Country = "", Postal_Code = "", Newsletter = True, Promotions = True, Push_Notifications = "Everything")
#     user_settings.save()
#     # create user tos check
#     user_tos = TOSChecked(user = user_exists, TOS_Checked = False)
#     user_tos.save()
#     # create user subscription
#     user_subscription = StreamLineSubscription(user = user_exists, Premium = False, Basic = False, Premium_Expiration = None, Basic_Expiration = None, stripe_customer_id = None, stripe_subscription_id = None)
#     user_subscription.save()
#     session = SessionStore()
#     session['user'] = user
#     session.save()
#     print(user)
#     # Send Welcome Email
#     template_id = "d-65eff9edfd4f47e493b649f54bb336f6"
#     message = Mail(
#     from_email='ekj0512@gmail.com',
#     to_emails=user,
#     )
#     message.template_id = template_id
#     try:
#         sg = sendgrid.SendGridAPIClient(api_key='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')  # Replace with your SendGrid API key
#         response = sg.send(message)
#         print(response)
#         if response.status_code == 202:
#             pass
#         else:
#             return Response({})
#     except Exception as e:
#         print(str(e))
#         pass
#     response = Response(data=data, status=status.HTTP_201_CREATED)
#     response.set_cookie('sessionid', session.session_key, httponly=True, samesite='None', secure=True)
#     print(response.cookies)
#     return response

# @api_view(['POST'])
# @permission_classes([AllowAny, ])
# def logout(request):
#     # Delete the session
#     session_key = request.COOKIES.get('sessionid')
#     print(session_key)
#     session = Session.objects.get(session_key=session_key)
#     session.delete()
#     logout(request)
#     data = {'success': 'Sucessfully logged out'}
#     return Response(data=data, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated, ])
# def password_change(request):
#     serializer = serializers.PasswordChangeSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     request.user.set_password(serializer.validated_data['new_password'])
#     request.user.save()
#     return Response(status=status.HTTP_204_NO_CONTENT)