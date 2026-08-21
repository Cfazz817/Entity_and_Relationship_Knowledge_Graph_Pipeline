from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class Source(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "sources"

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    url: Mapped[Optional[str]] = mapped_column(
        Text,
        unique=True,
        nullable=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    author: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    publisher: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    publication_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    metadata_: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
