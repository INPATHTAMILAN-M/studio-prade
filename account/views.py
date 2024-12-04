from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
import requests


from account.models import User
from .serializers import ProfileSerializer,FollowingSerializer
from postapp.models import Following

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]    
    http_method_names = ['get','patch']


    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            profile = serializer.instance
            return Response(profile.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    http_method_names = ['post']

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION", "").removeprefix("JWT ").strip()

        if not token:
            return JsonResponse({"message": "Access Token is required"}, status=400)

        # Verify token with external service
        response = self._verify_token(token)

        if response.status_code != 200 or "errors" in response.json():
            return JsonResponse({"error": "User not found"}, status=404)

        user_data = response.json().get("data", {}).get("tokenVerify", {}).get("user")
        is_valid = response.json().get("data", {}).get("tokenVerify", {}).get("isValid")

        if not is_valid or not user_data or not user_data.get("email"):
            return JsonResponse({"error": "Invalid token or user not found"}, status=400)

        # Get or create user based on the verified email
        user = self._get_or_create_user(user_data)

        # Generate access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "message": "User logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token
        }, status=status.HTTP_200_OK)

    def _verify_token(self, token):
        """ Helper method to verify token with external service. """
        query = {
            "query": f"""mutation {{
                tokenVerify(token: "{token}") {{
                    user {{
                        email
                        isActive
                        firstName
                        lastName
                    }}
                    isValid
                }}
            }}"""
        }
        return requests.post(
            f"{settings.PRADE_BACKEND_URL}/graphql/",
            json=query,
            headers={"Authorization": f"JWT {token}", "Content-Type": "application/json"},
            verify=False
        )

    def _get_or_create_user(self, user_data):
        """ Helper method to get or create user. """
        User = get_user_model()
        user, created = User.objects.get_or_create(email=user_data["email"].lower())

        if created:
            user.username = user.email
            user.first_name = user_data.get("firstName", "")
            user.last_name = user_data.get("lastName", "")
            user.is_active = user_data.get("isActive", True)
            user.save()

        return user
    
class FollowingViewSet(viewsets.ModelViewSet):
    queryset = Following.objects.all()
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        # Only return follow relationships for the authenticated user
        return Following.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='follow-unfollow')
    def follow_unfollow(self, request, *args, **kwargs):
        # Retrieve input data (brand, category, or following_user)
        brand_id = request.data.get("brand_id")
        category_id = request.data.get("category_id")
        following_user_id = request.data.get("following_user_id")
        user = request.user

        # Prepare the data for serializer
        data = {
            'user': user.id,
            'brand': brand_id if brand_id else None,
            'category': category_id if category_id else None,
            'following_user': following_user_id if following_user_id else None
        }

        # Initialize the serializer
        serializer = self.get_serializer(data=data)

        # Validate and create the follow/unfollow relationship
        if serializer.is_valid():
            # Check if the follow relationship exists
            following, created = Following.objects.get_or_create(user=user, **serializer.validated_data)
            if created:
                return Response({"message": "Followed successfully"}, status=status.HTTP_201_CREATED)
            else:
                following.delete()
                return Response({"message": "Unfollowed successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)