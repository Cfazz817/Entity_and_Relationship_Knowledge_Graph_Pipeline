from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class LocationType(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "location_types"

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )


class LocationRegion(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "location_regions"

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )


class Location(Base):
    __tablename__ = "locations"

    entity_id: Mapped[UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        primary_key=True,
    )

    location_type_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("location_types.id"),
        nullable=True,
        index=True,
    )

    location_region_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("location_regions.id"),
        nullable=True,
        index=True,
    )

    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    latitude: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    longitude: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    location_type: Mapped[Optional["LocationType"]] = relationship(
        "LocationType",
        foreign_keys=[location_type_id],
    )

    location_region: Mapped[Optional["LocationRegion"]] = relationship(
        "LocationRegion",
        foreign_keys=[location_region_id],
    )
