from django.shortcuts import render

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import  AllowAny

from .serializers import RegisterSerializer

# Create your views here.
class RegisterView(CreateAPIView):
    """
    View for user registration.

    Provides an endpoint for creating new user accounts.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]