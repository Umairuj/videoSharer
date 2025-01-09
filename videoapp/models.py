from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        return self.create_user(email, username, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):  # Add PermissionsMixin here
    USER_TYPES = [('creator', 'Creator'), ('consumer', 'Consumer'), ('admin', 'Admin')]  # Added 'admin' choice
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)  # Required for Admin access
    is_active = models.BooleanField(default=True)  # Required for active status
    is_superuser = models.BooleanField(default=False)  # Needed for superuser

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = ['username', 'user_type']  # Additional fields required when creating a user

    def __str__(self):
        return self.username


class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)
    tags = models.TextField()  # Could be a ManyToMany if tags are separate entities
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="videos")
    video_url = models.URLField(null=True)  # Store the video URL instead of a file

    def __str__(self):
        return self.title

class Rating(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField(blank=True, null=True)
