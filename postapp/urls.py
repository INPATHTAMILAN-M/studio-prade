from django.contrib import admin
from .routers import router
from django.urls import path, include
from . import views

# urlpatterns = [
#     path('api/post/',views.PostView.as_view(), name='post_api'),
#     path('api/bookmark_view/',views.BookmarkView.as_view(), name='bookmark_view'),
#     path('api/bookmark_add/',views.BookmarkAdd.as_view(), name='bookmark_add'),
#     path('api/report_post/', views.ReportPostView.as_view(), name='report_post'),
#     path('api/like_unlike/<int:pk>/',views.LikeUnlikeView.as_view(), name="api_like_unlike"),
#     path('api/post_view/', views.UserPostView.as_view(), name='post_view'),
#     path('api/post_create/', views.PostCreate.as_view(), name='post_create'),
#     #path('api/post_edit/<int:pk>/', views.Post_Edit.as_view(), name='post_edit'),
#     path('api/post_delete/<int:pk>/', views.PostDelete.as_view(), name='post_delete'),
#     path('api/post_active_inactive/<int:pk>/', views.PostActiveInactive.as_view(), name='post_active_inactive'),
#     path('api/post_filter/', views.Post_Filter.as_view(), name='post_filter'),
#     path('api/post_user_filter/<int:pk>/', views.Post_User_Filter.as_view(), name='post_filter'),
#     path('api/following_post_filter/', views.Following_Post_Filter.as_view(), name='following_post_filter'),
#     path('api/suggestion/',views.Suggestion.as_view(), name='suggestion'),
    

# ]

urlpatterns = [
    path('api/', include(router.urls)),  # Includes all router-generated URLs

]

