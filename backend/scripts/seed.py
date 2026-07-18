"""Seed the database with a demo user and a sample course.

Usage:
    python -m scripts.seed
"""
from __future__ import annotations

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.course import Chapter, Course, Lesson
from app.models.upload import Upload
from app.models.user import User

DEMO_EMAIL = "demo@ecourse.dev"
DEMO_PASSWORD = "demopassword123"


def seed() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == DEMO_EMAIL).one_or_none()
        if user is None:
            user = User(
                email=DEMO_EMAIL,
                full_name="Demo Learner",
                hashed_password=hash_password(DEMO_PASSWORD),
                auth_provider="email",
                is_verified=True,
            )
            db.add(user)
            db.flush()
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print("Demo user already exists")

        upload = Upload(
            user_id=user.id,
            filename="sample.pdf",
            original_filename="Introduction to Machine Learning.pdf",
            content_type="application/pdf",
            size_bytes=123456,
            page_count=12,
            storage_path="seed/sample.pdf",
            storage_provider="local",
            extracted_text="Sample extracted text about machine learning fundamentals.",
            status="ready",
        )
        db.add(upload)
        db.flush()

        course = Course(
            user_id=user.id,
            upload_id=upload.id,
            title="Introduction to Machine Learning",
            description="A beginner-friendly course generated from a sample PDF.",
            difficulty="beginner",
            estimated_minutes=120,
            learning_objectives=["Understand ML basics", "Distinguish supervised vs unsupervised"],
            prerequisites=["Basic Python", "High-school math"],
            tags=["ml", "ai", "beginner"],
            status="ready",
        )
        db.add(course)
        db.flush()

        chapter = Chapter(
            course_id=course.id,
            title="Foundations of Machine Learning",
            summary="Core concepts and terminology.",
            order_index=0,
        )
        db.add(chapter)
        db.flush()

        db.add(
            Lesson(
                chapter_id=chapter.id,
                title="What is Machine Learning?",
                explanation="Machine learning is a field of AI focused on learning from data.",
                examples="Spam filters, recommendation systems.",
                important_notes="ML models require quality data.",
                summary="ML learns patterns from data to make predictions.",
                content="Machine learning is a field of AI focused on learning from data.",
                key_takeaways=["ML learns from data", "Data quality matters"],
                estimated_minutes=10,
                order_index=0,
            )
        )
        db.commit()
        print(f"Seeded sample course: {course.title} ({course.id})")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
