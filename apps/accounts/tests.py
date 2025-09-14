from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='PATIENT'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'PATIENT')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str(self):
        expected = f"{self.user.get_full_name()} (PATIENT)"
        self.assertEqual(str(self.user), expected)

    def test_user_properties(self):
        self.assertTrue(self.user.is_patient)
        self.assertFalse(self.user.is_doctor)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_admin)


class UserAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.login_url = reverse('user-login')
        self.profile_url = reverse('user-profile')

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+1234567890',
            'role': 'PATIENT',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

    def test_user_login(self):
        User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_user_profile_requires_auth(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_authenticated(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
