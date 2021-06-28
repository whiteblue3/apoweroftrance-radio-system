from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    path('claim/list', views.ClaimListAPI.as_view()),
    path('claim/post', views.PostClaimAPI.as_view()),
    path('claim/status', views.UpdateClaimStatusAPI.as_view()),
    path('claim/accept/<int:claim_id>', views.AcceptClaimAPI.as_view()),
    path('claim/detail/<int:claim_id>', views.ClaimRetrieveAPI.as_view()),
    path('claim/reply/list', views.ClaimReplyListAPI.as_view()),
    path('claim/reply/post', views.PostClaimReplyAPI.as_view()),
    path('comment/list', views.CommentListAPI.as_view()),
    path('comment/post', views.PostCommentAPI.as_view()),
    path('directmessage/list', views.DirectMessageListAPI.as_view()),
    path('directmessage/post', views.PostDirectMessageAPI.as_view()),
    path('notification/list', views.NotificationListAPI.as_view()),
]
