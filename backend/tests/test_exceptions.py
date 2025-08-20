import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from exceptions import (
    PLException, ValidationError, AuthenticationError,
    AuthorizationError, NotFoundError, DuplicateError,
    FileProcessingError, DatabaseError
)

client = TestClient(app)

class TestExceptions:
    def test_pl_exception_base(self):
        exc = PLException("Test error", status_code=500, details={"key": "value"})
        assert exc.message == "Test error"
        assert exc.status_code == 500
        assert exc.details == {"key": "value"}
    
    def test_validation_error(self):
        exc = ValidationError("Invalid input", details={"field": "email"})
        assert exc.message == "Invalid input"
        assert exc.status_code == 400
        assert exc.details == {"field": "email"}
    
    def test_authentication_error(self):
        exc = AuthenticationError()
        assert exc.message == "Authentication failed"
        assert exc.status_code == 401
    
    def test_authorization_error(self):
        exc = AuthorizationError("Access denied")
        assert exc.message == "Access denied"
        assert exc.status_code == 403
    
    def test_not_found_error(self):
        exc = NotFoundError("Resource not found")
        assert exc.status_code == 404
    
    def test_duplicate_error(self):
        exc = DuplicateError("Already exists")
        assert exc.status_code == 409
    
    def test_file_processing_error(self):
        exc = FileProcessingError("Failed to parse CSV")
        assert exc.status_code == 422
    
    def test_database_error(self):
        exc = DatabaseError("Connection failed")
        assert exc.status_code == 500