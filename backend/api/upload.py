# backend/api/upload.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import date
from typing import Literal, Dict, Any
import os

from etl.common import (
    sha256_bytes, detect_period, upsert_import, insert_raw_rows, check_duplicate_import
)
from etl.bnp import load_bnp_csv
from etl.boursorama import load_boursorama_csv
from etl.revolut import load_revolut_csv
from db.duck import get_conn, execute_update
from services.rollup import rebuild_rollup_monthly
from auth import get_current_user
from config import settings
from logger import logger
from exceptions import ValidationError, FileProcessingError, DuplicateError

router = APIRouter()

Bank = Literal["BNP", "Boursorama", "Revolut"]

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_extensions:
        raise ValidationError(
            f"Invalid file extension. Allowed: {settings.allowed_extensions}",
            details={"filename": file.filename, "extension": file_ext}
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.max_upload_size:
        raise ValidationError(
            f"File too large. Maximum size: {settings.max_upload_size} bytes",
            details={"filename": file.filename, "size": file_size}
        )
    
    if file_size == 0:
        raise ValidationError(
            "File is empty",
            details={"filename": file.filename}
        )

@router.post("/api/upload")
async def upload_csv(
    bank: Bank = Form(...),
    period_month: str = Form(...),  # 'YYYY-MM'
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload and process bank CSV file"""
    try:
        # Validate file
        validate_file(file)
        
        content = await file.read()
        period = detect_period(period_month)
        digest = sha256_bytes(content)
        user_id = current_user["id"]
        
        logger.info(
            "csv_upload_started",
            bank=bank,
            period=period.isoformat(),
            filename=file.filename,
            user=current_user["username"]
        )
        
        # Check for duplicate
        duplicate = check_duplicate_import(bank, period, digest, user_id)
        if duplicate:
            logger.warning(
                "duplicate_file_detected",
                bank=bank,
                period=period.isoformat(),
                digest=digest,
                user=current_user["username"]
            )
            raise DuplicateError(
                "This file has already been imported",
                details={
                    "bank": bank,
                    "period_month": period.isoformat(),
                    "filename": file.filename
                }
            )
        
        # Load rows by bank
        try:
            if bank == "BNP":
                rows = load_bnp_csv(content)
            elif bank == "Boursorama":
                rows = load_boursorama_csv(content)
            elif bank == "Revolut":
                rows = load_revolut_csv(content)
            else:
                raise ValidationError(f"Unsupported bank: {bank}")
        except Exception as e:
            logger.error(
                "csv_parsing_failed",
                bank=bank,
                error=str(e),
                user=current_user["username"]
            )
            raise FileProcessingError(
                f"Failed to parse CSV file: {str(e)}",
                details={"bank": bank, "filename": file.filename}
            )
        
        # Insert data
        import_id = upsert_import(bank, period, digest, file.filename, user_id)
        count = insert_raw_rows(rows, import_id, bank, user_id)
        
        logger.info(
            "csv_upload_completed",
            bank=bank,
            period=period.isoformat(),
            rows_inserted=count,
            import_id=import_id,
            user=current_user["username"]
        )
        
        return {
            "success": True,
            "import_batch_id": import_id,
            "rows": count,
            "bank": bank,
            "period_month": period.isoformat()
        }
        
    except (ValidationError, FileProcessingError, DuplicateError):
        raise
    except Exception as e:
        logger.exception("unexpected_upload_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process upload")

# Import commit endpoint moved to api/import_commit.py