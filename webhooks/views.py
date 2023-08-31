from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json
import stripe

stripe.api_key = "sk_test_51NPcYzLPNbsO0xpZ3ypmarjukmXpUaySegVecBCiZEcfbiUrBxeuXBQU8QiafXpARoIUKdU2uqzdifzly9DlWedt00aO6ZevFh"

# Create your views here.
@csrf_exempt
@api_view(['POST'])
def recieveStripeWebhook(request):
    # payload = request.body
    # event = None

    # try:
    #     event = stripe.Event.construct_from(
    #     json.loads(payload), stripe.api_key
    #     )
    # except ValueError as e:
    #     return Response(status=status.HTTP_400_BAD_REQUEST)
    # # Handle the event

    print(request.data)
    return Response(status=status.HTTP_200_OK)