from rest_framework import serializers
from .models import GenreModel, VideoModel

class GenreModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenreModel
        fields = ['id', 'name']
        
        
class VideoModelListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VideoModel
        fields = ['id', 'title', 'description', 'created_at', 'genres'] # thumbnail
        

class VideoModelDetailSerializer(serializers.ModelSerializer):
    
    video_url = serializers.SerializerMethodField()
    class Meta:
        model = VideoModel
        fields = ['id', 'title', 'description', 'created_at', 'genres', 'video_url'] # thumbnail, video
        
    def get_video_url(self, obj):
        """
        Provides url for video stream api endpoint.
        """
        request = self.context.get('request')
        if obj.video_file:
            video_url = f"{request.scheme}://{request.get_host()}/api/videos/{obj.id}/stream/"
            return video_url
        return None
