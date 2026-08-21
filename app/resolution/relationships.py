from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.relationship import (
    Relationship,
    RelationshipType,
)
from app.models.temporal import TemporalValue
from app.schemas.extraction import ExtractedRelationship


def resolve_relationship(
    session: Session,
    source_entity_id,
    target_entity_id,
    extracted: ExtractedRelationship,
) -> Relationship:

    relationship_type = session.scalar(
        select(RelationshipType).where(
            RelationshipType.code
            == extracted.relationship_type.value
        )
    )

    if relationship_type is None:
        raise ValueError(
            "Unknown relationship type: "
            f"{extracted.relationship_type.value}"
        )

    existing = session.scalar(
        select(Relationship).where(
            Relationship.source_entity_id
            == source_entity_id,

            Relationship.target_entity_id
            == target_entity_id,

            Relationship.relationship_type_id
            == relationship_type.id,
        )
    )

    if existing is not None:
        return existing

    valid_time_id = None

    if extracted.validity is not None:

        temporal = TemporalValue(
            precision=extracted.validity.precision.value,
            calendar=extracted.validity.calendar.value,
            date_value=extracted.validity.date_value,
            start_date=extracted.validity.start_date,
            end_date=extracted.validity.end_date,
            year_value=extracted.validity.year_value,
            circa=extracted.validity.circa,
            original_text=extracted.validity.original_text,
        )

        session.add(temporal)

        session.flush()

        valid_time_id = temporal.id

    relationship = Relationship(
        source_entity_id=source_entity_id,
        target_entity_id=target_entity_id,
        relationship_type_id=relationship_type.id,
        valid_time_id=valid_time_id,
    )

    session.add(relationship)

    session.flush()

    return relationship
