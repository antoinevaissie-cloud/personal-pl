import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from auth import get_password_hash, verify_password, create_access_token
from jose import jwt
from config import settings

client = TestClient(app)

class TestAuthentication:
    def test_password_hashing(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_create_access_token(self):
        data = {"sub": "testuser"}
        token = create_access_token(data)
        decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded
    
    @patch('auth.execute_query')
    @patch('auth.execute_update')
    def test_register_user(self, mock_update, mock_query):
        mock_query.return_value = []  # No existing user
        
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert mock_update.called
    
    @patch('auth.execute_query')
    def test_register_duplicate_user(self, mock_query):
        mock_query.return_value = [("existing-id",)]  # User exists
        
        response = client.post("/api/auth/register", json={
            "username": "existinguser",
            "email": "existing@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    @patch('auth.execute_query')
    def test_login_success(self, mock_query):
        hashed_password = get_password_hash("password123")
        mock_query.return_value = [(
            "user-id",
            "testuser",
            "test@example.com",
            hashed_password,
            True
        )]
        
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @patch('auth.execute_query')
    def test_login_invalid_credentials(self, mock_query):
        mock_query.return_value = []  # User not found
        
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    @patch('auth.execute_query')
    def test_get_current_user(self, mock_query):
        mock_query.return_value = [(
            "user-id",
            "testuser",
            "test@example.com",
            True
        )]
        
        token = create_access_token({"sub": "testuser"})
        
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_get_current_user_invalid_token(self):
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalidtoken"
        })
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]