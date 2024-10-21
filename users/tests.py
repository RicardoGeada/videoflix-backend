from unittest.mock import patch
from django.test import TestCase

from users.tasks import send_activation_email, send_password_reset_email
from .models import CustomUser
from django.utils import timezone
from datetime import timedelta

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

# Create your tests here.
class CustomUserModelTest(TestCase):
    
    def test_user_model_exists(self):
        users = CustomUser.objects.count()
        self.assertEqual(users, 0)
        
    
    def test_user_can_be_created(self):
        new_user = CustomUser.objects.create_user(email='user@mail.com', password='password')
        self.assertEqual(new_user.email, 'user@mail.com')
        self.assertTrue(new_user.check_password('password'))
        self.assertEqual(new_user.first_name, '')
        self.assertEqual(new_user.last_name, '')
        self.assertEqual(new_user.phone, None)
        self.assertEqual(new_user.address, None)
        
        self.assertEqual(new_user.is_active, False)
        self.assertEqual(new_user.is_staff, False)
        self.assertEqual(new_user.is_superuser, False)

        now = timezone.now()
        self.assertLessEqual(new_user.date_joined, now)
        self.assertGreaterEqual(new_user.date_joined, now - timedelta(seconds=10))

    
    def test_super_user_can_be_created(self):
        new_user = CustomUser.objects.create_superuser(email='user@mail.com', password='password')
        self.assertEqual(new_user.email, 'user@mail.com')
        self.assertTrue(new_user.check_password('password'))
        self.assertEqual(new_user.first_name, '')
        self.assertEqual(new_user.last_name, '')
        self.assertEqual(new_user.phone, None)
        self.assertEqual(new_user.address, None)
        
        self.assertEqual(new_user.is_active, True)
        self.assertEqual(new_user.is_staff, True)
        self.assertEqual(new_user.is_superuser, True)

        now = timezone.now()
        self.assertLessEqual(new_user.date_joined, now)
        self.assertGreaterEqual(new_user.date_joined, now - timedelta(seconds=10))
        

class RegisterViewTests(APITestCase):
    
    @patch('django_rq.enqueue')  
    def test_register_new_user(self, mock_enqueue):
        """
        Ensure a new user can be registered and a confirmation email has been send.
        """
        url = reverse('register')
        data = {
            'email': 'newuser@mail.com',
            'password': 'newuserpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # check if user exists
        new_user = CustomUser.objects.filter(email=data['email']).first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.email, data['email'])
        self.assertTrue(new_user.check_password(data['password']))
        
        # account is not activated
        self.assertEqual(new_user.is_active, False)
        
        # check if django_rq.enqueue was called once with the correct arguments
        mock_enqueue.assert_called_once_with(send_activation_email, new_user)
        

class ActivationViewTests(APITestCase):
    
    def test_activate_user(self):
        """
        Ensure that the activation link activates the user.
        """
        # create new user
        new_user = CustomUser.objects.create_user(
            email='newuser@mail.com',
            password='newuserpassword',
            is_active=False
        )
        
        # generate uidb64 and token for activation link
        uidb64 = urlsafe_base64_encode(force_bytes(new_user.pk))
        token = default_token_generator.make_token(new_user)       
        activation_url = reverse('activate_account')
        data = {
            'uidb64': uidb64,
            'token': token,
        }
        
        response = self.client.post(activation_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)
        


class LoginViewTests(APITestCase):
    
    def setUp(self):
        self.activated_user=CustomUser.objects.create_user(email='activateduser@mail.com', password='activated', is_active=True)
        self.unactivated_user=CustomUser.objects.create_user(email='unactivateduser@mail.com', password='unactivated', is_active=False)
        
    
    def test_activated_user_can_login(self):
        """
        Ensure an activated user can login.
        """
        url = reverse('login')
        data = {
            'email' : self.activated_user.email,
            'password': 'activated'
        }
        response = self.client.post(url, data, format='json')
        
        # check for login success
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check for tokens in response
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        
        
    def test_unactivated_user_cant_login(self):
        """
        Ensure an unactivated user can't login.
        """
        url = reverse('login')
        data = {
            'email' : self.unactivated_user.email,
            'password': 'unactivated'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    
    
    # def test_access_token_authentification(self):
    #     """
    #     Ensure user can authenticate using the access token.
    #     """
    #     # login to get access token
    #     url = reverse('login')
    #     data = {
    #         'email' : self.activated_user.email,
    #         'password': 'activated'
    #     }
    #     response = self.client.post(url, data, format='json')
    #     access_token = response.data['access']
        
    #     # authenticate to protected view via access token
    #     protected_url = reverse('') # TODO: Insert protected view e.g. 'videos'
    #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    #     protected_response = self.client.get(protected_url)
        
    #     self.assertEqual(protected_response.status_code, status.HTTP_200_OK)
    
    
    def test_refresh_token_to_get_a_new_access_token(self):
        """
        Ensure user can use the refresh token to get a new access token.
        """
        # login to get a refresh token
        url = reverse('login')
        data = {
            'email' : self.activated_user.email,
            'password': 'activated'
        }
        response = self.client.post(url, data, format='json')
        
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
        # get a new access_token from the refresh token
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': refresh_token
        }
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
        self.assertNotEqual(access_token, refresh_response.data['access'])



