from django.shortcuts import render
from .models import BlogPost
import requests
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import BlogPostSerializer
from authentication.models import CustomUser
import math



SECRET_KEY = "9fG2Jm5qZkRLpcYn6vjDWhYUdN1X3tH4" # Why are you here

class getAllPosts(generics.ListAPIView):
    def get(self, request):
        queryset = BlogPost.objects.all()
        # Get all blog posts
        data = BlogPost.objects.order_by('-created_at')
        # Serialize the posts
        response = BlogPostSerializer(data, many=True).data
        return Response(response, status=status.HTTP_200_OK)
    
class getPost(generics.ListAPIView):
    def get(self, request):
        # Get the post id
        id = request.query_params.get('id')
        # Get the post
        data = BlogPost.objects.get(id=id)
        if data is None:
            return Response({'error': 'No post with that id'}, status=status.HTTP_400_BAD_REQUEST)
        # Serialize the post
        response = BlogPostSerializer(data).data
        return Response(response, status=status.HTTP_200_OK)
    
class getPagePosts(generics.ListAPIView):
    def get(self, request):
        # Get the page number
        page = request.query_params.get('page')
        # Get the posts
        data = BlogPost.objects.order_by('-created_at')
        # There are only 6 per page, so we need to get the correct posts
        if int(page) > math.floor(len(data) / 6):
            data = data[(int(page)-1)*6:]
        else:
            data = data[(int(page)-1)*6:int(page)*6]
        # Serialize the posts
        posts = BlogPostSerializer(data, many=True).data
        response = {"posts": posts, "totalPages": math.ceil(len(data) / 6)}
        return Response(response, status=status.HTTP_200_OK)

## NEED TO ADD PAGINATION