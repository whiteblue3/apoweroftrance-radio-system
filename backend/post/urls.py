from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    path('comment/list', views.CommentListAPI.as_view()),
    path('comment/post', views.PostCommentAPI.as_view()),
    path('directmessage/list', views.DirectMessageListAPI.as_view()),
    path('directmessage/post', views.PostDirectMessageAPI.as_view()),
    path('notification/list', views.NotificationListAPI.as_view()),
]
