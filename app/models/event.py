from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


if TYPE_CHECKING:
    from app.models.temporal import TemporalValue


class Event(Base):
    __tablename__ = "events"

    entity_id: Mapped[UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        primary_key=True,
    )

    start_time_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("temporal_values.id"),
        nullable=True,
    )

    end_time_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("temporal_values.id"),
        nullable=True,
    )

    event_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    start_time: Mapped[Optional["TemporalValue"]] = relationship(
        "TemporalValue",
        foreign_keys=[start_time_id],
    )

    end_time: Mapped[Optional["TemporalValue"]] = relationship(
        "TemporalValue",
        foreign_keys=[end_time_id],
    )
