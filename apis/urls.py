from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from apis import views

app_name = 'api'
urlpatterns = [
    # authentication api
    path('api-token-auth/', views.CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('api-token-logout/', views.Logout.as_view(), name='api_token_logout'),

    path('password/', views.Password.as_view(), name='forgot-password'),
    path('reset/', views.Reset.as_view(), name='reset-password'),
    path('request/', views.Request.as_view(), name='request'),

    # community api
    path('fake-post/', views.FakePost.as_view(), name='fake-post'),
    path('fake-comment/', views.FakeComment.as_view(), name='fake-comment'),
    path('posts/', views.PostList.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.PostDetail.as_view(), name='single-post'),
    path('comments/', views.CommentList.as_view(), name='comment-list'),
    path('comments/<int:pk>/', views.CommentDetail.as_view(), name='single-comment'),

    # affiliates api
    path('profile/', views.Profile.as_view(), name='profile'),
    path('list/campaign/', views.ListCampaign.as_view(), name='list-campaign'),
    path('campaigns/', views.CampaignList.as_view(), name='campaign-list'),
    path('campaigns/<int:pk>/', views.CampaignDetail.as_view(), name='single-campaign'),
    path('reports/', views.ReportList.as_view(), name='report-list'),
    path('adashboard/', views.AffiliatesDashboard.as_view(), name='affiliates-dashboard'),
    path('contact/', views.Contact.as_view(), name='contact'),

    # screen recoder api
    path('trade-list/', views.TradeList.as_view(), name='trade-list'),
    path('trade-token/', views.TradeToken.as_view(), name='trade-token'),
    path('srecorder-upload/', views.SRecorderUpload.as_view(), name='srecorder-upload'),
]