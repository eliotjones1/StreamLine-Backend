from rest_framework import routers
from django.urls import path, include
from .views import login, register, logout, password_change

# router = routers.DefaultRouter(trailing_slash=False)
# router.register('auth', AuthViewSet, basename='auth')


urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('change-password/', password_change, name='password_change'),
    # path('', include(router.urls)),
]