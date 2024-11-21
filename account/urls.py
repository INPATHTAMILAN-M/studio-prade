from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/',views.CustomLoginView.as_view(), name='login',kwargs={'redirect_authenticated_user': True}),  
    path('logout/',views.logout, name="logout"),

    #API
    path('api/register/', views.RegisterAPI.as_view(), name='register'),
    path('api/login/',views.Login_View.as_view(), name='signin'),
    path('api/reset-password/', views.PasswordResetView.as_view(), name='password-reset'),
    path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = "registration/password_reset_form.html"), name ='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name = "registration/password_reset_done.html"), name ='password_reset_complete'),
    path('api/change_password/', views.Change_Password.as_view(), name='change_password'),
    path('api/my_profile_view/',views.My_Profile_View.as_view(), name='my_profile_view'),
    path('api/edit_profile/',views.Edit_Profile.as_view(), name='edit_profile'),
    path('api/follow_unfollow/', views.Follow_Unfollow.as_view(), name='follow_unfollow'),
        
]
