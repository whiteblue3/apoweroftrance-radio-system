from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    path('comment/list', views.CommentListAPI.as_view()),
    path('comment/post', views.PostCommentAPI.as_view()),
]
