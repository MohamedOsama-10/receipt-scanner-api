import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.expense import ScanResult, ExpenseCreate, ExpenseOut
from app.services.scanner import scan_receipt_bytes
from app.services.expense_service import create_expense

router = APIRouter(prefix="/scan", tags=["Receipt Scanner"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_SIZE_MB = 10


@router.post(
    "/",
    response_model=ScanResult,
    summary="Scan a receipt image (preview only — does not save)",
)
async def scan_receipt(
    file: UploadFile = File(..., description="Receipt image (JPG, PNG, WEBP)"),
):
    """
    Upload a receipt image → get back AI-extracted JSON.
    Does NOT save to the database. Use /scan/save to do both.
    """
    _validate_file(file)
    image_bytes = await file.read()
    _validate_size(image_bytes)

    try:
        result = await scan_receipt_bytes(image_bytes, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI scanner error: {str(e)}",
        )

    return result


@router.post(
    "/save",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Scan a receipt and save it as an expense",
)
async def scan_and_save(
    file: UploadFile = File(..., description="Receipt image (JPG, PNG, WEBP)"),
    db: Session = Depends(get_db),
):
    """
    Upload a receipt → AI scans it → expense saved to DB in one step.
    The image is stored in the uploads/ folder.
    """
    _validate_file(file)
    image_bytes = await file.read()
    _validate_size(image_bytes)

    # Save the image to disk
    ext = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = Path(settings.UPLOAD_DIR) / filename
    save_path.write_bytes(image_bytes)

    # Run AI scan
    try:
        scan = await scan_receipt_bytes(image_bytes, file.content_type)
    except Exception as e:
        save_path.unlink(missing_ok=True)  # clean up orphaned image
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI scanner error: {str(e)}",
        )

    # Persist to DB
    expense_data = ExpenseCreate(
        merchant=scan.merchant,
        total=scan.total,
        currency=scan.currency,
        date=scan.date,
        category=scan.category,
    )
    expense = create_expense(db, expense_data, image_path=str(save_path))
    return expense


# ── helpers ──────────────────────────────────────────────────────────────────

def _validate_file(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Use JPG, PNG, or WEBP.",
        )


def _validate_size(data: bytes):
    size_mb = len(data) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({size_mb:.1f} MB). Max is {MAX_SIZE_MB} MB.",
        )
