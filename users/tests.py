from django.test import TestCase
from .models import CustomUser
from django.utils import timezone
from datetime import timedelta

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
        self.assertLessEqual(new_user.created_at, now)
        self.assertGreaterEqual(new_user.created_at, now - timedelta(seconds=10))

    
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
        self.assertLessEqual(new_user.created_at, now)
        self.assertGreaterEqual(new_user.created_at, now - timedelta(seconds=10))