"""Embedding metadata model.

Vector values themselves live in ChromaDB; this table stores the metadata needed
to map a chunk back to its source document and location for citations.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.upload import Upload


class Embedding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "embeddings"

    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploads.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    vector_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    collection_name: Mapped[str] = mapped_column(String(255), nullable=False)

    upload: Mapped[Upload] = relationship(back_populates="embeddings")
