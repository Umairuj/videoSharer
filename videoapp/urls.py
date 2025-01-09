from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    VideoListCreateView,
    VideoDetailView,
    RatingListCreateView,
    RatingDetailView,
    HomePageView,
    VideoFeedView,
    UploadVideoView,
    ProfileView,
    SettingsView,
    AboutView,
    ContactView,
    VideoLikeView,
    VideoCommentView,
    VideoSearchView,
)

urlpatterns = [
    # User endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='login'),  # Changed to match template
    path('logout/', UserLogoutView.as_view(), name='logout'),  # Changed to match template
    
    # Video endpoints
    path('videos/', VideoListCreateView.as_view(), name='video-list-create'),
    path('videos/<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
    
    # Feed and video interaction endpoints
    path('feed/', VideoFeedView.as_view(), name='video_feed'),  # Changed to match template
    path('feed/<int:video_id>/', VideoFeedView.as_view(), name='video_feed'),  # Single URL pattern for feed
    
    # API endpoints for video interactions
    path('api/videos/<int:video_id>/like/', VideoLikeView.as_view(), name='video_like'),
    path('api/videos/<int:video_id>/comment/', VideoCommentView.as_view(), name='video_comment'),
    path('api/videos/search/', VideoSearchView.as_view(), name='video_search'),
    
    # Rating endpoints
    path('ratings/', RatingListCreateView.as_view(), name='rating-list-create'),
    path('ratings/<int:pk>/', RatingDetailView.as_view(), name='rating-detail'),
    
    # User profile and settings
    path('upload/', UploadVideoView.as_view(), name='upload-video'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('settings/', SettingsView.as_view(), name='settings'),
    
    # Static pages
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
]