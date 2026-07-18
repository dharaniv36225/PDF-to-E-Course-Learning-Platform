"""PDF upload routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Message
from app.schemas.upload import UploadDetail, UploadRead
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", response_model=list[UploadRead], status_code=status.HTTP_201_CREATED)
async def upload_pdfs(
    files: list[UploadFile] = File(..., description="One or more PDF files"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[UploadRead]:
    """Upload one or more PDFs. Each is stored, text-extracted, chunked and embedded."""
    service = UploadService(db)
    created = []
    for file in files:
        data = await file.read()
        upload = service.create_upload(
            current_user.id, data, file.filename or "document.pdf", file.content_type or "application/pdf"
        )
        created.append(upload)
    return created


@router.get("", response_model=list[UploadRead])
def list_uploads(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[UploadRead]:
    return list(UploadService(db).list_uploads(current_user.id))


@router.get("/{upload_id}", response_model=UploadDetail)
def get_upload(
    upload_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UploadDetail:
    return UploadService(db).get_upload(upload_id, current_user.id)


@router.delete("/{upload_id}", response_model=Message)
def delete_upload(
    upload_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    UploadService(db).delete_upload(upload_id, current_user.id)
    return Message(message="Upload deleted")
