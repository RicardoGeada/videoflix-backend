from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import GenreModel
from users.models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken

# Create your tests here.
class GenreAPITests(APITestCase):
    
    def setUp(self):
        self.genre_action = GenreModel.objects.create(name='Action')
        self.genre_comedy = GenreModel.objects.create(name='Comedy')
        
        self.user = CustomUser.objects.create_user(email='test@user.com', password='testpassword', is_active=True)
        
    def authenticate_user(self):
        """
        Helper function to authenticate the test user and set the JWT token in the request header.
        """
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_unauthorized_access(self):
        """
        Ensure unauthorized users don't receive access.
        """
        url = reverse('genre-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_genres(self):
        """
        Ensure authorized users receive all genres as a list.
        """
        self.authenticate_user()
        
        url = reverse('genre-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Action')
        self.assertEqual(response.data[1]['name'], 'Comedy')
        
        
    def test_get_genre_detail(self):
        """
        Ensure authorized users can retrieve a genre by id.
        """
        self.authenticate_user()
        
        url = reverse('genre-detail', args=[self.genre_action.id])
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.genre_action.name)