"""Upload service: persist PDF, extract text, chunk, embed and index."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.ai.text_splitter import split_pages
from app.ai.vector_store import get_vector_store
from app.core.config import settings
from app.core.errors import NotFoundError
from app.core.logging import get_logger
from app.models.embedding import Embedding
from app.models.upload import Upload
from app.repositories.upload import UploadRepository
from app.utils.pdf import extract_pages, pages_to_text, validate_pdf
from app.utils.storage import get_storage

logger = get_logger(__name__)


class UploadService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.uploads = UploadRepository(db)
        self.storage = get_storage()
        self.vector_store = get_vector_store()

    def create_upload(
        self, user_id: uuid.UUID, data: bytes, original_filename: str, content_type: str
    ) -> Upload:
        validate_pdf(
            data,
            content_type=content_type,
            filename=original_filename,
            max_bytes=settings.MAX_UPLOAD_MB * 1024 * 1024,
        )

        storage_path, provider = self.storage.save(data, original_filename, str(user_id))
        upload = Upload(
            user_id=user_id,
            filename=storage_path.split("/")[-1],
            original_filename=original_filename,
            content_type=content_type or "application/pdf",
            size_bytes=len(data),
            storage_path=storage_path,
            storage_provider=provider,
            status="processing",
        )
        self.uploads.add(upload)
        self.uploads.commit()

        try:
            self._process(upload, data)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Upload processing failed: %s", exc)
            upload.status = "failed"
            upload.error_message = str(exc)
            self.uploads.commit()
            raise
        return upload

    def _process(self, upload: Upload, data: bytes) -> None:
        pages, page_count = extract_pages(data)
        full_text = pages_to_text(pages)
        upload.page_count = page_count
        upload.extracted_text = full_text

        chunks = split_pages(pages)
        if chunks:
            self.vector_store.add_chunks(str(upload.id), chunks)
            embeddings = [
                Embedding(
                    upload_id=upload.id,
                    chunk_index=chunk["chunk_index"],
                    page_number=chunk.get("page_number"),
                    content=chunk["content"],
                    vector_id=f"{upload.id}:{chunk['chunk_index']}",
                    collection_name=self.vector_store.collection_name(str(upload.id)),
                )
                for chunk in chunks
            ]
            self.db.add_all(embeddings)
        upload.status = "ready"
        self.uploads.commit()

    def list_uploads(self, user_id: uuid.UUID) -> Sequence[Upload]:
        return self.uploads.list_for_user(user_id)

    def get_upload(self, upload_id: uuid.UUID, user_id: uuid.UUID) -> Upload:
        upload = self.uploads.get_for_user(upload_id, user_id)
        if not upload:
            raise NotFoundError("Upload not found")
        return upload

    def delete_upload(self, upload_id: uuid.UUID, user_id: uuid.UUID) -> None:
        upload = self.get_upload(upload_id, user_id)
        self.vector_store.delete_collection(str(upload.id))
        self.storage.delete(upload.storage_path, upload.storage_provider)
        self.uploads.delete(upload)
        self.uploads.commit()
