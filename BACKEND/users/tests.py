"""
Comprehensive tests for the users app authentication system.
Tests cover user registration, login with user_type validation,
and cross-frontend access prevention.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserRegistrationTestCase(TestCase):
    """Test user registration for different user types."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
    
    def test_register_customer(self):
        """Test registering a customer user."""
        data = {
            'username': 'customer1',
            'email': 'customer1@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'user_type': 'customer'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['user_type'], 'customer')
        self.assertTrue(User.objects.filter(username='customer1', user_type='customer').exists())
    
    def test_register_officer(self):
        """Test registering an officer user."""
        data = {
            'username': 'officer1',
            'email': 'officer1@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'user_type': 'officer'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['user_type'], 'officer')
        self.assertTrue(User.objects.filter(username='officer1', user_type='officer').exists())
    
    def test_register_manager(self):
        """Test registering a manager user."""
        data = {
            'username': 'manager1',
            'email': 'manager1@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'user_type': 'manager'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['user_type'], 'manager')
        self.assertTrue(User.objects.filter(username='manager1', user_type='manager').exists())
    
    def test_register_password_mismatch(self):
        """Test that registration fails when passwords don't match."""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'TestPass123!',
            'password2': 'DifferentPass123!',
            'user_type': 'customer'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(TestCase):
    """Test login functionality with user type validation."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        
        # Create test users of different types
        self.customer = User.objects.create_user(
            username='customer_test',
            email='customer@test.com',
            password='TestPass123!',
            user_type='customer'
        )
        self.officer = User.objects.create_user(
            username='officer_test',
            email='officer@test.com',
            password='TestPass123!',
            user_type='officer'
        )
        self.manager = User.objects.create_user(
            username='manager_test',
            email='manager@test.com',
            password='TestPass123!',
            user_type='manager'
        )
    
    def test_customer_login_via_customer_interface(self):
        """Test that a customer can login via customer interface (SHOULD SUCCEED)."""
        data = {
            'username': 'customer_test',
            'password': 'TestPass123!',
            'user_type': 'customer'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['user_type'], 'customer')
    
    def test_customer_login_via_officer_interface(self):
        """Test that a customer CANNOT login via officer interface (SHOULD FAIL)."""
        data = {
            'username': 'customer_test',
            'password': 'TestPass123!',
            'user_type': 'officer'  # Wrong interface
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
    
    def test_customer_login_via_manager_interface(self):
        """Test that a customer CANNOT login via manager interface (SHOULD FAIL)."""
        data = {
            'username': 'customer_test',
            'password': 'TestPass123!',
            'user_type': 'manager'  # Wrong interface
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
    
    def test_officer_login_via_officer_interface(self):
        """Test that an officer can login via officer interface (SHOULD SUCCEED)."""
        data = {
            'username': 'officer_test',
            'password': 'TestPass123!',
            'user_type': 'officer'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['user_type'], 'officer')
    
    def test_officer_login_via_customer_interface(self):
        """Test that an officer CANNOT login via customer interface (SHOULD FAIL)."""
        data = {
            'username': 'officer_test',
            'password': 'TestPass123!',
            'user_type': 'customer'  # Wrong interface
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
    
    def test_manager_login_via_manager_interface(self):
        """Test that a manager can login via manager interface (SHOULD SUCCEED)."""
        data = {
            'username': 'manager_test',
            'password': 'TestPass123!',
            'user_type': 'manager'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['user_type'], 'manager')
    
    def test_manager_login_via_customer_interface(self):
        """Test that a manager CANNOT login via customer interface (SHOULD FAIL)."""
        data = {
            'username': 'manager_test',
            'password': 'TestPass123!',
            'user_type': 'customer'  # Wrong interface
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
    
    def test_login_invalid_credentials(self):
        """Test that login fails with invalid credentials."""
        data = {
            'username': 'customer_test',
            'password': 'WrongPassword',
            'user_type': 'customer'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTestCase(TestCase):
    """Test user profile endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.profile_url = '/api/auth/profile/'
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='customer'
        )
        
        # Login to get token
        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!',
            'user_type': 'customer'
        }
        response = self.client.post('/api/auth/login/', login_data, format='json')
        self.access_token = response.data['access']
    
    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_profile_unauthenticated(self):
        """Test getting profile when not authenticated."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        """Test updating profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '1234567890'
        }
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['first_name'], 'John')
        self.assertEqual(response.data['user']['last_name'], 'Doe')


class JWTTokenTestCase(TestCase):
    """Test JWT token generation with user_type claim."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='customer'
        )
    
    def test_jwt_contains_user_type(self):
        """Test that JWT token contains user_type claim."""
        import jwt
        from django.conf import settings
        
        data = {
            'username': 'testuser',
            'password': 'TestPass123!',
            'user_type': 'customer'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Decode the access token to check for user_type claim
        access_token = response.data['access']
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        
        self.assertIn('user_type', decoded)
        self.assertEqual(decoded['user_type'], 'customer')

