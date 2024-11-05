import os
import random
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
from django.http import FileResponse, Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from rest_framework.response import Response

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# Create your views here.
@method_decorator(cache_page(CACHE_TTL), name='list')
@method_decorator(cache_page(CACHE_TTL), name='retrieve')
class GenreModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GenreModel.objects.all()
    serializer_class = GenreModelSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
@method_decorator(cache_page(CACHE_TTL), name='get')
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

@method_decorator(cache_page(CACHE_TTL), name='get')
class VideoModelDetailView(RetrieveAPIView):
    queryset = VideoModel.objects.all()
    serializer_class = VideoModelDetailSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
# TODO: Add token-based authentication to media URLs for secure access
@method_decorator(cache_page(CACHE_TTL), name='get')
class VideoStreamView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    
    def get(self, request, pk, format=None):
        video = get_object_or_404(VideoModel, id=pk)
        
        master_playlist_path = f'media/videos/{video.id}/master.m3u8'
        
        if not os.path.exists(master_playlist_path):
            raise Http404("Video stream not found")
        
        response = FileResponse(open(master_playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')
        response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
        
        return response
    

class VideoSegmentView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    def get(self, request, pk, filename, format=None):
        video = get_object_or_404(VideoModel, id=pk)
        segment_path = f'media/videos/{video.id}/{filename}'

        if filename.endswith(".m3u8"):
            content_type = 'application/vnd.apple.mpegurl'
        elif filename.endswith(".ts"):
            content_type = 'video/MP2T'
        else:
            raise Http404("Unsupported file type")

        response = FileResponse(open(segment_path, 'rb'), content_type=content_type)
        response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
        
        return response
    
    

class BillboardVideoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, *args, **kwargs):
        # get the 10 newest videos
        pks = VideoModel.objects.order_by('-created_at').values_list('pk', flat=True)[:10]
        # choose one random
        random_pk = random.choice(pks)
        random_video = VideoModel.objects.get(pk=random_pk)
        
        serializer = VideoModelDetailSerializer(random_video, context={'request': request})
        return Response(serializer.data)