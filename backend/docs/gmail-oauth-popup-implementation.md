# Gmail OAuth Implementation with Popup Flow

## Overview
This document provides complete implementation instructions for integrating Gmail OAuth authentication using a popup window approach. This maintains user experience by keeping them in the main application while handling OAuth flow.

## Architecture Overview

```
Frontend (React) → Backend (Django) → Google OAuth → Backend → Frontend
     ↓                ↓                   ↓           ↓         ↓
"Connect Gmail"   "OAuth URL"        "User Auth"   "Process"  "Success"
   (Popup)        (Generate)         (In Popup)    (Tokens)   (Close)
```

## 1. Backend Implementation

### 1.1 Dependencies

Add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies ...
    "google-auth>=2.23.0",
    "google-auth-oauthlib>=1.1.0",
    "google-auth-httplib2>=0.1.1",
    "google-api-python-client>=2.100.0",
    "cryptography>=41.0.0",  # For token encryption
]
```

### 1.2 Environment Variables

Add to `.env`:
```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/gmail/callback/

# Frontend URL for redirects
FRONTEND_URL=http://localhost:3000

# Encryption key for tokens (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
TOKEN_ENCRYPTION_KEY=your_generated_encryption_key
```

### 1.3 Django Settings

Add to `settings.py`:
```python
# Google OAuth Settings
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
FRONTEND_URL = os.getenv('FRONTEND_URL')

# Token encryption
TOKEN_ENCRYPTION_KEY = os.getenv('TOKEN_ENCRYPTION_KEY')

# Gmail API Scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email'
]
```

### 1.4 Database Models

Create `accounts/models.py`:
```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings

class EmailAccount(models.Model):
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_accounts')
    email_address = models.EmailField()
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    encrypted_access_token = models.TextField()
    encrypted_refresh_token = models.TextField(blank=True, null=True)
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
        fernet = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())
        return fernet.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt a token for use"""
        if not encrypted_token:
            return None
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

class APIAccessLog(models.Model):
    """Log all API access for security auditing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # 'token_refresh', 'email_fetch', 'auth_success'
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    error_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
```

### 1.5 OAuth Views

Create `accounts/views.py`:
```python
import json
import base64
import secrets
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from .models import EmailAccount, APIAccessLog

