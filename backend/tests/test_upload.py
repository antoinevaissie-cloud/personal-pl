import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, Mock
import sys
import os
from io import BytesIO
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from auth import create_access_token
from datetime import date

client = TestClient(app)

class TestUploadAPI:
    @pytest.fixture
    def auth_headers(self):
        token = create_access_token({"sub": "testuser"})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def mock_current_user(self):
        return {
            "id": "test-user-id",
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True
        }
    
    @patch('api.upload.get_current_user')
    @patch('api.upload.check_duplicate_import')
    @patch('api.upload.upsert_import')
    @patch('api.upload.insert_raw_rows')
    @patch('api.upload.load_bnp_csv')
    def test_upload_csv_success(self, mock_load_bnp, mock_insert, mock_upsert, 
                                mock_duplicate, mock_user, mock_current_user):
        mock_user.return_value = mock_current_user
        mock_duplicate.return_value = False
        mock_upsert.return_value = "import-id-123"
        mock_insert.return_value = 10
        mock_load_bnp.return_value = [
            {"ts": "2025-01-01", "description": "Test", "amount": 100.0}
        ]
        
        csv_content = b"Date,Description,Amount\n2025-01-01,Test,100.00"
        
        response = client.post(
            "/api/upload",
            data={
                "bank": "BNP",
                "period_month": "2025-01"
            },
            files={"file": ("test.csv", csv_content, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["rows"] == 10
        assert data["bank"] == "BNP"
    
    @patch('api.upload.get_current_user')
    def test_upload_invalid_file_extension(self, mock_user, mock_current_user):
        mock_user.return_value = mock_current_user
        
        response = client.post(
            "/api/upload",
            data={
                "bank": "BNP",
                "period_month": "2025-01"
            },
            files={"file": ("test.txt", b"invalid", "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Invalid file extension" in response.json()["error"]
    
    @patch('api.upload.get_current_user')
    def test_upload_empty_file(self, mock_user, mock_current_user):
        mock_user.return_value = mock_current_user
        
        response = client.post(
            "/api/upload",
            data={
                "bank": "BNP",
                "period_month": "2025-01"
            },
            files={"file": ("test.csv", b"", "text/csv")}
        )
        
        assert response.status_code == 400
        assert "File is empty" in response.json()["error"]
    
    @patch('api.upload.get_current_user')
    @patch('api.upload.check_duplicate_import')
    def test_upload_duplicate_file(self, mock_duplicate, mock_user, mock_current_user):
        mock_user.return_value = mock_current_user
        mock_duplicate.return_value = True
        
        csv_content = b"Date,Description,Amount\n2025-01-01,Test,100.00"
        
        response = client.post(
            "/api/upload",
            data={
                "bank": "BNP",
                "period_month": "2025-01"
            },
            files={"file": ("test.csv", csv_content, "text/csv")}
        )
        
        assert response.status_code == 409
        assert "already been imported" in response.json()["error"]
    
    @patch('api.upload.get_current_user')
    @patch('api.upload.get_conn')
    @patch('api.upload.rebuild_rollup_monthly')
    def test_import_commit_success(self, mock_rollup, mock_conn, mock_user, mock_current_user):
        mock_user.return_value = mock_current_user
        mock_db = MagicMock()
        mock_conn.return_value = mock_db
        mock_rollup.return_value = {"rows_inserted": 25}
        
        response = client.post(
            "/api/import/commit",
            json={"period_month": "2025-01"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["period_month"] == "2025-01-01"
        assert mock_db.execute.called
        assert mock_db.commit.called
    
    def test_upload_without_auth(self):
        response = client.post(
            "/api/upload",
            data={
                "bank": "BNP",
                "period_month": "2025-01"
            },
            files={"file": ("test.csv", b"test", "text/csv")}
        )
        
        assert response.status_code == 403  # Forbidden without auth