class PasswordResetTests(APITestCase):
    
    def setUp(self):
        self.activated_user=CustomUser.objects.create_user(email='activateduser@mail.com', password='activated', is_active=True)
        self.unactivated_user=CustomUser.objects.create_user(email='unactivateduser@mail.com', password='unactivated', is_active=False)
        mail.outbox = [] # empty mailbox from activation email for unactivated_user
        
    
    # reset_password
    @patch('django_rq.enqueue')
    def test_email_with_password_reset_link_send(self, mock_queue):
        """
        Ensure a password reset link gets created.
        """
        url = reverse('password_reset')
        data = {
            'email' : self.activated_user.email,
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_queue.assert_called_once_with(send_password_reset_email, self.activated_user)
        
    @patch('django_rq.enqueue')
    def test_password_reset_with_non_existent_email(self, mock_queue):
        """
        Ensure that no error is raised when a non-existent email is provided.
        """
        url = reverse('password_reset')
        data = {
            'email': 'nonexistent@mail.com',
        }
        response = self.client.post(url, data, format='json')

        # no information for the user if the email exists
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # no email sent, because the user doesn't exist (no signal called)
        mock_queue.assert_not_called()
        
    
    # reset_password_confirm
    
    def test_password_reset_confirm_success(self):
        """
        Ensure the password reset confirm works with an apropriate link.
        """
        uidb64 = urlsafe_base64_encode(force_bytes(self.activated_user.pk))
        token = default_token_generator.make_token(self.activated_user) 
        
        url = reverse('password_reset_confirm')
        data = {
            'new_password': 'newpassword',
            'uidb64': uidb64, 
            'token': token,
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.activated_user.refresh_from_db()
        self.assertTrue(self.activated_user.check_password(data['new_password']))
        

    def test_password_reset_confirm_with_invalid_token(self):
        """
        Ensure password reset fails with an invalid token.
        """
        uidb64 = urlsafe_base64_encode(force_bytes(self.activated_user.pk))
        invalid_token = 'invalid-token'
        url = reverse('password_reset_confirm')
        data = {
            'new_password': 'newpassword',
            'uidb64': uidb64,
            'token': invalid_token,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_password_reset_confirm_with_invalid_uid(self):
        """
        Ensure password reset fails with an invalid uid.
        """
        invalid_uidb64 = 'invalid-uid'  # Setze eine ungültige UID
        token = default_token_generator.make_token(self.activated_user)
        url = reverse('password_reset_confirm')
        data = {
            'new_password': 'newpassword',
            'uidb64': invalid_uidb64,
            'token': token,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_password_reset_confirm_with_missing_data(self):
        """
        Ensure password reset fails when required data is missing.
        """
        uidb64 = urlsafe_base64_encode(force_bytes(self.activated_user.pk))
        token = default_token_generator.make_token(self.activated_user)

        url = reverse('password_reset_confirm')
        data = {
            # 'new_password' 
            'uidb64': uidb64,
            'token': token,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_password_reset_for_inactive_user(self):
        """
        Ensure password reset does not work for inactive users.
        """
        uidb64 = urlsafe_base64_encode(force_bytes(self.unactivated_user.pk))
        token = default_token_generator.make_token(self.unactivated_user)

        url = reverse('password_reset_confirm')
        data = {
            'new_password': 'newpassword',
            'uidb64': uidb64,
            'token': token,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class TasksTests(TestCase):
    
    def setUp(self):
        
        self.user=CustomUser.objects.create(email='test@user.com', password='password', is_active=False)
    
    def test_send_activation_email(self):
        """
        Ensure activation email gets send.
        """
        send_activation_email(self.user)
        self.assertEqual(len(mail.outbox),1)
        self.assertIn('Confirm your email', mail.outbox[0].subject)
        
        
    def test_send_password_reset_email(self):
        """
        Ensure password reset email gets send.
        """
        self.user.is_active = True; 
        send_password_reset_email(self.user)
        self.assertEqual(len(mail.outbox),1)
        self.assertIn('Reset your password', mail.outbox[0].subject)


