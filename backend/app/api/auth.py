"""Authentication API endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter()


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
