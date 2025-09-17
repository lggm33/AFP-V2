from allauth.account.adapter import DefaultAccountAdapter
import uuid


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter to handle username generation
    """
    
    def generate_unique_username(self, txts, uids=None):
        """
        Generate a unique username from email
        """
        # Get the first text (usually email prefix)
        base_username = txts[0] if txts else 'user'
        
        # Add a unique suffix to avoid conflicts
        unique_suffix = uuid.uuid4().hex[:8]
        username = f"{base_username}_{unique_suffix}"
        
        return username
    
    def populate_username(self, request, user):
        """
        Fill in a valid username, if required and missing.
        """
        if hasattr(user, 'username'):
            # Generate username from email if not set
            if not user.username:
                email = getattr(user, 'email', '')
                if email:
                    email_prefix = email.split('@')[0]
                    user.username = self.generate_unique_username([email_prefix])
                else:
                    user.username = self.generate_unique_username(['user'])
        return user
