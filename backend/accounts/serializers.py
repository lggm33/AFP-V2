from rest_framework import serializers
from django.contrib.auth.models import User
from dj_rest_auth.registration.serializers import RegisterSerializer as BaseRegisterSerializer


class CustomRegisterSerializer(BaseRegisterSerializer):
    """
    Custom registration serializer that doesn't require username
    """
    username = None  # Remove username field
    
    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
        }


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    Custom user details serializer for API responses
    """
    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
        read_only_fields = ('pk', 'email', 'is_staff', 'date_joined')
