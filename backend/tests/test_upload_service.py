"""Integration tests for UploadService (requires the configured database)."""
import uuid

import pytest

import app.services.upload_service as upload_service_module
from app.core.config import settings
from app.core.errors import NotFoundError, ValidationAppError
from app.models.embedding import Embedding
from app.services.upload_service import UploadService


class _FakeStorage:
    def __init__(self):
        self.saved = []
        self.deleted = []

    def save(self, data, original_filename, user_id):
        self.saved.append((data, original_filename, user_id))
        return (f"/tmp/{user_id}/stored_{original_filename}", "local")

    def delete(self, storage_path, provider):
        self.deleted.append((storage_path, provider))


class _FakeVectorStore:
    def __init__(self):
        self.added = []
        self.deleted = []

    def add_chunks(self, upload_id, chunks):
        self.added.append((upload_id, chunks))
        return [f"{upload_id}:{c['chunk_index']}" for c in chunks]

    def collection_name(self, upload_id):
        return f"doc_{upload_id}"

    def delete_collection(self, upload_id):
        self.deleted.append(upload_id)


@pytest.fixture
def fakes(monkeypatch):
    storage = _FakeStorage()
    vector_store = _FakeVectorStore()
    monkeypatch.setattr(upload_service_module, "get_storage", lambda: storage)
    monkeypatch.setattr(upload_service_module, "get_vector_store", lambda: vector_store)
    return storage, vector_store


def test_create_upload_rejects_non_pdf(db, user, fakes):
    service = UploadService(db)
    with pytest.raises(ValidationAppError):
        service.create_upload(user.id, b"data", "notes.txt", "text/plain")


def test_create_upload_rejects_oversized_file(db, user, fakes, monkeypatch):
    monkeypatch.setattr(settings, "MAX_UPLOAD_MB", 1, raising=False)
    service = UploadService(db)
    too_big = b"x" * (2 * 1024 * 1024)
    with pytest.raises(ValidationAppError):
        service.create_upload(user.id, too_big, "big.pdf", "application/pdf")


def test_create_upload_processes_and_indexes(db, user, fakes, monkeypatch):
    storage, vector_store = fakes
    pages = [{"page_number": 1, "text": "content"}]
    chunks = [{"content": "content", "chunk_index": 0, "page_number": 1}]
    monkeypatch.setattr(upload_service_module, "extract_pages", lambda data: (pages, 3))
    monkeypatch.setattr(upload_service_module, "pages_to_text", lambda p: "full text")
    monkeypatch.setattr(upload_service_module, "split_pages", lambda p: chunks)

    service = UploadService(db)
    upload = service.create_upload(user.id, b"%PDF-bytes", "doc.pdf", "application/pdf")

    try:
        assert upload.status == "ready"
        assert upload.page_count == 3
        assert upload.extracted_text == "full text"
        assert len(storage.saved) == 1
        assert vector_store.added[0][0] == str(upload.id)

        rows = db.query(Embedding).filter(Embedding.upload_id == upload.id).all()
        assert len(rows) == 1
        assert rows[0].vector_id == f"{upload.id}:0"
    finally:
        db.delete(upload)
        db.commit()


def test_create_upload_marks_failed_on_processing_error(db, user, fakes, monkeypatch):
    def boom(data):
        raise RuntimeError("corrupt pdf")

    monkeypatch.setattr(upload_service_module, "extract_pages", boom)
    service = UploadService(db)

    with pytest.raises(RuntimeError):
        service.create_upload(user.id, b"%PDF", "doc.pdf", "application/pdf")

    upload = service.uploads.list_for_user(user.id)[0]
    try:
        assert upload.status == "failed"
        assert "corrupt pdf" in (upload.error_message or "")
    finally:
        db.delete(upload)
        db.commit()


def test_get_upload_unknown_raises(db, user, fakes):
    service = UploadService(db)
    with pytest.raises(NotFoundError):
        service.get_upload(uuid.uuid4(), user.id)


def test_delete_upload_cleans_vector_and_storage(db, user, fakes, make_upload):
    storage, vector_store = fakes
    upload = make_upload(storage_path="/tmp/x/doc.pdf", storage_provider="local")
    service = UploadService(db)

    service.delete_upload(upload.id, user.id)

    assert vector_store.deleted == [str(upload.id)]
    assert storage.deleted == [("/tmp/x/doc.pdf", "local")]
    assert service.uploads.get_for_user(upload.id, user.id) is None
