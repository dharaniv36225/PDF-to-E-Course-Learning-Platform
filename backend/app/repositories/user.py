"""User repository."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_supabase_id(self, supabase_user_id: str) -> User | None:
        stmt = select(User).where(User.supabase_user_id == supabase_user_id)
        return self.db.execute(stmt).scalar_one_or_none()
