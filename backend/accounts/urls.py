from django.urls import path
from accounts import views


app_name = 'accounts'

urlpatterns = [
    path('authenticate', views.AuthenticateAPI.as_view()),
    path('register', views.RegistrationAPI.as_view()),
    path('reset_password', views.ResetPasswordAPI.as_view()),
    path('confirm_reset_password', views.ConfirmResetPasswordAPI.as_view()),
    path('ban', views.BanJWTAPIView.as_view()),
]