class GmailAuthorizeView(APIView):
    """Generate OAuth authorization URL for Gmail access"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
                    }
                },
                scopes=settings.GMAIL_SCOPES
            )
            
            flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
            
            # Generate secure state parameter
            state_data = {
                'user_id': request.user.id,
                'timestamp': timezone.now().isoformat(),
                'nonce': secrets.token_urlsafe(32)
            }
            state = base64.urlsafe_b64encode(
                json.dumps(state_data).encode()
            ).decode()
            
            # Generate authorization URL
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',  # Force consent to get refresh token
                state=state
            )
            
            return Response({
                'authorization_url': authorization_url,
                'success': True
            })
            
        except Exception as e:
            return Response({
                'error': str(e),
                'success': False
            }, status=500)

class GmailCallbackView(APIView):
    """Handle OAuth callback from Google"""
    authentication_classes = []  # Google calls this directly
    permission_classes = []
    
    def get(self, request):
        try:
            # Validate state parameter
            state = request.GET.get('state')
            if not state:
                return self._return_error('Missing state parameter')
            
            # Decode and validate state
            try:
                state_data = json.loads(
                    base64.urlsafe_b64decode(state.encode()).decode()
                )
                user_id = state_data['user_id']
                user = User.objects.get(id=user_id)
            except (json.JSONDecodeError, KeyError, User.DoesNotExist):
                return self._return_error('Invalid state parameter')
            
            # Check for authorization code
            code = request.GET.get('code')
            error = request.GET.get('error')
            
            if error:
                return self._return_error(f'OAuth error: {error}')
            
            if not code:
                return self._return_error('Missing authorization code')
            
            # Exchange code for tokens
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
                    }
                },
                scopes=settings.GMAIL_SCOPES
            )
            flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            # Get user email from Google
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            email_address = user_info.get('email')
            
            if not email_address:
                return self._return_error('Could not retrieve email address')
            
            # Save or update email account
            email_account, created = EmailAccount.objects.get_or_create(
                user=user,
                email_address=email_address,
                provider='gmail',
                defaults={
                    'token_expires_at': credentials.expiry or timezone.now() + timedelta(hours=1)
                }
            )
            
            # Set tokens
            email_account.set_tokens(
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expires_at=credentials.expiry
            )
            email_account.is_active = True
            email_account.save()
            
            # Log successful authentication
            APIAccessLog.objects.create(
                user=user,
                email_account=email_account,
                action='auth_success',
                success=True,
                ip_address=self._get_client_ip(request)
            )
            
            return self._return_success('Gmail connected successfully')
            
        except Exception as e:
            # Log error
            if 'user' in locals() and 'email_account' in locals():
                APIAccessLog.objects.create(
                    user=user,
                    email_account=email_account,
                    action='auth_error',
                    success=False,
                    error_message=str(e),
                    ip_address=self._get_client_ip(request)
                )
            
            return self._return_error(f'Authentication failed: {str(e)}')
    
    def _return_success(self, message):
        """Return success HTML that communicates with parent window"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gmail Connected</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                    background: #f0f9ff;
                }}
                .success {{ color: #059669; }}
            </style>
        </head>
        <body>
            <h2 class="success">✅ Gmail Connected Successfully!</h2>
            <p>You can close this window.</p>
            <script>
                // Send success message to parent window
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'GMAIL_AUTH_SUCCESS',
                        message: '{message}'
                    }}, '{settings.FRONTEND_URL}');
                }}
                
                // Auto-close after 2 seconds
                setTimeout(() => {{
                    window.close();
                }}, 2000);
            </script>
        </body>
        </html>
        """
        return HttpResponse(html)
    
    def _return_error(self, error_message):
        """Return error HTML that communicates with parent window"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Connection Error</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                    background: #fef2f2;
                }}
                .error {{ color: #dc2626; }}
            </style>
        </head>
        <body>
            <h2 class="error">❌ Connection Failed</h2>
            <p>{error_message}</p>
            <p>You can close this window and try again.</p>
            <script>
                // Send error message to parent window
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'GMAIL_AUTH_ERROR',
                        message: '{error_message}'
                    }}, '{settings.FRONTEND_URL}');
                }}
                
                // Auto-close after 5 seconds
                setTimeout(() => {{
                    window.close();
                }}, 5000);
            </script>
        </body>
        </html>
        """
        return HttpResponse(html)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class EmailAccountListView(APIView):
    """List user's connected email accounts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        accounts = EmailAccount.objects.filter(
            user=request.user,
            is_active=True
        ).values(
            'id', 'email_address', 'provider', 'created_at', 'token_expires_at'
        )
        
        return Response({
            'accounts': list(accounts),
            'count': len(accounts)
        })
    
    def delete(self, request):
        """Disconnect an email account"""
        account_id = request.data.get('account_id')
        
        try:
            account = EmailAccount.objects.get(
                id=account_id,
                user=request.user
            )
            account.is_active = False
            account.save()
            
            # Log disconnection
            APIAccessLog.objects.create(
                user=request.user,
                email_account=account,
                action='disconnect',
                success=True,
                ip_address=self._get_client_ip(request)
            )
            
            return Response({'success': True})
            
        except EmailAccount.DoesNotExist:
            return Response({'error': 'Account not found'}, status=404)
```

### 1.6 URL Configuration

Add to `accounts/urls.py`:
```python
from django.urls import path
from .views import GmailAuthorizeView, GmailCallbackView, EmailAccountListView

urlpatterns = [
    # API endpoints (called from React)
    path('api/auth/gmail/authorize/', GmailAuthorizeView.as_view(), name='gmail-authorize'),
    path('api/email-accounts/', EmailAccountListView.as_view(), name='email-accounts'),
    
    # OAuth callback (called by Google)
    path('auth/gmail/callback/', GmailCallbackView.as_view(), name='gmail-callback'),
]
```

Include in main `urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
]
```

## 2. Frontend Implementation

### 2.1 Gmail Connection Hook

Create `src/hooks/useGmailAuth.js`:
```javascript
import { useState, useCallback } from 'react';
import { toast } from 'react-hot-toast'; // or your preferred toast library

