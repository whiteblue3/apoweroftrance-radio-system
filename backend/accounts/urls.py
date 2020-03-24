from django.urls import path
from accounts import views


app_name = 'accounts'

urlpatterns = [
    path('authenticate', views.AuthenticateAPI.as_view()),
    path('logout', views.LogOutAPI.as_view()),
    path('signup', views.RegistrationAPI.as_view()),
    path('reset_password/<str:email>', views.ResetPasswordAPI.as_view()),
    path('confirm_reset_password', views.ConfirmResetPasswordAPI.as_view()),
    path('ban', views.BanJWTAPIView.as_view()),
    path('info', views.UserRetrieveAPIView.as_view()),
    path('profile/<str:email>', views.ProfileRetrieveAPIView.as_view()),
    path('image', views.UserProfileImageUpdateAPIView.as_view()),
    path('update', views.UserUpdateAPIView.as_view()),
]
