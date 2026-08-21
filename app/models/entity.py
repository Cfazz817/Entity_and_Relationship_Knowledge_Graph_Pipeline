from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from pgvector.sqlalchemy import Vector


if TYPE_CHECKING:
    from app.models.relationship import Relationship
    from app.models.temporal import TemporalValue


class EntityType(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "entity_types"

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )


class Entity(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "entities"

    entity_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("entity_types.id"),
        nullable=False,
        index=True,
    )

    primary_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    normalized_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(3072),
        nullable=True,
    )

    outgoing_relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan",
    )

    incoming_relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan",
    )


class Person(Base):
    __tablename__ = "people"

    entity_id: Mapped[UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        primary_key=True,
    )

    birth_time_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("temporal_values.id"),
        nullable=True,
    )

    death_time_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("temporal_values.id"),
        nullable=True,
    )

    is_alive: Mapped[Optional[bool]] = mapped_column(
        nullable=True,
    )

    birth_time: Mapped[Optional["TemporalValue"]] = relationship(
        "TemporalValue",
        foreign_keys=[birth_time_id],
    )

    death_time: Mapped[Optional["TemporalValue"]] = relationship(
        "TemporalValue",
        foreign_keys=[death_time_id],
    )
