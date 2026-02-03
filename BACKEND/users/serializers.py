from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model representation.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'phone_number', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password confirmation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 
                  'first_name', 'last_name', 'user_type', 'phone_number']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        """
        Validate that passwords match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create and return a new user instance with encrypted password.
        """
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with CRITICAL user_type validation.
    This prevents users from logging into frontends they are not authorized for.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    user_type = serializers.ChoiceField(
        choices=['customer', 'officer', 'manager'],
        required=True,
        help_text='User type from the frontend application'
    )
    
    def validate(self, attrs):
        """
        Validate credentials and CRITICAL: ensure user_type matches.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        requested_user_type = attrs.get('user_type')
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            raise serializers.ValidationError({
                'detail': 'Invalid credentials. Please check your username and password.'
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': 'User account is disabled.'
            })
        
        # CRITICAL VALIDATION: Check if user's type matches the requested type
        if user.user_type != requested_user_type:
            raise serializers.ValidationError({
                'detail': f'Access denied. This account is registered as a {user.get_user_type_display()}, '
                         f'but you are trying to access the {requested_user_type} interface. '
                         f'Please use the correct application for your account type.'
            })
        
        attrs['user'] = user
        return attrs
