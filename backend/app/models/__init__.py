"""ORM models package. Import all models so SQLAlchemy metadata is complete."""
from app.db.base import Base
from app.models.chat import ChatMessage, ChatSession
from app.models.course import Chapter, Course, Lesson
from app.models.embedding import Embedding
from app.models.progress import LessonProgress
from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.models.upload import Upload
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "Upload",
    "Course",
    "Chapter",
    "Lesson",
    "LessonProgress",
    "ChatSession",
    "ChatMessage",
    "Quiz",
    "QuizQuestion",
    "QuizAttempt",
    "Embedding",
]
