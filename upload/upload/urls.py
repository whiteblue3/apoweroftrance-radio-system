from django.urls import path
from upload import views


app_name = 'upload'

urlpatterns = [
    path('upload', views.UploadAPI.as_view()),
    path('replace', views.ReplaceAPI.as_view()),
]
