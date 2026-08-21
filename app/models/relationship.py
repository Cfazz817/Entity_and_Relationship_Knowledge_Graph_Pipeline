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
    from app.models.entity import Entity
    from app.models.temporal import TemporalValue


class RelationshipType(
    Base,
    UUIDPrimaryKeyMixin,
):
    __tablename__ = "relationship_types"

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    inverse_type_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("relationship_types.id"),
        nullable=True,
    )

    symmetric: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    inverse_type: Mapped[Optional["RelationshipType"]] = relationship(
        "RelationshipType",
        remote_side="RelationshipType.id",
        foreign_keys=[inverse_type_id],
        uselist=False,
    )


class Relationship(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "relationships"

    source_entity_id: Mapped[UUID] = mapped_column(
        ForeignKey("entities.id"),
        nullable=False,
        index=True,
    )

    target_entity_id: Mapped[UUID] = mapped_column(
        ForeignKey("entities.id"),
        nullable=False,
        index=True,
    )

    relationship_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("relationship_types.id"),
        nullable=False,
        index=True,
    )

    valid_time_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("temporal_values.id"),
        nullable=True,
    )

    source_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[source_entity_id],
        back_populates="outgoing_relationships",
    )

    target_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[target_entity_id],
        back_populates="incoming_relationships",
    )

    relationship_type: Mapped["RelationshipType"] = relationship(
        "RelationshipType",
        foreign_keys=[relationship_type_id],
    )

    valid_time: Mapped[Optional["TemporalValue"]] = relationship(
        "TemporalValue",
        foreign_keys=[valid_time_id],
    )
