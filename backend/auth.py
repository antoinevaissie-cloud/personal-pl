from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from config import settings
from db.duck import execute_query, execute_update
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool = True
    created_at: Optional[datetime] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_user(user: UserCreate) -> Dict[str, Any]:
    # Check if user exists
    existing = execute_query(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        [user.username, user.email]
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    
    execute_update("""
        INSERT INTO users (id, username, email, password_hash, is_active, created_at)
        VALUES (?, ?, ?, ?, TRUE, now())
    """, [user_id, user.username, user.email, hashed_password])
    
    return {
        "id": str(user_id),
        "username": user.username,
        "email": user.email,
        "is_active": True
    }

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    result = execute_query(
        "SELECT id, username, email, password_hash, is_active FROM users WHERE username = ?",
        [username]
    )
    if not result:
        return None
    
    user = result[0]
    if not verify_password(password, user[3]):
        return None
    
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "is_active": user[4]
    }

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = execute_query(
        "SELECT id, username, email, is_active FROM users WHERE username = ?",
        [username]
    )
    
    if not result:
        raise credentials_exception
    
    user = result[0]
    if not user[3]:  # is_active
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return {
        "id": str(user[0]),
        "username": user[1],
        "email": user[2],
        "is_active": user[3]
    }

# Optional: API key authentication for certain endpoints
async def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
    if settings.api_key and api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key