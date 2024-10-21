import os
import shutil

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

import content

from .models import GenreModel, VideoModel
from users.models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken

from urllib.parse import urlencode

from django.core.files import File

from unittest import mock

from PIL import Image
import io

from django.core.files.uploadedfile import SimpleUploadedFile

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
        self.video_3 = VideoModel.objects.create(title='Video 3', description='Description 3', thumbnail_img=SimpleUploadedFile("test_thumbnail.jpg", b"file_content", content_type="image/jpeg"))
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
        
        # check thumbnail_url
        thumbnail_url = f"{response.wsgi_request.scheme}://{response.wsgi_request.get_host()}/api/videos/{self.video_3.id}/thumbnail/"
        self.assertEqual(response.data[2]['thumbnail_url'], thumbnail_url)
        self.assertEqual(response.data[0]['thumbnail_url'], None)
        
        
        
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
        
        
    
    def tearDown(self):
      """Clean Up test data after test."""
      if self.video_3:
          if os.path.exists(self.video_3.thumbnail_img.path):
              os.remove(self.video_3.thumbnail_img.path)
          shutil.rmtree(os.path.dirname(self.video_3.thumbnail_img.path), ignore_errors=True)
        
        
class VideoDetailAPITests(APITestCase):
    
    # @mock.patch('content.signals.delete_file')
    # @mock.patch('content.signals.convert_to_hls')
    # def setUp(self, mock_convert, mock_delete_file):
    #     self.genre_action = GenreModel.objects.create(name='Action')
    #     self.genre_comedy = GenreModel.objects.create(name='Comedy')
        
    #     self.video_1 = VideoModel.objects.create(title='Video 1', description='Description 1')
    #     self.video_1.genres.set([self.genre_action])
    #     self.video_2 = VideoModel.objects.create(title='Video 2', description='Description 2')
    #     self.video_2.genres.set([self.genre_action])
    #     self.video_3 = VideoModel.objects.create(title='Video 3', description='Description 3', video_file=SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4"), thumbnail_img=SimpleUploadedFile("test_thumbnail.jpg", b"file_content", content_type="image/jpeg"))
    #     self.video_3.genres.set([self.genre_comedy])
    #     self.video_4 = VideoModel.objects.create(title='Video 4', description='Description 4')
    #     self.video_4.genres.set([self.genre_comedy])
    #     self.video_5 = VideoModel.objects.create(title='Video 5', description='Description 5')
    #     self.video_5.genres.set([self.genre_comedy])
        
    #     self.user = CustomUser.objects.create_user(email='test@user.com', password='testpassword', is_active=True)
    
    
    def setUp(self):
        # Verwende patch.object für spezifischere Mocks
        self.mock_convert = mock.patch.object(content.signals, 'convert_to_hls', autospec=True).start()
        self.mock_delete_file = mock.patch.object(content.signals, 'delete_file', autospec=True).start()
        
        # Sicherstellen, dass die Patches nach dem Test gestoppt werden
        self.addCleanup(mock.patch.stopall)

        # Erstelle deine Testdaten wie zuvor
        self.genre_action = GenreModel.objects.create(name='Action')
        self.genre_comedy = GenreModel.objects.create(name='Comedy')

        self.video_1 = VideoModel.objects.create(title='Video 1', description='Description 1')
        self.video_1.genres.set([self.genre_action])

        self.video_2 = VideoModel.objects.create(title='Video 2', description='Description 2')
        self.video_2.genres.set([self.genre_action])

        self.video_3 = VideoModel.objects.create(
            title='Video 3', 
            description='Description 3', 
            video_file=SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4"), 
            thumbnail_img=SimpleUploadedFile("test_thumbnail.jpg", b"file_content", content_type="image/jpeg")
        )
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
        
        video_url = f"{response.wsgi_request.scheme}://{response.wsgi_request.get_host()}/api/videos/{self.video_3.id}/stream/"
        thumbnail_url = f"{response.wsgi_request.scheme}://{response.wsgi_request.get_host()}/api/videos/{self.video_3.id}/thumbnail/"
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.video_3.title)
        self.assertEqual(response.data['description'], self.video_3.description)
        self.assertEqual(response.data['genres'], [2])
        self.assertEqual(response.data['video_url'], video_url)
        self.assertEqual(response.data['thumbnail_url'], thumbnail_url)
        
        
        
    def tearDown(self):
        """Clean Up test data after test."""
        if self.video_3:
            if os.path.exists(self.video_3.video_file.path):
                os.remove(self.video_3.video_file.path)
            shutil.rmtree(os.path.dirname(self.video_3.video_file.path), ignore_errors=True)
        

