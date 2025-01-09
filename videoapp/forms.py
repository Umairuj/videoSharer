from django import forms
from .models import Video

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'tags', 'video_url']  

    # You can add custom validations if needed for the URL
    def clean_video_url(self):
        video_url = self.cleaned_data.get('video_url')
        if not video_url:
            raise forms.ValidationError("This field is required.")
        # You could add further validation to check if the URL points to a video format
        return video_url
