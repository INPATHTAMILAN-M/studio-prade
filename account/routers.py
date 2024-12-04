from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'profile',ProfileViewSet, basename='Profile')
router.register(r'sso-auth', UserViewSet, basename='Sso-Auth')
router.register(r'follow-user', FollowingViewSet, basename='Folllow-User')



