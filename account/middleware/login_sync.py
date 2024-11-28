from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import login
from django.contrib.auth import get_user_model
import requests



user = get_user_model()


class LoginSyncMiddleware(MiddlewareMixin):
    """
    Middleware to synchronize login between Studio and Prade platforms.
    """

    def process_request(self, request):
        # Extract and validate token
        token = request.META.get("HTTP_AUTHORIZATION", "").removeprefix("JWT ").strip()
        if not token:
            return JsonResponse({"message": "Access Token is required"}, status=400)

        # Verify token with GraphQL API
        response = requests.post(
            f"{settings.PRADE_BACKEND_URL}/graphql/",
            json={"query": """
                {
                    me {
                        email
                        firstName
                        lastName
                    }
                }
            """},
            headers={
                "Authorization": f"JWT {token}",
                "Content-Type": "application/json"
            },
            verify=False
        )

        # Handle errors in response
        if response.status_code != 200 or "errors" in response.json():
            return JsonResponse({"error": "User not found"}, status=404)

        user_data = response.json().get("data", {}).get("me")
        if not user_data or not user_data.get("email"):
            return JsonResponse({"error": "User data is invalid or incomplete"}, status=404)

        # Get or create user in Studio
        User = get_user_model()
        user, created = User.objects.get_or_create(email=user_data["email"].lower())

        if created:
            user.username = user.email
            user.first_name = user_data.get("firstName", "")
            user.last_name = user_data.get("lastName", "")
            user.is_active = True
            user.save()

        login(request, user)
        return None    