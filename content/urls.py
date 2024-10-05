from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreModelViewSet

router = DefaultRouter()
router.register(r'genres', GenreModelViewSet, basename='genre')

urlpatterns = [
    path('', include(router.urls))
]