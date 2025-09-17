from django.urls import path
# from .views import (
#     GmailAuthorizeView, GmailCallbackView,
#     OutlookAuthorizeView, OutlookCallbackView,
#     EmailProviderListView
# )

urlpatterns = [
    # TODO: OAuth para Gmail API (implementar después)
    # path('api/auth/gmail/authorize/', GmailAuthorizeView.as_view(), name='gmail-authorize'),
    # path('auth/gmail/callback/', GmailCallbackView.as_view(), name='gmail-callback'),
    
    # TODO: OAuth para Outlook API (implementar después)
    # path('api/auth/outlook/authorize/', OutlookAuthorizeView.as_view(), name='outlook-authorize'),
    # path('auth/outlook/callback/', OutlookCallbackView.as_view(), name='outlook-callback'),
    
    # TODO: Gestión de providers (implementar después)
    # path('api/email-providers/', EmailProviderListView.as_view(), name='email-providers'),
]
