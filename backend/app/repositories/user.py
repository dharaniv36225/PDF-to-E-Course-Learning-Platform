"""User repository."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        return self.find_one(User.email == email.lower())

    def get_by_supabase_id(self, supabase_user_id: str) -> User | None:
        return self.find_one(User.supabase_user_id == supabase_user_id)
