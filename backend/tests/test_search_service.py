"""Integration tests for SearchService (requires the configured database)."""
import app.services.search_service as search_service_module
from app.services.search_service import SearchService


class _FakeVectorStore:
    def __init__(self, chunks=None, error=None):
        self.chunks = chunks or []
        self.error = error

    def query(self, upload_id, query_text, top_k=4):
        if self.error is not None:
            raise self.error
        return self.chunks


def _service(db, monkeypatch, vector_store):
    monkeypatch.setattr(search_service_module, "get_vector_store", lambda: vector_store)
    return SearchService(db)


def test_keyword_search_matches_course_title(db, user, make_course, monkeypatch):
    make_course(title="Quantum Physics Basics")
    service = _service(db, monkeypatch, _FakeVectorStore())

    result = service.search(user.id, "Quantum")
    titles = [r["title"] for r in result["keyword_results"] if r["type"] == "course"]
    assert "Quantum Physics Basics" in titles
    assert result["query"] == "Quantum"


def test_keyword_search_matches_lesson_content(db, user, make_course, make_lesson, monkeypatch):
    course = make_course(title="Unrelated Course")
    make_lesson(course, title="Photosynthesis", content="Plants convert light energy.")
    service = _service(db, monkeypatch, _FakeVectorStore())

    result = service.search(user.id, "Photosynthesis")
    lesson_hits = [r for r in result["keyword_results"] if r["type"] == "lesson"]
    assert any(r["title"] == "Photosynthesis" for r in lesson_hits)


def test_semantic_results_are_sorted_by_score(db, user, make_course, monkeypatch):
    course = make_course(title="Course With Vectors")
    vector_store = _FakeVectorStore(
        chunks=[
            {"content": "low relevance", "score": 0.2},
            {"content": "high relevance", "score": 0.9},
        ]
    )
    service = _service(db, monkeypatch, vector_store)

    result = service.search(user.id, "anything", course_id=course.id)
    semantic = result["semantic_results"]
    assert [r["snippet"] for r in semantic] == ["high relevance", "low relevance"]
    assert all(r["type"] == "document" for r in semantic)


def test_semantic_search_tolerates_vector_store_errors(db, user, make_course, monkeypatch):
    course = make_course()
    service = _service(db, monkeypatch, _FakeVectorStore(error=RuntimeError("chroma down")))

    result = service.search(user.id, "anything", course_id=course.id)
    assert result["semantic_results"] == []
