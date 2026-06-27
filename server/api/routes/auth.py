"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    AuthResponse,
    TokenRefresh,
)
from app.security.auth import (
    get_password_hash,
    verify_password,
    create_tokens,
    decode_token,
)
from app.database.db import get_db
from app.utils.logger import setup_logger

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = setup_logger(__name__)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered",
            )

        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_admin=False,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate tokens
        tokens = create_tokens(
            subject=new_user.email,
            user_id=new_user.id,
            is_admin=new_user.is_admin,
        )

        logger.info(f"New user registered: {new_user.username}")

        return AuthResponse(
            user=UserResponse.from_orm(new_user),
            tokens=TokenResponse(**tokens),
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login user and return access/refresh tokens
    """
    try:
        # Find user by username or email
        user = db.query(User).filter(
            (User.username == credentials.username) | (User.email == credentials.username)
        ).first()

        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Generate tokens
        tokens = create_tokens(
            subject=user.email,
            user_id=user.id,
            is_admin=user.is_admin,
        )

        logger.info(f"User logged in: {user.username}")

        return AuthResponse(
            user=UserResponse.from_orm(user),
            tokens=TokenResponse(**tokens),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token
    """
    try:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("user_id")
        subject = payload.get("sub")

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new tokens
        tokens = create_tokens(
            subject=subject,
            user_id=user.id,
            is_admin=user.is_admin,
        )

        logger.info(f"Token refreshed for user: {user.username}")

        return TokenResponse(**tokens)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user
    """
    return UserResponse.from_orm(current_user)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current user from JWT token
    """
    try:
        payload = decode_token(token)
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# OAuth2 scheme for OpenAPI/Swagger
from fastapi.security import HTTPBearer

oauth2_scheme = HTTPBearer()
