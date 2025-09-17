from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings


class UserProfile(models.Model):
    """Extender User model para finanzas personales"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    timezone = models.CharField(max_length=50, default='UTC')
    currency_preference = models.CharField(max_length=3, default='USD')
    notification_preferences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.email}"


class EmailProvider(models.Model):
    """OAuth tokens para email APIs - SEPARADO de allauth"""
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_providers')
    email_address = models.EmailField()
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    encrypted_access_token = models.TextField()
    encrypted_refresh_token = models.TextField(blank=True, null=True)
    scopes = models.JSONField()  # ['gmail.readonly', 'mail.read']
    token_expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'email_address', 'provider']
    
    def encrypt_token(self, token):
        """Encrypt a token for storage"""
        if not token:
            return ''
        if not settings.TOKEN_ENCRYPTION_KEY:
            raise ValueError("TOKEN_ENCRYPTION_KEY not configured")
        fernet = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())
        return fernet.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt a token for use"""
        if not encrypted_token:
            return None
        if not settings.TOKEN_ENCRYPTION_KEY:
            raise ValueError("TOKEN_ENCRYPTION_KEY not configured")
        fernet = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())
        return fernet.decrypt(encrypted_token.encode()).decode()
    
    def get_access_token(self):
        """Get decrypted access token"""
        return self.decrypt_token(self.encrypted_access_token)
    
    def get_refresh_token(self):
        """Get decrypted refresh token"""
        return self.decrypt_token(self.encrypted_refresh_token)
    
    def set_tokens(self, access_token, refresh_token=None, expires_at=None):
        """Set encrypted tokens"""
        self.encrypted_access_token = self.encrypt_token(access_token)
        if refresh_token:
            self.encrypted_refresh_token = self.encrypt_token(refresh_token)
        if expires_at:
            self.token_expires_at = expires_at
        self.save()

    def __str__(self):
        return f"{self.provider}: {self.email_address} ({self.user.email})"


class APIAccessLog(models.Model):
    """Audit log para APIs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_provider = models.ForeignKey(EmailProvider, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50)  # 'token_refresh', 'email_fetch', 'auth_success'
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    error_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.action} - {self.user.email} at {self.timestamp}"