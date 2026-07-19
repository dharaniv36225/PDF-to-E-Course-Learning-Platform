"""Generic repository implementing common CRUD operations."""
from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import ColumnElement

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Reusable CRUD repository parameterised by an ORM model."""

    def __init__(self, model: type[ModelType], db: Session) -> None:
        self.model = model
        self.db = db

    def get(self, obj_id: uuid.UUID) -> ModelType | None:
        return self.db.get(self.model, obj_id)

    def find_one(
        self,
        *criteria: ColumnElement[bool],
        options: Sequence[ExecutableOption] | None = None,
    ) -> ModelType | None:
        """Return a single row matching ``criteria`` (or ``None``)."""
        stmt = select(self.model).where(*criteria)
        if options:
            stmt = stmt.options(*options)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_all(
        self,
        *criteria: ColumnElement[bool],
        order_by: Sequence[ColumnElement] | ColumnElement | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ModelType]:
        """Return all rows matching ``criteria`` with optional ordering/paging."""
        stmt = select(self.model).where(*criteria)
        if order_by is not None:
            order = order_by if isinstance(order_by, list | tuple) else (order_by,)
            stmt = stmt.order_by(*order)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        return self.db.execute(stmt).scalars().all()

    def count_where(self, *criteria: ColumnElement[bool]) -> int:
        """Count rows matching ``criteria`` (all rows when none given)."""
        stmt = select(func.count()).select_from(self.model).where(*criteria)
        return self.db.execute(stmt).scalar_one()

    def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        return self.find_all(limit=limit, offset=offset)

    def count(self) -> int:
        return self.count_where()

    def add(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()
        return obj

    def add_all(self, objs: list[ModelType]) -> list[ModelType]:
        self.db.add_all(objs)
        self.db.flush()
        return objs

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()
