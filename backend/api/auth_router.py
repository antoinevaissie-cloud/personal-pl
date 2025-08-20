from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from auth import (
    Token, UserCreate, UserLogin, User,
    create_user, authenticate_user, create_access_token, get_current_user
)
from config import settings
from logger import logger

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register a new user"""
    try:
        created_user = create_user(user)
        logger.info("user_registered", username=user.username)
        return created_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error("registration_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """Login and receive access token"""
    user = authenticate_user(user_login.username, user_login.password)
    if not user:
        logger.warning("login_failed", username=user_login.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    logger.info("user_logged_in", username=user["username"])
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout (client should discard token)"""
    logger.info("user_logged_out", username=current_user["username"])
    return {"message": "Successfully logged out"}