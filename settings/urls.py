from django.urls import path
from django.contrib import admin
from .settings_views import *
from .subscription_views import *
from .account_views import *

urlpatterns = [
    path('get-user-settings/', ReturnSettings.as_view(), name='user-settings'),
    path('update-user-settings/', UpdateSettings, name='update-settings'),
    path('delete-user-account/', deleteAccount, name='delete-account'),
    path('subscription/status/', SubStatus.as_view(), name='subscription-status'),
    path('user-subscriptions/create/', createSubscription, name='create-subscription'),
    path('user-subscriptions/cancel/', removeSubscription, name='remove-subscription'),
    path('user-subscriptions/renew/', renewSubscription, name='renew-subscription'),
    path('user-subscriptions/view/', getSubscriptions.as_view(), name='view-subscriptions'),
    path('avail-subscriptions/search/', AvailSubs.as_view(), name='search-subscriptions'),
    path('tosCompliance/', checkTOSStatus.as_view(), name='tos-compliance'),
    path('tosCompliance/update/', agreeTOS, name='update-tos-compliance'),
    path('user-subscriptions/generateBundle/', generateBundle, name='create-bundle'),
    path('user-subscriptions/upcoming/', getMyUpcoming.as_view(), name='get-upcoming'),
    path('contact/', ContactFormSub, name='contact-us'),
    path('is-authenticated/', isAuthenticated.as_view(), name='is-authenticated'),
    path('user-subscriptions/recommendations/', recommendedServices.as_view(), name='get-recommendations'),
]

