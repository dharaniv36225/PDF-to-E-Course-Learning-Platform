"""Integration test for DashboardService (requires the configured database)."""
import uuid

from app.db.session import SessionLocal
from app.models.course import Course
from app.models.upload import Upload
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import DashboardService


def test_get_stats_with_a_course_validates_against_response_model() -> None:
    """A user with >=1 course must produce a response that validates as DashboardStats.

    Regression: recent_courses were built as nested dicts and failed validation
    (HTTP 500) whenever the user had any course.
    """
    db = SessionLocal()
    user = User(email=f"dash-{uuid.uuid4()}@test.dev", full_name="Dash Tester", auth_provider="email")
    db.add(user)
    db.flush()

    upload = Upload(
        user_id=user.id,
        filename="doc.pdf",
        original_filename="doc.pdf",
        storage_path="/tmp/doc.pdf",
        status="ready",
    )
    db.add(upload)
    db.flush()

    course = Course(
        user_id=user.id,
        upload_id=upload.id,
        title="Test Course",
        difficulty="beginner",
        status="ready",
    )
    db.add(course)
    db.commit()

    try:
        stats = DashboardService(db).get_stats(user.id)
        assert stats["total_courses"] == 1
        assert len(stats["recent_courses"]) == 1
        # Must not raise — proves the shape matches the endpoint's response_model.
        validated = DashboardStats.model_validate(stats)
        assert validated.recent_courses[0].title == "Test Course"
        assert validated.recent_courses[0].completion_percent == 0
    finally:
        db.delete(user)  # cascades to upload + course
        db.commit()
        db.close()
