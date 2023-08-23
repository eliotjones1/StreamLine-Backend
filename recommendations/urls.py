from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('generate-data/', generate.as_view(), name='generateData'),
    path('save-rating/', saveRating, name='saveRating'),
    path('get-recommendations/', returnRecommendations.as_view(), name='returnRecommendations'),
    path('save-email/', saveEmail, name='saveEmail'),
]