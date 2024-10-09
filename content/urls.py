from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreModelViewSet, VideoModelListView, VideoModelDetailView, VideoStreamView, VideoThumbnailView

router = DefaultRouter()
router.register(r'genres', GenreModelViewSet, basename='genre')

urlpatterns = [
    path('', include(router.urls)),
    path('videos/', VideoModelListView.as_view(), name='video-list'),
    path('videos/<int:pk>/', VideoModelDetailView.as_view(), name='video-detail'),
    path('videos/<int:pk>/stream/', VideoStreamView.as_view(), name='video-stream'),
    path('videos/<int:pk>/thumbnail/', VideoThumbnailView.as_view(), name='video-thumbnail'),
]