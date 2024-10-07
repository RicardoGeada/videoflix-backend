from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreModelViewSet, VideoModelListView

router = DefaultRouter()
router.register(r'genres', GenreModelViewSet, basename='genre')

urlpatterns = [
    path('', include(router.urls)),
    path('videos/', VideoModelListView.as_view(), name='video-list')
]