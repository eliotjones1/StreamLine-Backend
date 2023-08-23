from rest_framework import routers
from django.urls import path, include
from .views import AuthViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register('auth', AuthViewSet, basename='auth')


urlpatterns = router.urls