const useGmailAuth = () => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [emailAccounts, setEmailAccounts] = useState([]);

  const connectGmail = useCallback(async () => {
    if (isConnecting) return;
    
    setIsConnecting(true);
    
    try {
      // Get OAuth URL from backend
      const response = await fetch('/api/auth/gmail/authorize/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to get authorization URL');
      }
      
      // Open OAuth popup
      const popup = window.open(
        data.authorization_url,
        'gmail-auth',
        'width=500,height=600,scrollbars=yes,resizable=yes,status=yes,location=yes'
      );
      
      if (!popup) {
        throw new Error('Popup blocked. Please allow popups for this site.');
      }
      
      // Listen for messages from popup
      const handleMessage = (event) => {
        // Verify origin for security
        if (event.origin !== window.location.origin) {
          return;
        }
        
        if (event.data.type === 'GMAIL_AUTH_SUCCESS') {
          popup.close();
          toast.success(event.data.message || 'Gmail connected successfully!');
          fetchEmailAccounts(); // Refresh the list
        } else if (event.data.type === 'GMAIL_AUTH_ERROR') {
          popup.close();
          toast.error(event.data.message || 'Failed to connect Gmail');
        }
        
        // Clean up listener
        window.removeEventListener('message', handleMessage);
        setIsConnecting(false);
      };
      
      window.addEventListener('message', handleMessage);
      
      // Handle popup being closed manually
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          window.removeEventListener('message', handleMessage);
          setIsConnecting(false);
          
          // Only show message if we didn't get a success/error message
          if (isConnecting) {
            toast.info('Gmail connection cancelled');
          }
        }
      }, 1000);
      
    } catch (error) {
      console.error('Gmail connection error:', error);
      toast.error(error.message || 'Failed to connect Gmail');
      setIsConnecting(false);
    }
  }, [isConnecting]);

  const fetchEmailAccounts = useCallback(async () => {
    try {
      const response = await fetch('/api/email-accounts/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await response.json();
      setEmailAccounts(data.accounts || []);
      
    } catch (error) {
      console.error('Error fetching email accounts:', error);
      toast.error('Failed to load email accounts');
    }
  }, []);

  const disconnectAccount = useCallback(async (accountId) => {
    try {
      const response = await fetch('/api/email-accounts/', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ account_id: accountId })
      });
      
      if (response.ok) {
        toast.success('Email account disconnected');
        fetchEmailAccounts(); // Refresh the list
      } else {
        throw new Error('Failed to disconnect account');
      }
      
    } catch (error) {
      console.error('Error disconnecting account:', error);
      toast.error('Failed to disconnect account');
    }
  }, [fetchEmailAccounts]);

  return {
    connectGmail,
    disconnectAccount,
    fetchEmailAccounts,
    emailAccounts,
    isConnecting
  };
};

export default useGmailAuth;
```

### 2.2 Gmail Connection Component

Create `src/components/GmailConnection.jsx`:
```javascript
import React, { useEffect } from 'react';
import useGmailAuth from '../hooks/useGmailAuth';

