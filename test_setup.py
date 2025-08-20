#!/usr/bin/env python
"""Test script to verify the setup is working correctly"""

import sys
import os
sys.path.append('backend')

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import fastapi
        import duckdb
        import pandas
        import pydantic
        import structlog
        from jose import jwt
        from passlib.context import CryptContext
        print("✅ All Python packages imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from config import settings
        print(f"✅ Configuration loaded")
        print(f"   App Name: {settings.app_name}")
        print(f"   Debug: {settings.debug}")
        print(f"   CORS Origins: {settings.cors_origins}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    return True

def test_database():
    """Test database connection"""
    print("\nTesting database...")
    try:
        from db.duck import get_conn
        conn = get_conn()
        
        # Check tables exist
        tables = [r[0] for r in conn.execute("SHOW TABLES").fetchall()]
        required_tables = ['users', 'imports', 'transactions', 'transactions_raw']
        
        for table in required_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
                return False
                
        # Check users table structure
        columns = conn.execute("DESCRIBE users").fetchall()
        print(f"✅ Users table has {len(columns)} columns")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    return True

def test_auth():
    """Test authentication functions"""
    print("\nTesting authentication...")
    try:
        from auth import get_password_hash, verify_password, create_access_token
        from jose import jwt
        from config import settings
        
        # Test password hashing
        password = "testpass123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        print("✅ Password hashing works")
        
        # Test token creation
        token = create_access_token({"sub": "testuser"})
        decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert decoded["sub"] == "testuser"
        print("✅ JWT token creation works")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Personal P&L Setup Verification")
    print("=" * 60)
    
    all_passed = True
    all_passed &= test_imports()
    all_passed &= test_config()
    all_passed &= test_database()
    all_passed &= test_auth()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure")
        print("2. Run 'make backend' to start the API server")
        print("3. Run 'make frontend' to start the web interface")
        print("4. Visit http://localhost:3000 to use the application")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()