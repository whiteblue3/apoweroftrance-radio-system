from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    path('config', views.ConfigListAPI.as_view()),
]
