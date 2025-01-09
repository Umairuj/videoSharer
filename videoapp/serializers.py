from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Video, Rating


# Serializer for user registration
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'password')
        extra_kwargs = {
            'password': {'write_only': True} 
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


# Serializer for login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid username or password")


# Serializer for video data
class VideoSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'tags', 'upload_date', 
            'creator', 'file_url', 'thumbnail_url', 'views', 'likes'
        ]


# Serializer for ratings
class RatingSerializer(serializers.ModelSerializer):
    video = serializers.ReadOnlyField(source='video.title')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Rating
        fields = ['id', 'video', 'user', 'rating', 'comment', 'created_at']
