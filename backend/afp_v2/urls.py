"""
URL configuration for afp_v2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def debug_login_api(request):
    """
    Temporary debug endpoint to test login without page reload
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password required'
            })
        
        # Test authentication
        user = authenticate(username=username, password=password)
        
        if user:
            return JsonResponse({
                'success': True,
                'user_info': {
                    'username': user.username,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'last_login': str(user.last_login) if user.last_login else None,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Authentication failed',
                'debug_info': {
                    'username_provided': username,
                    'session_engine': settings.SESSION_ENGINE,
                    'debug_mode': settings.DEBUG,
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

urlpatterns = [
    path("admin/", admin.site.urls),

    
    # Autenticación básica con allauth
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/social/', include('allauth.socialaccount.urls')),
    
    # OAuth personalizado para email APIs
    path('', include('accounts.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
