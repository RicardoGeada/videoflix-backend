from rest_framework import serializers
from .models import GenreModel, VideoModel

class GenreModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenreModel
        fields = ['id', 'name']
        
        
class VideoModelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoModel
        fields = ['id', 'title', 'description', 'created_at', 'genres'] # thumbail
        

class VideoModelDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VideoModel
        fields = ['id', 'title', 'description', 'created_at', 'genres'] # thumbnail, video
        


