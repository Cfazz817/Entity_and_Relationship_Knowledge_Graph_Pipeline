from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class TemporalPrecision(str, Enum):
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    DECADE = "decade"
    CIRCA = "circa"
    RANGE = "range"
    BEFORE = "before"
    AFTER = "after"
    UNKNOWN = "unknown"


class CalendarSystem(str, Enum):
    GREGORIAN = "gregorian"
    JULIAN = "julian"
    HEBREW = "hebrew"
    ISLAMIC = "islamic"
    UNKNOWN = "unknown"


class TemporalValue(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    __tablename__ = "temporal_values"

    precision: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    calendar: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=CalendarSystem.GREGORIAN.value,
    )

    date_value: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    year_value: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    circa: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    original_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
