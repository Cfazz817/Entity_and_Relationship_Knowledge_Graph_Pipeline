from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.temporal import TemporalValue
from app.schemas.extraction import ExtractedTemporalValue


def create_temporal_value(
    session: Session,
    extracted: ExtractedTemporalValue,
) -> TemporalValue:

    temporal = TemporalValue(
        precision=extracted.precision.value,
        calendar=extracted.calendar.value,
        date_value=extracted.date_value,
        start_date=extracted.start_date,
        end_date=extracted.end_date,
        year_value=extracted.year_value,
        circa=extracted.circa,
        original_text=extracted.original_text,
    )

    session.add(temporal)

    session.flush()

    return temporal
