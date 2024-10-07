from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import GenreModel, VideoModel
from users.models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken

from urllib.parse import urlencode

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


class VideoListAPITests(APITestCase):
    
    def setUp(self):
        self.genre_action = GenreModel.objects.create(name='Action')
        self.genre_comedy = GenreModel.objects.create(name='Comedy')
        
        self.video_1 = VideoModel.objects.create(title='Video 1', description='Description 1')
        self.video_1.genres.set([self.genre_action])
        self.video_2 = VideoModel.objects.create(title='Video 2', description='Description 2')
        self.video_2.genres.set([self.genre_action])
        self.video_3 = VideoModel.objects.create(title='Video 3', description='Description 3')
        self.video_3.genres.set([self.genre_comedy])
        self.video_4 = VideoModel.objects.create(title='Video 4', description='Description 4')
        self.video_4.genres.set([self.genre_comedy])
        self.video_5 = VideoModel.objects.create(title='Video 5', description='Description 5')
        self.video_5.genres.set([self.genre_comedy])
        
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
        url = reverse('video-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    


    def test_get_videos(self):
        """
        Ensure authorized user receives all videos as a list.
        """
        self.authenticate_user()
        
        url = reverse('video-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        
        
        
    def test_get_genre_videos(self):
        """
        Ensure authorized user can filter for a specific genre.
        """
        self.authenticate_user()
        
        url = reverse('video-list')
        query_params = {'genre': self.genre_action.id}
        url_with_params = f"{url}?{urlencode(query_params)}"
        
        response = self.client.get(url_with_params, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    
    
    def test_limit_offset_videos(self):
        """
        Ensure authorized user can filter by limit and offset.
        """
        self.authenticate_user()
        
        url = reverse('video-list')
        query_params = {'genre': self.genre_comedy.id,'offset': 1,'limit': 2}
        url_with_params = f"{url}?{urlencode(query_params)}"
        
        response = self.client.get(url_with_params, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], 'Video 4')
        self.assertEqual(response.data['results'][1]['title'], 'Video 5')
        
        
class VideoDetailAPITests(APITestCase):
    
    def setUp(self):
        self.genre_action = GenreModel.objects.create(name='Action')
        self.genre_comedy = GenreModel.objects.create(name='Comedy')
        
        self.video_1 = VideoModel.objects.create(title='Video 1', description='Description 1')
        self.video_1.genres.set([self.genre_action])
        self.video_2 = VideoModel.objects.create(title='Video 2', description='Description 2')
        self.video_2.genres.set([self.genre_action])
        self.video_3 = VideoModel.objects.create(title='Video 3', description='Description 3')
        self.video_3.genres.set([self.genre_comedy])
        self.video_4 = VideoModel.objects.create(title='Video 4', description='Description 4')
        self.video_4.genres.set([self.genre_comedy])
        self.video_5 = VideoModel.objects.create(title='Video 5', description='Description 5')
        self.video_5.genres.set([self.genre_comedy])
        
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
        url = reverse('video-detail', kwargs={'pk': self.video_3.pk})
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    
    
    def test_get_video_detail(self):
        """
        Ensure authorized users can retrieve specific videos by id.
        """
        self.authenticate_user()
        
        url = reverse('video-detail', kwargs={'pk': self.video_3.pk})
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.video_3.title)
        self.assertEqual(response.data['description'], self.video_3.description)
        self.assertEqual(response.data['genres'], [2])