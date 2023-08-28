from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('return-all-posts/', getAllPosts.as_view()),
    path('return-post/', getPost.as_view()),
    path('return-page-posts/', getPagePosts.as_view()),
]