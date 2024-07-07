import requests
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .functions import *
import cvxpy as cp
import numpy as np
import pandas as pd
from django.core.cache import cache
from authentication.models import CustomUser
from authentication.serializers import *
from .models import *
from .serializers import *
from surprise import Reader, Dataset
from .functions import *
from api.functions import *
from django.contrib.sessions.models import Session
from api.views import isSessionActive
from settings.models import ThirdPartySubscription


@api_view(['POST'])
def saveRating(request):
    sessionid = request.COOKIES.get('sessionid')
    if not isSessionActive(sessionid):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    # Expect email to be at 0
    # Expect object at 1, rating at 2
    # Functionality: When the user, in their dashboard, removes something from their list, we prompt them to rate it. 
    # This rating corresponds to the TMDB ID of the media, and gets saved to their account. Have users rate by choosing a number 1-10.
    # Maybe prompt them to rate some stuff in the beginning, and then have them rate media as they remove them from their list.
    object = data[0]
    rating = data[1]
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    user_exists = CustomUser.objects.get(email = user_email).id
    print(user_exists)

    # If there is a MediaRatings entry with the same object_id and user, we want to override it with new information. 
    # Else, create a new entry
    if MediaRatings.objects.filter(media_id = object["id"], user_id = user_exists).exists():
        current = MediaRatings.objects.get(media_id = object["id"], user_id = user_exists)
        current.rating = rating
        current.save()
    else:
        if object["media_type"] == "tv":
            services = getStreamingProviderShow(object["id"])
        else:
            services = getStreamingProviderMovie(object["id"])
        new = MediaRatings(media_id = object["id"], user_id = user_exists, rating = rating, type = object["media_type"], streaming_providers = services)
        new.save()

    return Response({"Status":"OK"})


class returnRecommendations(generics.ListAPIView):
     def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        if not isSessionActive(sessionid):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user_exists = CustomUser.objects.get(email = user_email)
        # If user doesn't exist throw an error
        if not user_exists:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            subscriptions = ThirdPartySubscription.objects.filter(user=user_exists)
            subscriptions = list(subscriptions.values_list('subscription_name', flat=True))
            user_id = user_exists.id
            if not MediaRatings.objects.filter(user_id = user_id).exists() or len(MediaRatings.objects.filter(user_id = user_id)) < 10:
                return Response({'Oops! This User does not have enough ratings'}, status=status.HTTP_200_OK)
            recs = returnRecs(user_exists.id, subscriptions)
            return Response(recOutput(recs, subscriptions), status=status.HTTP_200_OK)


class generate(generics.ListAPIView):
    def get(self, request):
        query = request.query_params.get('generate', None)
        if query is None:
            return Response({'error': 'Missing search query'}, status=status.HTTP_400_BAD_REQUEST)
        elif query == '1':
            for i in range(1,26):
                page_input = str(i)
                generateData(page_input)
            return Response({'Status': 'OK'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Query set to 0'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def saveEmail(request):
    email = request.data
    new_email = UserEmail(email=email)
    new_email.save()
    return Response(status=status.HTTP_200_OK)