# Django Multi-Frontend Authentication System

This implementation provides a comprehensive Django users app that manages three distinct user types (Customer, Officer, Manager) with authentication that ensures each user type can only access their designated Flutter frontend.

## Features

### 🔐 Security-First Design
- **Cross-Frontend Access Prevention**: Users cannot log into frontends they are not authorized for
- **User Type Validation**: LoginSerializer validates that user's type matches the frontend's expected type
- **JWT Token Claims**: Tokens include user_type claim for additional validation
- **Middleware Protection**: UserTypeMiddleware validates user types on authenticated requests
- **Token Blacklisting**: Secure logout with JWT token blacklisting

### 👥 User Types
- **Customer**: Regular users accessing the customer interface
- **Officer**: Staff members accessing the office interface
- **Manager**: Management accessing the manager interface

### 🛠️ Implementation

#### Backend Components
- **Custom User Model** (`users/models.py`): Extends AbstractUser with user_type field
- **Serializers** (`users/serializers.py`):
  - `UserSerializer`: User data representation
  - `RegisterSerializer`: User registration with password confirmation
  - `LoginSerializer`: **CRITICAL** - Validates user_type to prevent cross-frontend access
- **Views** (`users/views.py`):
  - `RegisterView`: User registration
  - `LoginView`: Login with user type validation, returns JWT tokens
  - `LogoutView`: Logout with token blacklisting
  - `UserProfileView`: Get/update user profile
- **Permissions** (`users/permissions.py`):
  - `IsCustomer`, `IsOfficer`, `IsManager`, `IsOfficerOrManager`
- **Middleware** (`users/middleware.py`):
  - `UserTypeMiddleware`: Validates user types on authenticated requests

#### Frontend Components
Each Flutter frontend has a hardcoded user type in its auth service:
- `user_interface/lib/services/auth_service.dart`: `userType = 'customer'`
- `office_interface/lib/services/auth_service.dart`: `userType = 'officer'`
- `manager_interface/lib/services/auth_service.dart`: `userType = 'manager'`

## Installation

1. **Install Dependencies**
```bash
cd BACKEND
pip install -r requirements.txt
```

2. **Run Migrations**
```bash
python manage.py migrate
```

3. **Create Superuser (Optional)**
```bash
python manage.py createsuperuser
```

4. **Run Development Server**
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login with user type validation
- `POST /api/auth/logout/` - Logout and blacklist token
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get current user profile
- `PUT/PATCH /api/auth/profile/` - Update user profile

## Testing

### Run Django Tests
```bash
cd BACKEND
python manage.py test users -v 2
```

**All 16 tests pass successfully:**
- User registration for all user types
- Cross-frontend login prevention
- JWT token generation with user_type claim
- Profile management
- Permission validation

### Run Demonstration Script
```bash
cd BACKEND
python test_authentication.py
```

This script demonstrates:
- User creation for all types
- Cross-frontend access prevention
- JWT token claims validation

## Security Validation

### Testing Scenarios (All Working ✓)

1. **Customer user logging into user_interface** → ✅ Success
2. **Customer user trying office_interface** → ❌ Blocked: "Access denied. This account is registered as a Customer, but you are trying to access the officer interface."
3. **Officer user logging into office_interface** → ✅ Success
4. **Officer user trying user_interface** → ❌ Blocked
5. **Manager user logging into manager_interface** → ✅ Success
6. **Manager user trying user_interface** → ❌ Blocked

## Configuration

### Settings (`BACKEND/settings.py`)
```python
AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'users',
]

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    'users.middleware.UserTypeMiddleware',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    ...
}
```

## Example Usage

### Register a Customer
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer1",
    "email": "customer@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "user_type": "customer"
  }'
```

### Login via Customer Interface
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer1",
    "password": "SecurePass123!",
    "user_type": "customer"
  }'
```

### Try Cross-Frontend Access (Will Fail)
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer1",
    "password": "SecurePass123!",
    "user_type": "officer"
  }'
```
**Response**: `400 Bad Request` with error message explaining the user type mismatch.

## Flutter Integration

Each Flutter app includes `lib/services/auth_service.dart` with:
- Hardcoded `userType` constant
- Login method that sends user_type for validation
- Token storage and management
- Automatic token refresh

### Example Flutter Usage
```dart
final authService = AuthService();

// Login (user_type is sent automatically)
final result = await authService.login('customer1', 'SecurePass123!');
if (result['success']) {
  // Login successful
  print('Welcome ${result['user']['username']}');
} else {
  // Login failed (e.g., wrong frontend)
  print('Error: ${result['message']}');
}
```

## Admin Interface

Access Django admin at `http://localhost:8000/admin/` to:
- View and manage users
- Filter by user type
- Search users by username, email, phone
- View user creation/update timestamps

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flutter Frontends                     │
├──────────────┬──────────────┬──────────────────────────┤
│ user_interface │ office_interface │ manager_interface  │
│ (customer)     │ (officer)        │ (manager)          │
└──────┬─────────┴──────┬───────────┴──────┬─────────────┘
       │                │                  │
       │ userType:      │ userType:        │ userType:
       │ 'customer'     │ 'officer'        │ 'manager'
       │                │                  │
       └────────────────┼──────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Django Backend API    │
            │  /api/auth/login/      │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  LoginSerializer       │
            │  Validates user_type   │
            │  matches user account  │
            └───────────┬───────────┘
                        │
                ┌───────┴────────┐
                │                │
          ✅ Match          ❌ Mismatch
          Returns JWT        Returns Error
```

## File Structure

```
BACKEND/
├── users/
│   ├── models.py              # Custom User model
│   ├── serializers.py         # DRF serializers with validation
│   ├── views.py               # API views
│   ├── permissions.py         # Custom permissions
│   ├── middleware.py          # User type middleware
│   ├── urls.py                # URL configuration
│   ├── admin.py               # Admin configuration
│   ├── tests.py               # Comprehensive tests
│   └── migrations/
├── BACKEND/
│   ├── settings.py            # Django settings
│   └── urls.py                # Main URL configuration
├── requirements.txt           # Python dependencies
└── test_authentication.py     # Demonstration script

FRONTEND/
├── user_interface/lib/services/auth_service.dart    # Customer auth
├── office_interface/lib/services/auth_service.dart  # Officer auth
└── manager_interface/lib/services/auth_service.dart # Manager auth
```

## Dependencies

```
Django==5.2.8
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
```

**Note**: Django 5.2.8 is used to patch security vulnerabilities present in 5.2.7:
- CVE: Denial-of-service vulnerability in HttpResponseRedirect and HttpResponsePermanentRedirect on Windows
- CVE: SQL injection via _connector keyword argument in QuerySet and Q objects

## Production Considerations

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables for `SECRET_KEY`
4. Enable HTTPS and set security headers
5. Configure proper CORS settings
6. Use a production database (PostgreSQL, MySQL)
7. Set up proper token rotation and expiration policies
8. Implement rate limiting for login attempts
9. Add logging and monitoring
10. Configure static files serving

## License

This implementation is part of the TPS project.
