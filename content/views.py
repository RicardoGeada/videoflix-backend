from rest_framework import viewsets
from .models import GenreModel
from .serializers import GenreModelSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.
class GenreModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GenreModel.objects.all()
    serializer_class = GenreModelSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
