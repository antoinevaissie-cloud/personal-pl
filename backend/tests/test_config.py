import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Settings

class TestConfiguration:
    def test_default_settings(self):
        settings = Settings()
        assert settings.app_name == "Personal P&L"
        assert settings.debug == False
        assert settings.algorithm == "HS256"
        assert settings.max_upload_size == 10 * 1024 * 1024
        assert settings.allowed_extensions == [".csv", ".CSV"]
    
    def test_cors_origins(self):
        settings = Settings()
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://127.0.0.1:3000" in settings.cors_origins
    
    def test_env_override(self):
        os.environ["DEBUG"] = "true"
        os.environ["SECRET_KEY"] = "test-secret-key"
        os.environ["LOG_LEVEL"] = "DEBUG"
        
        settings = Settings()
        assert settings.debug == True
        assert settings.secret_key == "test-secret-key"
        assert settings.log_level == "DEBUG"
        
        # Cleanup
        del os.environ["DEBUG"]
        del os.environ["SECRET_KEY"]
        del os.environ["LOG_LEVEL"]
    
    def test_cors_origins_parsing(self):
        os.environ["CORS_ORIGINS"] = "http://example.com,http://app.example.com"
        settings = Settings()
        assert settings.cors_origins == ["http://example.com", "http://app.example.com"]
        del os.environ["CORS_ORIGINS"]