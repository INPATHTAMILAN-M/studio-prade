from django.contrib import admin
from .routers import router
from django.urls import path, include
from . import views

urlpatterns = [

    path('api/suggestion/',views.Suggestion.as_view(), name='suggestion'),
]

# urlpatterns = [
#     path('', include(router.urls)),  # Includes all router-generated URLs

# ]

