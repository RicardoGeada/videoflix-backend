from django.test import TestCase
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
    
    def test_register_new_user(self):
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
        
        # check if confirmation email send
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Confirm your email', mail.outbox[0].subject)
        

class ActivationViewTest(APITestCase):
    
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
        activation_url = reverse('activate_account', kwargs={'uidb64': uidb64, 'token': token})
        
        response = self.client.post(activation_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)