class VideoStreamAPITests(APITestCase):
    
    @mock.patch('content.signals.delete_file')
    @mock.patch('content.signals.convert_to_hls')
    def setUp(self, mock_convert, mock_delete_file):
        
        self.user = CustomUser.objects.create_user(email='test@user.com', password='testpassword', is_active=True)
        self.genre_action = GenreModel.objects.create(name='Action')
        
        test_video_path = 'media/test_assets/test_video_1.mp4'
        
        with open(test_video_path, 'rb') as video_file:
            self.video_1 = VideoModel.objects.create(
                title='Video 1',
                description='Description 1',
                video_file=File(video_file, name='test_video_1.mp4')
            )
        
        self.video_1.genres.set([self.genre_action])
        
        
        
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
        url = reverse('video-stream', kwargs={'pk': self.video_1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        

    def test_get_non_existing_video(self):
        """
        Ensure if the video doesn't exist error code 404 will be send as response.
        """
        self.authenticate_user()
        
        url = reverse('video-stream', kwargs={'pk': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        
        
    def test_get_video_stream(self):
        """
        Ensure authorized users can retrieve specific videos by id.
        """
        self.authenticate_user()
        
        url = reverse('video-stream', kwargs={'pk': self.video_1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.apple.mpegurl')
        
        clean_title = self.video_1.title.replace(" ", "_").lower()
        expected_playlist_content = [
            "#EXTM3U",
            "#EXT-X-VERSION:3",
            "#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360",
            f"{clean_title}_480p.m3u8",
            "#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=1280x720",
            f"{clean_title}_720p.m3u8",
            "#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1920x1080",
            f"{clean_title}_1080p.m3u8",
        ]
        streaming_content = b''.join(response.streaming_content).decode('utf-8')
        actual_playlist_content = streaming_content.splitlines()
        self.assertEqual(expected_playlist_content, actual_playlist_content)


        
    def tearDown(self):
        """Clean Up test data after test."""
        if self.video_1:
            if os.path.exists(self.video_1.video_file.path):
                os.remove(self.video_1.video_file.path)
            shutil.rmtree(os.path.dirname(self.video_1.video_file.path), ignore_errors=True)
            
            
class VideoThumbnailAPITests(APITestCase):
    
    @mock.patch('content.signals.delete_file')
    @mock.patch('content.signals.convert_to_hls')
    def setUp(self, mock_convert, mock_delete_file):
        
        self.user = CustomUser.objects.create_user(email='test@user.com', password='testpassword', is_active=True)
        self.genre_action = GenreModel.objects.create(name='Action')
        
        test_thumbnail_img_path = 'media/test_assets/test_thumbnail.jpg'
        
        with open(test_thumbnail_img_path, 'rb') as thumbnail_img:
            self.video_1 = VideoModel.objects.create(
                title='Video 1',
                description='Description 1',
                thumbnail_img=File(thumbnail_img, name='test_thumbnail.jpg')
            )
        
        self.video_1.genres.set([self.genre_action])
        
        
        
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
        url = reverse('video-thumbnail', kwargs={'pk': self.video_1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
        
    def test_get_non_existing_thumbnail(self):
        """
        Ensure if the thumbnail doesn't exist error code 404 will be send as response.
        """
        self.authenticate_user()
        
        url = reverse('video-thumbnail', kwargs={'pk': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        
        
    def test_get_video_thumbnails(self):
        """
        Ensure authorized users can retrieve specific thumbnails by id.
        """
        self.authenticate_user()
        
        url = reverse('video-thumbnail', kwargs={'pk': self.video_1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        
        image_data = response.content
        response_bytes = io.BytesIO(image_data) # create BytesIO-object
        response_image = Image.open(response_bytes) # open image with PIL
        
        with open(self.video_1.thumbnail_img.path, 'rb') as f:
            expected_image_data = f.read()  # read image data
            expected_image_bytes = io.BytesIO(expected_image_data)  # create BytesIO-object
            expected_image = Image.open(expected_image_bytes) # open image with PIL
        
        # compare response image and thumbnail image
        self.assertEqual(list(response_image.getdata()), list(expected_image.getdata()))

        
    def tearDown(self):
        """Clean Up test data after test."""
        if self.video_1:
            if os.path.exists(self.video_1.thumbnail_img.path):
                os.remove(self.video_1.thumbnail_img.path)
            shutil.rmtree(os.path.dirname(self.video_1.thumbnail_img.path), ignore_errors=True)
        