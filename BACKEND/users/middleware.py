from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class UserTypeMiddleware(MiddlewareMixin):
    """
    Middleware to validate user type on authenticated requests.
    Skips public endpoints like login/register.
    Extracts and validates user_type from JWT token.
    """
    
    # Endpoints that should skip user type validation
    SKIP_PATHS = [
        '/api/auth/register/',
        '/api/auth/login/',
        '/api/auth/token/refresh/',
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """
        Process incoming request and validate user type if authenticated.
        """
        # Skip validation for excluded paths
        path = request.path
        if any(path.startswith(skip_path) for skip_path in self.SKIP_PATHS):
            return None
        
        # Try to authenticate using JWT
        jwt_auth = JWTAuthentication()
        
        try:
            # Extract token from header
            header = jwt_auth.get_header(request)
            if header is None:
                # No auth header, skip validation (will be handled by view permissions)
                return None
            
            raw_token = jwt_auth.get_raw_token(header)
            if raw_token is None:
                return None
            
            # Validate token
            validated_token = jwt_auth.get_validated_token(raw_token)
            
            # Get user from token
            user = jwt_auth.get_user(validated_token)
            
            # Validate user_type claim exists and matches user's actual type
            token_user_type = validated_token.get('user_type')
            
            if token_user_type and user.user_type != token_user_type:
                raise AuthenticationFailed(
                    'Token user_type does not match user account type.'
                )
            
        except AuthenticationFailed:
            # Re-raise authentication failures
            raise
        except Exception:
            # For any other exceptions, skip validation
            # (will be handled by view permissions)
            pass
        
        return None
