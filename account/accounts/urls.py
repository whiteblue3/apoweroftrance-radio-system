from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('authenticate', views.AuthenticateAPI.as_view()),
    path('logout', views.LogOutAPI.as_view()),
    path('signup', views.RegistrationAPI.as_view()),
    path('signout', views.DeleteAPI.as_view()),
    path('reset_password/<str:email>', views.ResetPasswordAPI.as_view()),
    path('confirm_reset_password', views.ConfirmResetPasswordAPI.as_view()),
    path('activate', views.ActivateAPI.as_view()),
    path('ban', views.BanJWTAPIView.as_view()),
    path('info', views.UserRetrieveAPIView.as_view()),
    path('profile/<int:user_id>', views.ProfileRetrieveAPIView.as_view()),
    path('image', views.UserProfileImageUpdateAPIView.as_view()),
    path('update', views.UserUpdateAPIView.as_view()),
    path('list', views.UserListAPIView.as_view()),
    path('follow/<int:follow_user_id>', views.FollowAPIView.as_view()),
    path('followers', views.FollowerListAPIView.as_view()),
    path('follows', views.FollowListAPIView.as_view()),
]
