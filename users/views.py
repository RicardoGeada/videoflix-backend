from django.shortcuts import render

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import  AllowAny

from .serializers import RegisterSerializer

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser

# Create your views here.
class RegisterView(CreateAPIView):
    """
    View for user registration.

    Provides an endpoint for creating new user accounts.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    


class ActivateAccount(APIView):
    def post(self, request, uidb64, token):
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)