const GmailConnection = () => {
  const {
    connectGmail,
    disconnectAccount,
    fetchEmailAccounts,
    emailAccounts,
    isConnecting
  } = useGmailAuth();

  useEffect(() => {
    fetchEmailAccounts();
  }, [fetchEmailAccounts]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Email Connections</h2>
      
      {/* Connect Button */}
      <div className="mb-6">
        <button
          onClick={connectGmail}
          disabled={isConnecting}
          className={`
            px-4 py-2 rounded-md font-medium transition-colors
            ${isConnecting 
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700'
            }
          `}
        >
          {isConnecting ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Connecting...
            </>
          ) : (
            <>
              <svg className="w-5 h-5 inline mr-2" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Connect Gmail
            </>
          )}
        </button>
      </div>

      {/* Connected Accounts */}
      <div>
        <h3 className="text-lg font-medium mb-3">Connected Accounts</h3>
        
        {emailAccounts.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <p>No email accounts connected yet.</p>
            <p className="text-sm">Connect your Gmail to start processing transactions.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {emailAccounts.map((account) => (
              <div key={account.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-600" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium">{account.email_address}</p>
                    <p className="text-sm text-gray-500">
                      Connected on {formatDate(account.created_at)}
                    </p>
                    <p className="text-xs text-gray-400">
                      Token expires: {formatDate(account.token_expires_at)}
                    </p>
                  </div>
                </div>
                
                <button
                  onClick={() => disconnectAccount(account.id)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Disconnect
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GmailConnection;
```

## 3. Token Management for Workers

### 3.1 Token Refresh Service

Create `accounts/services.py`:
```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailAccount, APIAccessLog

class GmailTokenService:
    @staticmethod
    def refresh_token(email_account):
        """Refresh an expired Gmail token"""
        try:
            # Create credentials object
            credentials = Credentials(
                token=email_account.get_access_token(),
                refresh_token=email_account.get_refresh_token(),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=settings.GMAIL_SCOPES
            )
            
            # Refresh the token
            credentials.refresh(Request())
            
            # Update stored tokens
            email_account.set_tokens(
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expires_at=credentials.expiry
            )
            
            # Log success
            APIAccessLog.objects.create(
                user=email_account.user,
                email_account=email_account,
                action='token_refresh',
                success=True
            )
            
            return credentials.token
            
        except Exception as e:
            # Log error
            APIAccessLog.objects.create(
                user=email_account.user,
                email_account=email_account,
                action='token_refresh',
                success=False,
                error_message=str(e)
            )
            
            # Deactivate account if refresh fails
            email_account.is_active = False
            email_account.save()
            
            raise e
    
    @staticmethod
    def get_valid_token(email_account):
        """Get a valid access token, refreshing if necessary"""
        # Check if token is expired or will expire soon
        if email_account.token_expires_at <= timezone.now() + timedelta(minutes=5):
            return GmailTokenService.refresh_token(email_account)
        
        return email_account.get_access_token()
    
    @staticmethod
    def build_gmail_service(email_account):
        """Build Gmail service with valid credentials"""
        access_token = GmailTokenService.get_valid_token(email_account)
        
        credentials = Credentials(
            token=access_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=settings.GMAIL_SCOPES
        )
        
        return build('gmail', 'v1', credentials=credentials)
```

### 3.2 Celery Tasks

Create `accounts/tasks.py`:
```python
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import EmailAccount
from .services import GmailTokenService
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_user_emails(user_id, email_account_id):
    """Process emails for a specific user and email account"""
    try:
        email_account = EmailAccount.objects.get(
            id=email_account_id,
            user_id=user_id,
            is_active=True
        )
        
        # Build Gmail service with valid token
        service = GmailTokenService.build_gmail_service(email_account)
        
        # Get recent emails (last 7 days)
        query = 'newer_than:7d'
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute()
        
        messages = results.get('messages', [])
        
        for message in messages:
            # Get full message
            msg = service.users().messages().get(
                userId='me',
                id=message['id']
            ).execute()
            
            # Process message (extract transaction data)
            # This is where you'd implement your email parsing logic
            process_email_message.delay(email_account.id, msg)
        
        logger.info(f"Processed {len(messages)} emails for {email_account.email_address}")
        
    except EmailAccount.DoesNotExist:
        logger.error(f"Email account {email_account_id} not found for user {user_id}")
    except Exception as e:
        logger.error(f"Error processing emails for account {email_account_id}: {e}")

@shared_task
def process_email_message(email_account_id, message_data):
    """Process individual email message to extract transaction data"""
    try:
        email_account = EmailAccount.objects.get(id=email_account_id)
        
        # Extract transaction data from email
        # This is where your AI/regex parsing would happen
        
        # Example structure:
        headers = message_data.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        
        # Only process emails from known bank senders
        if not is_bank_email(sender):
            return
        
        # Extract transaction details
        transaction_data = extract_transaction_data(message_data)
        
        if transaction_data:
            # Save transaction to database
            # create_transaction(email_account.user, transaction_data)
            pass
        
        logger.info(f"Processed email {message_data['id']} from {sender}")
        
    except Exception as e:
        logger.error(f"Error processing email message: {e}")

@shared_task
def refresh_expiring_tokens():
    """Refresh tokens that are about to expire"""
    # Find tokens expiring in the next 2 hours
    expiring_accounts = EmailAccount.objects.filter(
        token_expires_at__lt=timezone.now() + timedelta(hours=2),
        is_active=True
    )
    
    for account in expiring_accounts:
        try:
            GmailTokenService.refresh_token(account)
            logger.info(f"Refreshed token for {account.email_address}")
        except Exception as e:
            logger.error(f"Failed to refresh token for {account.email_address}: {e}")

def is_bank_email(sender):
    """Check if email is from a known bank"""
    bank_domains = [
        'bancobcr.com',
        'baccredomatic.com',
        'scotiabankcr.com',
        # Add more bank domains
    ]
    
    return any(domain in sender.lower() for domain in bank_domains)

def extract_transaction_data(message_data):
    """Extract transaction data from email message"""
    # This would contain your AI/regex logic
    # Return structured transaction data
    return None
```

## 4. Security Considerations

### 4.1 Environment Security
- Never commit `.env` files
- Use different encryption keys for different environments
- Rotate encryption keys periodically
- Use strong, randomly generated keys

### 4.2 Token Security
- Tokens are encrypted at rest
- Tokens are only decrypted when needed
- Failed refresh attempts deactivate accounts
- All API access is logged for auditing

### 4.3 CORS Configuration
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev
    "https://your-frontend-domain.com",  # Production
]

# OAuth callback doesn't need CORS (not called from frontend)
```

## 5. Testing

### 5.1 Backend Testing
```python
# tests/test_gmail_auth.py
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import EmailAccount

class GmailAuthTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_email_account_encryption(self):
        account = EmailAccount.objects.create(
            user=self.user,
            email_address='test@gmail.com',
            provider='gmail'
        )
        
        # Test token encryption/decryption
        test_token = 'test_access_token_123'
        account.set_tokens(access_token=test_token)
        
        # Token should be encrypted in database
        self.assertNotEqual(account.encrypted_access_token, test_token)
        
        # But should decrypt correctly
        self.assertEqual(account.get_access_token(), test_token)
```

### 5.2 Frontend Testing
```javascript
// __tests__/GmailConnection.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import GmailConnection from '../components/GmailConnection';

// Mock the hook
jest.mock('../hooks/useGmailAuth', () => ({
  __esModule: true,
  default: () => ({
    connectGmail: jest.fn(),
    emailAccounts: [],
    isConnecting: false,
    fetchEmailAccounts: jest.fn()
  })
}));

test('renders connect gmail button', () => {
  render(<GmailConnection />);
  expect(screen.getByText('Connect Gmail')).toBeInTheDocument();
});
```

## 6. Deployment Checklist

### 6.1 Backend Deployment
- [ ] Set all environment variables
- [ ] Run migrations: `python manage.py migrate`
- [ ] Configure Google OAuth credentials
- [ ] Set up Celery workers
- [ ] Configure Redis for token caching
- [ ] Set up SSL certificates

### 6.2 Frontend Deployment
- [ ] Update API URLs for production
- [ ] Configure CORS origins
- [ ] Test popup functionality in production
- [ ] Verify OAuth redirect URLs

### 6.3 Google OAuth Setup
- [ ] Create Google Cloud Project
- [ ] Enable Gmail API
- [ ] Configure OAuth consent screen
- [ ] Add authorized redirect URIs
- [ ] Set up API credentials

This implementation provides a secure, scalable solution for Gmail OAuth integration with popup-based authentication flow. The tokens are properly encrypted, workers can access them securely, and the user experience remains smooth throughout the process.
