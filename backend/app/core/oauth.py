"""OAuth 2.0 authentication service."""
from typing import Optional, Dict
from authlib.integrations.starlette_client import OAuth
from app.core.config import settings


# Initialize OAuth client
oauth = OAuth()

# Register Google OAuth
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    },
)

# Register Microsoft OAuth
oauth.register(
    name='microsoft',
    client_id=settings.MICROSOFT_CLIENT_ID,
    client_secret=settings.MICROSOFT_CLIENT_SECRET,
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    client_kwargs={
        'scope': 'openid email profile',
    },
)

# Register LinkedIn OAuth
oauth.register(
    name='linkedin',
    client_id=settings.LINKEDIN_CLIENT_ID,
    client_secret=settings.LINKEDIN_CLIENT_SECRET,
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


def get_oauth_provider_data(provider: str, token: Dict) -> Optional[Dict[str, str]]:
    """
    Extract user data from OAuth provider's token response.

    Returns dict with keys: id, email, name, avatar_url, email_verified
    """
    if provider == 'google':
        user_info = token.get('userinfo', {})
        return {
            'id': user_info.get('sub'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'avatar_url': user_info.get('picture'),
            'email_verified': user_info.get('email_verified', False),
        }

    elif provider == 'microsoft':
        user_info = token.get('userinfo', {})
        return {
            'id': user_info.get('sub'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'avatar_url': None,  # Microsoft doesn't provide avatar in basic scope
            'email_verified': True,  # Microsoft emails are pre-verified
        }

    elif provider == 'linkedin':
        user_info = token.get('userinfo', {})
        return {
            'id': user_info.get('sub'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'avatar_url': user_info.get('picture'),
            'email_verified': user_info.get('email_verified', False),
        }

    return None
