from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


if TYPE_CHECKING:
    from app.models.source import Source


class Document(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "documents"

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    mime_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    language: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    content_hash: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    original_content: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary,
        nullable=True,
    )

    source: Mapped["Source"] = relationship(
        "Source",
        foreign_keys=[source_id],
    )


class DocumentChunk(
    Base,
    UUIDPrimaryKeyMixin,
):
    __tablename__ = "document_chunks"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    page_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    paragraph_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    char_start: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    char_end: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    document: Mapped["Document"] = relationship(
        "Document",
        foreign_keys=[document_id],
    )
