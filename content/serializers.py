from django.conf import settings
from rest_framework import serializers
from .models import GenreModel, VideoModel

class GenreModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenreModel
        fields = ['id', 'name']
        
        
class VideoModelListSerializer(serializers.ModelSerializer):
    
    thumbnail_url = serializers.SerializerMethodField()
    class Meta:
        model = VideoModel
        fields = ['id', 'title', 'description', 'created_at', 'genres', 'thumbnail_url']
        
    def get_thumbnail_url(self, obj):
        """
        Provides url for video thumbnail.
        """
        request = self.context.get('request')
        if obj.thumbnail_img:
            thumbnail_url = f"{request.scheme}://{request.get_host()}{settings.MEDIA_URL}videos/{obj.id}/thumbnail.jpg"
            return thumbnail_url
        return None

class VideoModelDetailSerializer(serializers.ModelSerializer):
    
    thumbnail_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    class Meta:
        model = VideoModel
        fields = ['id', 'title', 'description', 'created_at', 'genres', 'thumbnail_url', 'video_url']
        
    def get_video_url(self, obj):
        """
        Provides url for video stream api endpoint.
        """
        request = self.context.get('request')
        if obj.video_file:
            video_url = f"{request.scheme}://{request.get_host()}/api/videos/{obj.id}/stream/"
            return video_url
        return None
    
    def get_thumbnail_url(self, obj):
        """
        Provides url for video thumbnail.
        """
        request = self.context.get('request')
        if obj.thumbnail_img:
            thumbnail_url = f"{request.scheme}://{request.get_host()}{settings.MEDIA_URL}videos/{obj.id}/thumbnail.jpg"
            return thumbnail_url
        return None
