"""
Test cases for Authentication API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json


User = get_user_model()

class AuthenticationAPITestCase(APITestCase):
    """Test cases for authentication endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.registration_url = reverse('api:auth-register')
        self.login_url = reverse('api:auth-login')
        self.token_url = reverse('api:token_obtain_pair')
        self.refresh_url = reverse('api:token_refresh')
        self.profile_url = reverse('api:auth-profile')
        self.change_password_url = reverse('api:auth-change-password')
        self.logout_url = reverse('api:auth-logout')
        self.status_url = reverse('api:auth-status')
        
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        # Create a test user
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpass123',
            first_name='Existing',
            last_name='User'
        )
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.registration_url, self.test_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('message', response.data)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Check response structure
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['username'], 'testuser')
        
    def test_user_registration_validation_errors(self):
        """Test registration with validation errors"""
        
        # Test missing required fields
        response = self.client.post(self.registration_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test password mismatch
        invalid_data = self.test_user_data.copy()
        invalid_data['password_confirm'] = 'wrongpass'
        response = self.client.post(self.registration_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test duplicate username
        invalid_data = self.test_user_data.copy()
        invalid_data['username'] = 'existinguser'
        response = self.client.post(self.registration_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test duplicate email
        invalid_data = self.test_user_data.copy()
        invalid_data['email'] = 'existing@example.com'
        response = self.client.post(self.registration_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_success(self):
        """Test successful user login"""
        login_data = {
            'username': 'existinguser',
            'password': 'existingpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['user']['username'], 'existinguser')
    
    def test_user_login_with_email(self):
        """Test login with email instead of username"""
        login_data = {
            'username': 'existing@example.com',  # Using email as username
            'password': 'existingpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'existinguser')
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'existinguser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_jwt_token_obtain(self):
        """Test JWT token obtain"""
        token_data = {
            'username': 'existinguser',
            'password': 'existingpass123'
        }
        
        response = self.client.post(self.token_url, token_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh"""
        # Get initial tokens
        refresh = RefreshToken.for_user(self.user)
        
        refresh_data = {
            'refresh': str(refresh)
        }
        
        response = self.client.post(self.refresh_url, refresh_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_user_profile_get(self):
        """Test getting user profile"""
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'existinguser')
        self.assertEqual(response.data['email'], 'existing@example.com')
    
    def test_user_profile_update(self):
        """Test updating user profile"""
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        self.assertEqual(response.data['email'], 'updated@example.com')
        
        # Verify user was updated in database
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.email, 'updated@example.com')
    
    def test_change_password(self):
        """Test changing user password"""
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        password_data = {
            'old_password': 'existingpass123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        response = self.client.post(self.change_password_url, password_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify password was changed
        updated_user = User.objects.get(id=self.user.id)
        self.assertTrue(updated_user.check_password('newpassword123'))
    
    def test_change_password_invalid_old_password(self):
        """Test changing password with invalid old password"""
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        password_data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        response = self.client.post(self.change_password_url, password_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout(self):
        """Test user logout"""
        # Get tokens
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        logout_data = {
            'refresh_token': str(refresh)
        }
        
        response = self.client.post(self.logout_url, logout_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_auth_status_authenticated(self):
        """Test authentication status for authenticated user"""
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])
        self.assertIn('user', response.data)
    
    def test_auth_status_unauthenticated(self):
        """Test authentication status for unauthenticated user"""
        response = self.client.get(self.status_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
