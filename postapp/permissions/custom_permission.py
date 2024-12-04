from rest_framework.permissions import BasePermission

class IsAuthenticatedForGET(BasePermission):
    def has_permission(self, request, view):
        # Only allow GET requests for authenticated users
        if request.method != 'GET' and not request.user.is_authenticated:
            return False
        return True
    
    
