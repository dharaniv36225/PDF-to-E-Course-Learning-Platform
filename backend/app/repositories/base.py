"""Generic repository implementing common CRUD operations."""
from __future__ import annotations

import builtins
import uuid
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Reusable CRUD repository parameterised by an ORM model."""

    def __init__(self, model: type[ModelType], db: Session) -> None:
        self.model = model
        self.db = db

    def get(self, obj_id: uuid.UUID) -> ModelType | None:
        return self.db.get(self.model, obj_id)

    def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        stmt = select(self.model).limit(limit).offset(offset)
        return self.db.execute(stmt).scalars().all()

    def count(self) -> int:
        return self.db.execute(select(func.count()).select_from(self.model)).scalar_one()

    def add(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()
        return obj

    def add_all(self, objs: builtins.list[ModelType]) -> builtins.list[ModelType]:
        self.db.add_all(objs)
        self.db.flush()
        return objs

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()
