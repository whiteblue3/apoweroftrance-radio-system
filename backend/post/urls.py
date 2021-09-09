from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    path('claim/list', views.ClaimListAPI.as_view()),
    path('claim/post', views.PostClaimAPI.as_view()),
    path('claim/update', views.UpdateClaimAPI.as_view()),
    path('claim/status', views.UpdateClaimStatusAPI.as_view()),
    path('claim/staff_action', views.UpdateClaimStaffActionAPI.as_view()),
    path('claim/accept/<int:claim_id>', views.AcceptClaimAPI.as_view()),
    path('claim/detail/<int:claim_id>', views.ClaimRetrieveAPI.as_view()),
    path('claim/reply/list', views.ClaimReplyListAPI.as_view()),
    path('claim/reply/post', views.PostClaimReplyAPI.as_view()),
    path('comment/list', views.CommentListAPI.as_view()),
    path('comment/post', views.PostCommentAPI.as_view()),
    path('comment/delete/<int:comment_id>', views.DeleteCommentAPI.as_view()),
    path('directmessage/list', views.DirectMessageListAPI.as_view()),
    path('directmessage/post', views.PostDirectMessageAPI.as_view()),
    path('directmessage/delete/<int:message_id>', views.DeleteDirectMessageAPI.as_view()),
    path('notification/list', views.NotificationListAPI.as_view()),
    path('notification/post', views.PostNotificationAPI.as_view()),
    path('track/tag/list', views.TrackTagListAPI.as_view()),
    path('track/tag/post', views.PostTrackTagAPI.as_view()),
    path('stream/feed', views.StreamFeedAPI.as_view()),
]
