from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth import authenticate, login, logout
from .models import User, Video, Rating
from .serializers import UserSerializer, LoginSerializer, VideoSerializer, RatingSerializer
from rest_framework import serializers
from .forms import VideoUploadForm 
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.db.models import Q
import json

# User Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# User Registration View
class UserRegistrationView(View):
    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect("home")  # Redirect to home or a page for authenticated users
        return render(request, "register.html")

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        user_type = request.POST.get("user_type")

        # Validate password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, "register.html")

        try:
            # Create the user
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                user_type=user_type  # Using your custom user_type field
            )
            
            # Optionally log the user in after registration
            login(request, user)
            
            messages.success(request, "Account created successfully! You are now logged in.")
            return redirect("home")  # Redirect to the home page or any other page after registration

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "register.html")       


# User Login View
class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect("home")  # Replace 'home' with your desired redirect URL for logged-in users
        return render(request, "login.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "You have logged in successfully!")
                return redirect("home")  # Replace 'home' with the URL name for your homepage
            else:
                messages.error(request, "Your account is inactive. Please contact support.")
                return render(request, "login.html")
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, "login.html")


# User Logout View
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return redirect('home')


# List and Create Videos
class VideoListCreateView(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Assign the authenticated user as the creator
        serializer.save(creator=self.request.user)


# Retrieve, Update, and Delete a Video
class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


# List and Create Ratings
class RatingListCreateView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter ratings by video ID if provided
        video_id = self.request.query_params.get('video_id')
        if video_id:
            return Rating.objects.filter(video_id=video_id)
        return Rating.objects.all()

    def perform_create(self, serializer):
        # Assign the authenticated user to the rating
        serializer.save(user=self.request.user)


# Retrieve, Update, and Delete a Rating
class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


# HomePageView - Shows videos for authenticated and non-authenticated users
class HomePageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'home.html')

        videos = Video.objects.all().order_by('-upload_date')[:10]  
        for video in videos:
            video.likes_count = video.ratings.filter(rating__gte=4).count() 
            video.comments_count = video.ratings.count() 
        return render(request, 'home.html', {'videos': videos})


# VideoFeedView - Displays videos in the feed
class VideoFeedView(LoginRequiredMixin, View):
    def get(self, request, video_id=None):
        if video_id:
            try:
                video = Video.objects.get(id=video_id)
                videos = Video.objects.all().order_by('-upload_date')
                return render(request, 'feed.html', {'videos': videos, 'video': video})
            except Video.DoesNotExist:
                return render(request, '404.html') 
        else:
            videos = Video.objects.all().order_by('-upload_date')
            return render(request, 'feed.html', {'videos': videos})


# UploadVideoView - Handles video uploads
class UploadVideoView(LoginRequiredMixin, View):
    def get(self, request):
        form = VideoUploadForm()
        return render(request, 'upload_video.html', {'form': form})

    def post(self, request):
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.creator = request.user
            video.save()
            return redirect('home')  # Redirect to video feed after upload
        return render(request, 'upload_video.html', {'form': form})


# ProfileView - Displays user's profile
class ProfileView(View):
    def get(self, request):
        user = request.user
        return render(request, 'profile.html', {'user': user})


# SettingsView - Allows users to update settings
class SettingsView(View):
    def get(self, request):
        user = request.user
        return render(request, 'settings.html', {'user': user})

    def post(self, request):
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')

        user.username = username
        user.email = email
        user.user_type = user_type
        user.save()

        return redirect('profile') 


# AboutView - Displays about page
class AboutView(View):
    def get(self, request):
        return render(request, 'about.html')


# ContactView - Displays contact page and handles form submission
class ContactView(View):
    def get(self, request):
        return render(request, 'contact.html')

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        return render(request, 'contact_success.html', {'name': name})


# VideoLikeView - Handles video likes (rating 5)
class VideoLikeView(LoginRequiredMixin, View):
    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        rating, created = Rating.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'rating': 5}  # Assuming 5 is for likes
        )

        if not created:
            rating.delete()  # Toggle like if already liked
        
        likes_count = video.ratings.filter(rating=5).count()
        return JsonResponse({'likes_count': likes_count})


# VideoCommentView - Handles comments on videos
class VideoCommentView(LoginRequiredMixin, View):
    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        data = json.loads(request.body)

        rating, created = Rating.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'rating': 0}  # Default rating is 0
        )

        comment_text = data.get('text')
        if comment_text:
            rating.comment = comment_text
            rating.save()

        return JsonResponse({
            'id': rating.id,
            'text': rating.comment,
            'created_at': rating.upload_date.isoformat() if rating.upload_date else None,
            'user': {
                'username': rating.user.username,
                'avatar_url': rating.user.profile.avatar_url if hasattr(rating.user, 'profile') else None
            }
        })


# VideoSearchView - Handles searching of videos
class VideoSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        videos = Video.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
        data = [{
            'id': video.id,
            'title': video.title,
            'thumbnail': f"https://img.youtube.com/vi/{video.video_url[32:43]}/hqdefault.jpg"
        } for video in videos]
        return JsonResponse({'results': data})
