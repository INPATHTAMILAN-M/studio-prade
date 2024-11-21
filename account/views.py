from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomAuthForm
from django.contrib.auth import logout as user_logout
from django.shortcuts import redirect
from .serializers import  RegisterSerializer, UserSerializer, LoginSerializer,PasswordResetSerializer,ChangePassword_Serializer,Following_Serializer,My_Profile_Serializer,Edit_Profile_Serializer,Password_Reset_Serializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth import get_user_model
from account.models import User
from postapp.models import Following,Brand


#login view
class CustomLoginView(LoginView):
    authentication_form = CustomAuthForm
    redirect_authenticated_user = True

#logout view
def logout(request):
    request.session['is_logout'] = True
    user_logout(request)
    return redirect('/login/')

#To authenticate and generate an access token for the user.    
class Login_View(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#View for logging out a user.
class Logout(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

#view allows a user to request a password reset by providing their email address.
class PasswordResetView(APIView):
    authentication_classes = ()
    permission_classes = ()
    
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.reset_password()
            if user:
                return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#To register a new user.
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(email=request.data['username'])
        return Response({"user": UserSerializer(user, context=self.get_serializer_context()).data},  status=201)
    
#To change the user password.
class Change_Password(ListAPIView):

    def post(self, request,format=None):
        serializer = ChangePassword_Serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"message": "Old password is incorrect."},status=status.HTTP_400_BAD_REQUEST)

            if serializer.validated_data['new_password'] != serializer.validated_data['confirm_new_password']:
                return Response({"message": "New passwords do not match."},status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user) 
            return Response({"message": "Password changed successfully."},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#To retrieve the user profile details and following brands.
class My_Profile_View(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        following_brand = Following.objects.filter(user=user)
        following_brands = Following_Serializer(following_brand, many=True, context={'request': request})
        my_profile = My_Profile_Serializer(user,context={'request': request})
        context = {
            'my_profile': my_profile.data ,
            'following_brands': following_brands.data,
        }
        return Response(context, status=status.HTTP_200_OK)

#Retrieves and update the profile details of the authenticated user.
class Edit_Profile(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        edit_profile = My_Profile_Serializer(user,context={'request':request})
        return Response(edit_profile.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = Edit_Profile_Serializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            profile = My_Profile_Serializer(request.user,context={'request':request})
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