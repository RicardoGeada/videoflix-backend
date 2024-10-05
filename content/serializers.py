from rest_framework import serializers
from .models import GenreModel

class GenreModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenreModel
        fields = ['id', 'name']
        