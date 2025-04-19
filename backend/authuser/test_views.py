from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from authuser.models import PhoneOTP
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password

User = get_user_model()

class AuthTestCase(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone_number='1234567890',
            name='Test User',
            is_phone_verified=True
        )
        self.token = Token.objects.create(user=self.test_user)

    def test_logout_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful. Your session has been securely ended.')

    def test_pre_register_user(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "confirm_password": "newpass123",
            "phone_number": "9999999999",
            "name": "New User"
        }
        response = self.client.post(reverse('pre_register'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'OTP has been sent to your email address.')

    def test_verify_and_register_user(self):
        # Create a temporary user
        temp_user = User.objects.create(
            username="verifyuser",
            email="verifyuser@example.com",
            phone_number="8888888888",
            name="Verify User",
            password=make_password("testpass123"),
            is_phone_verified=False
        )
        # Create PhoneOTP record
        PhoneOTP.objects.create(
            user=temp_user,
            otp="123456",
            is_verified=False
        )

        data = {
            "email": "verifyuser@example.com",
            "otp": "123456"
        }
        response = self.client.post(reverse('verify_register'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Your account has been successfully created and verified.')

    def test_login_user(self):
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['message'], 'Login successful.')

    def test_current_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(reverse('current_user'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.test_user.username)

    def test_password_reset_request(self):
        data = {"email": self.test_user.email}
        response = self.client.post(reverse('password_reset_request'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset link sent to your email.')

    def test_password_reset_confirm(self):
        uid = urlsafe_base64_encode(force_bytes(self.test_user.pk))
        token = default_token_generator.make_token(self.test_user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        data = {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password has been reset successfully.')