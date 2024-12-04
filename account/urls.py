from django.contrib import admin
from django.urls import path,include
from .routers import router
from django.contrib.auth import views as auth_views
from . import views

# urlpatterns = [
#     #API
#     # path('api/profile/',views.My_Profile_View.as_view(), name='pro'),
#     path('api/follow-unfollow/', views.Follow_Unfollow.as_view(), name='follow_unfollow'),
        
# ]

urlpatterns = [
    path('', include(router.urls)),  # Includes all router-generated URLs
]
