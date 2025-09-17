from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, EmailProvider, APIAccessLog


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(EmailProvider)
class EmailProviderAdmin(admin.ModelAdmin):
    list_display = ['email_address', 'provider', 'user', 'is_active', 'created_at', 'token_expires_at']
    list_filter = ['provider', 'is_active', 'created_at']
    search_fields = ['email_address', 'user__email']
    readonly_fields = ['encrypted_access_token', 'encrypted_refresh_token', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'email_address', 'provider', 'is_active')
        }),
        ('Token Info', {
            'fields': ('scopes', 'token_expires_at'),
        }),
        ('Encrypted Tokens (Read Only)', {
            'fields': ('encrypted_access_token', 'encrypted_refresh_token'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(APIAccessLog)
class APIAccessLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'success', 'email_provider', 'ip_address']
    list_filter = ['success', 'action', 'timestamp']
    search_fields = ['user__email', 'action', 'error_message']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'email_provider', 'action', 'success')
        }),
        ('Details', {
            'fields': ('error_message', 'ip_address', 'timestamp'),
        }),
    )


# Re-register User with profile
admin.site.unregister(User)
admin.site.register(User, UserAdmin)