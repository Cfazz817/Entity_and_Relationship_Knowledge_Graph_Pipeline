from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


if TYPE_CHECKING:
    from app.models.temporal import TemporalValue


class InstitutionCategory(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "institution_categories"

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )


class Institution(Base):
    __tablename__ = "institutions"

    entity_id: Mapped[UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        primary_key=True,
    )

    category_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("institution_categories.id"),
        nullable=True,
        index=True,
    )

    founding_time_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("temporal_values.id"),
        nullable=True,
    )

    dissolution_time_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("temporal_values.id"),
        nullable=True,
    )

    category: Mapped[Optional["InstitutionCategory"]] = relationship(
        "InstitutionCategory",
        foreign_keys=[category_id],
    )

    founding_time: Mapped[Optional["TemporalValue"]] = relationship(
        "TemporalValue",
        foreign_keys=[founding_time_id],
    )

    dissolution_time: Mapped[Optional["TemporalValue"]] = relationship(
        "TemporalValue",
        foreign_keys=[dissolution_time_id],
    )
