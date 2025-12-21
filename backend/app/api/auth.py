"""Authentication API endpoints."""
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.user import User, UserProfile
from app.schemas.user import (
    UserCreate, UserLogin, ProfileUpdate,
    UserResponse, UserProfileResponse, UserWithProfileResponse, TokenResponse
)
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.deps import get_current_user
from app.core.oauth import oauth, get_oauth_provider_data
from app.core.config import settings

router = APIRouter()

# Valid OAuth providers
OAuthProvider = Literal["google", "microsoft", "linkedin"]


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    # Check if email already exists
    query = select(User).where(User.email == user_data.email.lower())
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=user_data.email.lower(),
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
    )
    db.add(user)
    await db.flush()  # Get user.id

    # Create profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    await db.commit()
    await db.refresh(user)

    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token."""
    # Find user by email
    query = select(User).where(
        User.email == credentials.email.lower(),
        User.is_active == True
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserWithProfileResponse)
async def get_me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user with profile."""
    # Reload user with profile
    query = (
        select(User)
        .where(User.id == user.id)
        .options(selectinload(User.profile))
    )
    result = await db.execute(query)
    user = result.scalar_one()

    response = UserWithProfileResponse.model_validate(user)
    if user.profile:
        response.profile = UserProfileResponse.model_validate(user.profile)

    return response


@router.patch("/profile", response_model=UserWithProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile settings."""
    # Get profile
    query = select(UserProfile).where(UserProfile.user_id == user.id)
    result = await db.execute(query)
    profile = result.scalar_one()

    update_data = profile_data.model_dump(exclude_unset=True)

    # Update user name if provided
    if "name" in update_data:
        user.name = update_data.pop("name")

    # Update profile fields
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()

    # Return updated user with profile
    return await get_me(user, db)


# ============ OAuth Endpoints ============

def get_redirect_uri(provider: str) -> str:
    """Get redirect URI for OAuth provider."""
    redirect_uris = {
        "google": settings.GOOGLE_REDIRECT_URI,
        "microsoft": settings.MICROSOFT_REDIRECT_URI,
        "linkedin": settings.LINKEDIN_REDIRECT_URI,
    }
    return redirect_uris.get(provider, "")


@router.get("/oauth/{provider}/login")
async def oauth_login(provider: OAuthProvider, request: Request):
    """
    Initiate OAuth login flow.
    Redirects user to the OAuth provider's authorization page.
    """
    redirect_uri = get_redirect_uri(provider)
    if not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' not configured"
        )

    oauth_client = getattr(oauth, provider, None)
    if not oauth_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' not available"
        )

    return await oauth_client.authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: OAuthProvider,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth callback from provider.
    Creates or links user account and returns JWT token.
    """
    oauth_client = getattr(oauth, provider, None)
    if not oauth_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' not available"
        )

    try:
        # Exchange code for token
        token = await oauth_client.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )

    # Get user info from provider
    user_info = get_oauth_provider_data(provider, token)
    if not user_info or not user_info.get('email'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from OAuth provider"
        )

    email = user_info['email'].lower()
    oauth_id = user_info['id']

    # Check if user exists by OAuth ID
    query = select(User).where(
        User.oauth_provider == provider,
        User.oauth_id == oauth_id
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        # Check if user exists by email (for account linking)
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user:
            # Link OAuth to existing account
            user.oauth_provider = provider
            user.oauth_id = oauth_id
            user.oauth_email_verified = user_info.get('email_verified', False)
            if user_info.get('avatar_url') and not user.avatar_url:
                user.avatar_url = user_info['avatar_url']
            if user_info.get('name') and not user.name:
                user.name = user_info['name']
        else:
            # Create new user
            user = User(
                email=email,
                oauth_provider=provider,
                oauth_id=oauth_id,
                oauth_email_verified=user_info.get('email_verified', False),
                name=user_info.get('name'),
                avatar_url=user_info.get('avatar_url'),
                is_verified=user_info.get('email_verified', False),
            )
            db.add(user)
            await db.flush()

            # Create profile for new user
            profile = UserProfile(user_id=user.id)
            db.add(profile)

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Redirect to frontend with token
    frontend_url = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"
    redirect_url = f"{frontend_url}/auth/callback/{provider}?token={access_token}"

    return RedirectResponse(url=redirect_url)
