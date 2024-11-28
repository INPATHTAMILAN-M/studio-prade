from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomAuthForm
from django.contrib.auth import logout as user_logout
from django.shortcuts import redirect
from .serializers import My_Profile_Serializer,Edit_Profile_Serializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import viewsets
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth import get_user_model
from account.models import User
from postapp.models import Following,Brand


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Edit_Profile_Serializer
    allowed_methods = ['get', 'patch']

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        edit_profile = My_Profile_Serializer(user, context={'request': request})
        return Response(edit_profile.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            profile = My_Profile_Serializer(request.user, context={'request': request})
            return Response(profile.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
#Handles requests to follow or unfollow brands, categories, or users.
class Follow_Unfollow(APIView):
    def post(self, request, *args, **kwargs):
        brand_id = request.data.get("brand_id")
        category_id = request.data.get("category_id")
        following_user_id = request.data.get("following_user_id")
        user = request.user     
        if brand_id:
            try:
                brand = Brand.objects.get(id=brand_id)
                try:
                    following = Following.objects.get(user=user, brand=brand)
                    following.delete()
                    return Response({"message": "Brand unfollowed successfully"}, status=status.HTTP_200_OK)
                except Following.DoesNotExist:
                    Following.objects.create(user=user, brand=brand)
                    return Response({"message": "Brand followed successfully"}, status=status.HTTP_201_CREATED)
            except Brand.DoesNotExist:
                return Response({"message": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
        elif category_id:
            try:
                category = Post_Category.objects.get(id=category_id)
                try:
                    following = Following.objects.get(user=user, category=category)
                    following.delete()
                    return Response({"message": "Category unfollowed successfully"}, status=status.HTTP_200_OK)
                except Following.DoesNotExist:
                    Following.objects.create(user=user, category=category)
                    return Response({"message": "Category followed successfully"}, status=status.HTTP_201_CREATED)
            except Post_Category.DoesNotExist:
                return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        elif following_user_id:
            try:
                following_user = User.objects.get(id=following_user_id)
                if following_user == user:
                    return Response({"message": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    following = Following.objects.get(user=user, following_user=following_user)
                    following.delete()
                    return Response({"message": "User unfollowed successfully"}, status=status.HTTP_200_OK)
                except Following.DoesNotExist:
                    Following.objects.create(user=user, following_user=following_user)
                    return Response({"message": "User followed successfully"}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Please provide brand_id, category_id, or following_user_id"}, status=status.HTTP_400_BAD_REQUEST)