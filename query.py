from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.entity import Entity, EntityType
from app.models.extraction import EntityMention, RelationshipAssertion
from app.models.relationship import Relationship, RelationshipType
from sqlalchemy.orm import aliased


def print_summary():
    with SessionLocal() as session:
        print("\n================ KNOWLEDGE GRAPH SUMMARY ================")

        # 1. Total counts
        total_entities = session.scalar(select(func.count(Entity.id)))
        total_mentions = session.scalar(select(func.count(EntityMention.id)))
        total_assertions = session.scalar(
            select(func.count(RelationshipAssertion.id)))

        print(f"Total Unique Entities: {total_entities}")
        print(f"Total Entity Mentions: {total_mentions}")
        print(f"Total Relationship Assertions: {total_assertions}")

        # 2. Top 10 Most Mentioned Entities
        print("\n--- Top 100 Most Mentioned Entities ---")
        top_entities = session.execute(
            select(
                Entity.primary_name,
                EntityType.display_name,
                func.count(EntityMention.id).label('mentions')
            )
            .join(EntityType)
            .join(EntityMention)
            .group_by(Entity.id, EntityType.display_name)
            .order_by(func.count(EntityMention.id).desc())
            .limit(100)
        ).all()

        for name, type_name, mentions in top_entities:
            print(f"- {name} ({type_name}): {mentions} mentions")

        # 3. 10 Most Recent Relationships
        print("\n--- 100 Most Recent Relationships ---")
        SourceEntity = aliased(Entity)
        TargetEntity = aliased(Entity)

        recent_rels = session.execute(
            select(
                SourceEntity.primary_name.label('source_name'),
                RelationshipType.display_name.label('rel_type'),
                TargetEntity.primary_name.label('target_name'),
                RelationshipAssertion.evidence_text
            )
            .select_from(RelationshipAssertion)
            .join(Relationship, RelationshipAssertion.relationship_id == Relationship.id)
            .join(RelationshipType, Relationship.relationship_type_id == RelationshipType.id)
            .join(SourceEntity, Relationship.source_entity_id == SourceEntity.id)
            .join(TargetEntity, Relationship.target_entity_id == TargetEntity.id)
            .order_by(RelationshipAssertion.created_at.desc())
            .limit(100)
        ).all()

        for src, rel_type, tgt, evidence in recent_rels:
            print(f"\n[ {src} ] --({rel_type})--> [ {tgt} ]")
            print(f"    Evidence: \"{evidence}\"")

        print("\n=========================================================\n")


if __name__ == "__main__":
    print_summary()
