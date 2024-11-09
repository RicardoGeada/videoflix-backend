import os
from tempfile import TemporaryDirectory

from django.test import override_settings
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from content.tasks import convert_to_hls, create_master_playlist

from .models import GenreModel, VideoModel
from users.models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken

from urllib.parse import urlencode

from django.core.files import File

from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile


TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "media_test")


# Create your tests here.
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class GenreAPITests(APITestCase):

    def setUp(self):
        self.genre_action = GenreModel.objects.create(name="Action")
        self.genre_comedy = GenreModel.objects.create(name="Comedy")

        self.user = CustomUser.objects.create_user(
            email="test@user.com", password="testpassword", is_active=True
        )

    def authenticate_user(self):
        """
        Helper function to authenticate the test user and set the JWT token in the request header.
        """
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_unauthorized_access(self):
        """
        Ensure unauthorized users don't receive access.
        """
        url = reverse("genre-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_genres(self):
        """
        Ensure authorized users receive all genres as a list.
        """
        self.authenticate_user()

        url = reverse("genre-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Action")
        self.assertEqual(response.data[1]["name"], "Comedy")

    def test_get_genre_detail(self):
        """
        Ensure authorized users can retrieve a genre by id.
        """
        self.authenticate_user()

        url = reverse("genre-detail", args=[self.genre_action.id])
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.genre_action.name)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class VideoListAPITests(APITestCase):

    @mock.patch("django_rq.get_queue")
    def setUp(self, mock_queue):
        self.genre_action = GenreModel.objects.create(name="Action")
        self.genre_comedy = GenreModel.objects.create(name="Comedy")

        self.video_1 = VideoModel.objects.create(
            title="Video 1", description="Description 1"
        )
        self.video_1.genres.set([self.genre_action])
        self.video_2 = VideoModel.objects.create(
            title="Video 2", description="Description 2"
        )
        self.video_2.genres.set([self.genre_action])
        self.video_3 = VideoModel.objects.create(
            title="Video 3",
            description="Description 3",
            thumbnail_img=SimpleUploadedFile(
                "test_thumbnail.jpg", b"file_content", content_type="image/jpeg"
            ),
        )
        self.video_3.genres.set([self.genre_comedy])
        self.video_4 = VideoModel.objects.create(
            title="Video 4", description="Description 4"
        )
        self.video_4.genres.set([self.genre_comedy])
        self.video_5 = VideoModel.objects.create(
            title="Video 5", description="Description 5"
        )
        self.video_5.genres.set([self.genre_comedy])

        self.user = CustomUser.objects.create_user(
            email="test@user.com", password="testpassword", is_active=True
        )

    def authenticate_user(self):
        """
        Helper function to authenticate the test user and set the JWT token in the request header.
        """
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_unauthorized_access(self):
        """
        Ensure unauthorized users don't receive access.
        """
        url = reverse("video-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_videos(self):
        """
        Ensure authorized user receives all videos as a list.
        """
        self.authenticate_user()

        url = reverse("video-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

        # check thumbnail_url
        thumbnail_url = f"{response.wsgi_request.scheme}://{response.wsgi_request.get_host()}{settings.MEDIA_URL}videos/{self.video_3.id}/thumbnail.jpg"
        self.assertEqual(response.data[2]["thumbnail_url"], thumbnail_url)
        self.assertEqual(response.data[0]["thumbnail_url"], None)

    def test_get_genre_videos(self):
        """
        Ensure authorized user can filter for a specific genre.
        """
        self.authenticate_user()

        url = reverse("video-list")
        query_params = {"genre": self.genre_action.id}
        url_with_params = f"{url}?{urlencode(query_params)}"

        response = self.client.get(url_with_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_limit_offset_videos(self):
        """
        Ensure authorized user can filter by limit and offset.
        """
        self.authenticate_user()

        url = reverse("video-list")
        query_params = {"genre": self.genre_comedy.id, "offset": 1, "limit": 2}
        url_with_params = f"{url}?{urlencode(query_params)}"

        response = self.client.get(url_with_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["title"], "Video 4")
        self.assertEqual(response.data["results"][1]["title"], "Video 5")

    def tearDown(self):
        """Clean Up test data after test."""
        if os.path.exists(TEST_MEDIA_ROOT):
            for root, dirs, files in os.walk(TEST_MEDIA_ROOT, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    os.rmdir(dir_path)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class VideoDetailAPITests(APITestCase):

    @mock.patch("django_rq.get_queue")
    def setUp(self, mock_queue):

        self.genre_action = GenreModel.objects.create(name="Action")
        self.genre_comedy = GenreModel.objects.create(name="Comedy")

        self.video_1 = VideoModel.objects.create(
            title="Video 1", description="Description 1"
        )
        self.video_1.genres.set([self.genre_action])

        self.video_2 = VideoModel.objects.create(
            title="Video 2", description="Description 2"
        )
        self.video_2.genres.set([self.genre_action])

        self.video_3 = VideoModel.objects.create(
            title="Video 3",
            description="Description 3",
            video_file=SimpleUploadedFile(
                "test_video.mp4", b"file_content", content_type="video/mp4"
            ),
            thumbnail_img=SimpleUploadedFile(
                "test_thumbnail.jpg", b"file_content", content_type="image/jpeg"
            ),
        )
        self.video_3.genres.set([self.genre_comedy])

        self.video_4 = VideoModel.objects.create(
            title="Video 4", description="Description 4"
        )
        self.video_4.genres.set([self.genre_comedy])

        self.video_5 = VideoModel.objects.create(
            title="Video 5", description="Description 5"
        )
        self.video_5.genres.set([self.genre_comedy])

        self.user = CustomUser.objects.create_user(
            email="test@user.com", password="testpassword", is_active=True
        )

    def authenticate_user(self):
        """
        Helper function to authenticate the test user and set the JWT token in the request header.
        """
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_unauthorized_access(self):
        """
        Ensure unauthorized users don't receive access.
        """
        url = reverse("video-detail", kwargs={"pk": self.video_3.pk})
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_video_detail(self):
        """
        Ensure authorized users can retrieve specific videos by id.
        """
        self.authenticate_user()

        url = reverse("video-detail", kwargs={"pk": self.video_3.pk})
        response = self.client.get(url, format="json")

        video_url = f"{response.wsgi_request.scheme}://{response.wsgi_request.get_host()}/api/videos/{self.video_3.id}/stream/"
        thumbnail_url = f"{response.wsgi_request.scheme}://{response.wsgi_request.get_host()}{settings.MEDIA_URL}videos/{self.video_3.id}/thumbnail.jpg"

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.video_3.title)
        self.assertEqual(response.data["description"], self.video_3.description)
        self.assertEqual(response.data["genres"], [2])
        self.assertEqual(response.data["video_url"], video_url)
        self.assertEqual(response.data["thumbnail_url"], thumbnail_url)

    def tearDown(self):
        """Clean Up test data after test."""
        if os.path.exists(TEST_MEDIA_ROOT):
            for root, dirs, files in os.walk(TEST_MEDIA_ROOT, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    os.rmdir(dir_path)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class VideoStreamAPITests(APITestCase):

    @mock.patch("django_rq.get_queue")
    def setUp(self, mock_queue):

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        self.user = CustomUser.objects.create_user(
            email="test@user.com", password="testpassword", is_active=True
        )
        self.genre_action = GenreModel.objects.create(name="Action")

        test_video_path = "media/test_assets/test_video_1.mp4"

        with open(test_video_path, "rb") as video_file:
            self.video_1 = VideoModel.objects.create(
                title="Video 1",
                description="Description 1",
                video_file=File(video_file, name="test_video_1.mp4"),
            )

        self.video_1.genres.set([self.genre_action])

        # create master playlist file manuel
        create_master_playlist(self.video_1)

    def authenticate_user(self):
        """
        Helper function to authenticate the test user and set the JWT token in the request header.
        """
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    # TODO: Add token-based authentication to media URLs for secure access
    # def test_unauthorized_access(self):
    #     """
    #     Ensure unauthorized users don't receive access.
    #     """
    #     url = reverse('video-stream', kwargs={'pk': self.video_1.pk})
    #     response = self.client.get(url)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_non_existing_video(self):
        """
        Ensure if the video doesn't exist error code 404 will be send as response.
        """
        self.authenticate_user()

        url = reverse("video-stream", kwargs={"pk": 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_video_stream(self):
        """
        Ensure authorized users can retrieve specific videos by id.
        """
        self.authenticate_user()

        url = reverse("video-stream", kwargs={"pk": self.video_1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/vnd.apple.mpegurl")

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
        streaming_content = b"".join(response.streaming_content).decode("utf-8")
        actual_playlist_content = streaming_content.splitlines()
        self.assertEqual(expected_playlist_content, actual_playlist_content)

    def tearDown(self):
        """Clean Up test data after test."""
        if os.path.exists(TEST_MEDIA_ROOT):
            for root, dirs, files in os.walk(TEST_MEDIA_ROOT, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    os.rmdir(dir_path)


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class VideoSegmentAPITests(APITestCase):

    @mock.patch("django_rq.get_queue")
    def setUp(self, mock_queue):

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        self.user = CustomUser.objects.create_user(
            email="test@user.com", password="testpassword", is_active=True
        )
        self.genre_action = GenreModel.objects.create(name="Action")

        # set up test video
        test_video_path = "media/test_assets/test_video_1.mp4"
        with open(test_video_path, "rb") as video_file:
            self.video_1 = VideoModel.objects.create(
                title="Video 1",
                description="Description 1",
                video_file=File(video_file, name="test_video_1.mp4"),
            )
        self.video_1.genres.set([self.genre_action])

        self.create_mock_files(self.video_1, resolution="480")
         
    
    def create_mock_files(self, video_instance, resolution="480"):
        """
        Create a mock m3u8 file and a mock .ts file for the video.
        """
        video_folder = os.path.join(settings.MEDIA_ROOT, 'videos', str(video_instance.pk))
        os.makedirs(video_folder, exist_ok=True)

        self.create_mock_m3u8_file(video_folder, video_instance.title, resolution)
        self.create_mock_ts_file(video_folder, video_instance.title, resolution)
        
    
    def create_mock_m3u8_file(self, folder, title, resolution):
        """
        Create a mock m3u8 file.
        """
        m3u8_content = "\n".join([
            "#EXTM3U",
            "#EXT-X-VERSION:3",
            "#EXT-X-TARGETDURATION:17",
            "#EXT-X-MEDIA-SEQUENCE:0",
            "#EXTINF:16.683333,",
            f"{title.lower().replace(' ', '_')}_{resolution}p0.ts",
            "#EXTINF:8.341667,",
            f"{title.lower().replace(' ', '_')}_{resolution}p1.ts",
            "#EXTINF:7.474133,",
            f"{title.lower().replace(' ', '_')}_{resolution}p2.ts",
            "#EXTINF:12.746067,",
            f"{title.lower().replace(' ', '_')}_{resolution}p3.ts",
            "#EXTINF:6.506500,",
            f"{title.lower().replace(' ', '_')}_{resolution}p4.ts",
            "#EXTINF:5.972633,",
            f"{title.lower().replace(' ', '_')}_{resolution}p5.ts",
            "#EXT-X-ENDLIST",
        ])
        m3u8_path = os.path.join(folder, f"{title.lower().replace(' ', '_')}_{resolution}p.m3u8")
        with open(m3u8_path, "w") as f:
            f.write(m3u8_content)
            

    def create_mock_ts_file(self, folder, title, resolution):
        """
        Create a mock .ts file.
        """
        ts_path = os.path.join(folder, f"{title.lower().replace(' ', '_')}_{resolution}p0.ts")
        with open(ts_path, "wb") as ts_file:
            ts_file.write(b'\x00' * 1024) 
    
    

    def test_get_m3u8_file(self):
        """
        Ensure users can retrieve specific m3u8 video file by id.
        """
        url = reverse(
            "video-segment",
            kwargs={"pk": self.video_1.id, "filename": "video_1_480p.m3u8"},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/vnd.apple.mpegurl")

        expected_lines_start = [
            "#EXTM3U",
            "#EXT-X-VERSION:3",
            "#EXT-X-TARGETDURATION",
            "#EXTINF",
            "#EXT-X-ENDLIST",
        ]

        streaming_content = b"".join(response.streaming_content).decode("utf-8")
        actual_playlist_content = streaming_content.splitlines()

        # Check if each expected line start exists in actual playlist content
        for expected_start in expected_lines_start:
            found = any(line.startswith(expected_start) for line in actual_playlist_content)
            self.assertTrue(found, f"'{expected_start}' not found in playlist content")
            
            

    def test_get_ts_file(self):
        """
        Test for retrieving specific TS segment file by ID.
        """
        url = reverse(
            "video-segment",
            kwargs={"pk": self.video_1.id, "filename": "video_1_480p0.ts"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "video/MP2T")

