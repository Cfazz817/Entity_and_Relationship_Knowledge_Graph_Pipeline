from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class ExtractionRun(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "extraction_runs"

    chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    model: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    prompt_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    schema_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    raw_response: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )


class EntityMention(
    Base,
    UUIDPrimaryKeyMixin,
):
    __tablename__ = "entity_mentions"

    entity_id: Mapped[UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    surface_text: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    start_char: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )

    end_char: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )

    confidence: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )


class RelationshipAssertion(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "relationship_assertions"

    relationship_id: Mapped[UUID] = mapped_column(
        ForeignKey("relationships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    extraction_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    confidence: Mapped[float] = mapped_column(
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    evidence_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
