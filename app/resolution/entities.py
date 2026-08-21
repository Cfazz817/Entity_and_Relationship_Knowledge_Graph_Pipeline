from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.entity import Entity, EntityType
from app.schemas.extraction import ExtractedEntity


def normalize_name(name: str) -> str:
    """
    Produces a basic deterministic normalized form.
    """

    value = name.lower().strip()

    value = re.sub(
        r"[^\w\s]",
        "",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def resolve_entity(
    session: Session,
    extracted: ExtractedEntity,
    extractor=None,
    precalculated_embedding: list[float] | None = None,
) -> Entity:

    normalized = normalize_name(
        extracted.name
    )

    # 1. Try exact string match first
    existing = session.scalar(
        select(Entity).where(
            Entity.normalized_name == normalized
        )
    )

    if existing is not None:
        return existing

    entity_type = session.scalar(
        select(EntityType).where(
            EntityType.code
            == extracted.entity_type.value
        )
    )

    if entity_type is None:
        raise ValueError(
            f"Unknown entity type: "
            f"{extracted.entity_type.value}"
        )

    embedding_val = precalculated_embedding
    
    # 2. If extractor is provided and no embedding passed, try semantic match
    if embedding_val is None and extractor is not None:
        text_to_embed = f"{extracted.name}: {extracted.description}"
        try:
            embedding_val = extractor.embed(text_to_embed)
        except Exception:
            pass

    if embedding_val is not None:
        try:
            closest = session.scalar(
                select(Entity)
                .where(Entity.entity_type_id == entity_type.id)
                .where(Entity.embedding.is_not(None))
                .order_by(Entity.embedding.l2_distance(embedding_val))
                .limit(1)
            )
            
            if closest:
                distance = session.scalar(
                    select(closest.embedding.l2_distance(embedding_val))
                )
                if distance is not None and distance < 0.3:
                    return closest
        except Exception:
            pass

    entity = Entity(
        entity_type_id=entity_type.id,
        primary_name=extracted.name,
        normalized_name=normalized,
        description=extracted.description,
        embedding=embedding_val,
    )

    session.add(entity)

    try:
        with session.begin_nested():
            session.flush()
    except IntegrityError:
        session.expunge(entity)
        existing = session.scalar(
            select(Entity).where(
                Entity.normalized_name == normalized
            )
        )
        if existing:
            return existing
        raise

    return entity
