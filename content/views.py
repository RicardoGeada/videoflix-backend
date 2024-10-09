import os
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from .models import GenreModel, VideoModel
from .serializers import GenreModelSerializer, VideoModelDetailSerializer, VideoModelListSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from django.http import FileResponse, Http404

# Create your views here.
class GenreModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GenreModel.objects.all()
    serializer_class = GenreModelSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    
class VideoModelListView(ListAPIView):
    queryset = VideoModel.objects.all()
    serializer_class = VideoModelListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genres']
    
    def get_queryset(self):
        """
        Overwrite the standard query to filter for specific genres.
        """
        queryset = VideoModel.objects.all()

        genre = self.request.query_params.get('genre', None)
        if genre:
            queryset = queryset.filter(genres__id=genre)

        return queryset


class VideoModelDetailView(RetrieveAPIView):
    queryset = VideoModel.objects.all()
    serializer_class = VideoModelDetailSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    

class VideoStreamView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, pk, format=None):
        video = get_object_or_404(VideoModel, id=pk)
        
        master_playlist_path = f'media/videos/{video.id}/master.m3u8'
        
        if not os.path.exists(master_playlist_path):
            raise Http404("Video stream not found")
        
        response = FileResponse(open(master_playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')
        response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
        
        return response