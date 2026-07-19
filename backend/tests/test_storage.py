import os

import app.utils.storage as storage_module
from app.core.config import settings
from app.utils.storage import StorageService, get_storage


def _local_service(tmp_path, monkeypatch) -> StorageService:
    monkeypatch.setattr(settings, "USE_SUPABASE_STORAGE", False, raising=False)
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path), raising=False)
    return StorageService()


def test_save_writes_local_file(tmp_path, monkeypatch):
    service = _local_service(tmp_path, monkeypatch)
    path, provider = service.save(b"pdf-bytes", "My Report.pdf", "user-1")

    assert provider == "local"
    assert os.path.isfile(path)
    with open(path, "rb") as fh:
        assert fh.read() == b"pdf-bytes"
    # Original filename is preserved (sanitized) in the stored name.
    assert path.endswith("_My Report.pdf")


def test_save_generates_unique_names(tmp_path, monkeypatch):
    service = _local_service(tmp_path, monkeypatch)
    first, _ = service.save(b"a", "doc.pdf", "user-1")
    second, _ = service.save(b"b", "doc.pdf", "user-1")

    assert first != second


def test_delete_removes_existing_local_file(tmp_path, monkeypatch):
    service = _local_service(tmp_path, monkeypatch)
    path, provider = service.save(b"data", "doc.pdf", "user-1")

    service.delete(path, provider)
    assert not os.path.exists(path)


def test_delete_missing_file_is_noop(tmp_path, monkeypatch):
    service = _local_service(tmp_path, monkeypatch)
    # Should not raise even though the file does not exist.
    service.delete(str(tmp_path / "missing.pdf"), "local")


def test_get_storage_returns_singleton(monkeypatch):
    monkeypatch.setattr(storage_module, "_storage", None)
    first = get_storage()
    second = get_storage()
    assert first is second
