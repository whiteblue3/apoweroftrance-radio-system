from django.urls import path
from radio import views


app_name = 'radio'

urlpatterns = [
    path('upload', views.UploadAPI.as_view()),
]
