from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta

from app.extraction.base import BaseExtractor
from app.extraction.factory import get_extractor
from app.models.document import DocumentChunk
from app.models.extraction import (
    EntityMention,
    ExtractionRun,
    RelationshipAssertion,
)
from app.resolution.entities import resolve_entity
from app.resolution.relationships import resolve_relationship


class KnowledgePipeline:

    def __init__(
        self,
        extractor: BaseExtractor | None = None,
    ) -> None:

        self.extractor = (
            extractor
            if extractor is not None
            else get_extractor()
        )

    def reset_stuck_runs(self, session: Session, hours_old: int = 2) -> int:
        """
        Sweep for extraction runs that have been 'running' for too long
        and reset them to 'failed'.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)

        stuck_runs = session.scalars(
            select(ExtractionRun)
            .where(ExtractionRun.status == "running")
            .where(ExtractionRun.created_at < cutoff_time)
        ).all()

        for run in stuck_runs:
            run.status = "failed"
            run.error_message = "Automatically reset due to timeout."

        session.commit()
        return len(stuck_runs)

    def process_chunk(
        self,
        session: Session,
        chunk: DocumentChunk,
    ):

        extraction_run = ExtractionRun(
            chunk_id=chunk.id,
            model=self.extractor.model_name,
            prompt_version="1.0",
            schema_version="1.0",
            status="running",
        )

        session.add(extraction_run)

        session.flush()

        try:
            # 3. Context Loss Fix
            prev_text = None
            if chunk.chunk_number > 1:
                prev_chunk = session.scalar(
                    select(DocumentChunk)
                    .where(DocumentChunk.document_id == chunk.document_id)
                    .where(DocumentChunk.chunk_number == chunk.chunk_number - 1)
                )
                if prev_chunk:
                    prev_text = prev_chunk.text[-200:]

            result = self.extractor.extract(
                chunk.text,
                previous_context=prev_text,
            )

            extraction_run.raw_response = (
                result.model_dump(mode="json")
            )

            extraction_run.status = "completed"

            entity_map = {}

            # Precalculate embeddings in one batch
            texts_to_embed = [
                f"{e.name}: {e.description}" for e in result.entities
            ]
            embeddings_list = []
            if texts_to_embed:
                embeddings_list = self.extractor.embed_batch(texts_to_embed)

            entity_embeddings = {
                e.temporary_id: emb for e, emb in zip(result.entities, embeddings_list)
            }

            for extracted_entity in result.entities:

                entity = resolve_entity(
                    session=session,
                    extracted=extracted_entity,
                    extractor=self.extractor,
                    precalculated_embedding=entity_embeddings.get(extracted_entity.temporary_id),
                )

                entity_map[
                    extracted_entity.temporary_id
                ] = entity

                for evidence in extracted_entity.evidence:

                    mention = EntityMention(
                        entity_id=entity.id,
                        chunk_id=chunk.id,
                        surface_text=evidence.quote,
                        start_char=evidence.start_char,
                        end_char=evidence.end_char,
                        confidence=extracted_entity.confidence,
                    )

                    session.add(mention)

            session.flush()

            for extracted_relationship in result.relationships:

                source = entity_map.get(
                    extracted_relationship.source_entity_id
                )

                target = entity_map.get(
                    extracted_relationship.target_entity_id
                )

                if source is None:
                    raise ValueError(
                        "Relationship references unknown "
                        "source entity: "
                        f"{extracted_relationship.source_entity_id}"
                    )

                if target is None:
                    raise ValueError(
                        "Relationship references unknown "
                        "target entity: "
                        f"{extracted_relationship.target_entity_id}"
                    )

                relationship = resolve_relationship(
                    session=session,
                    source_entity_id=source.id,
                    target_entity_id=target.id,
                    extracted=extracted_relationship,
                )

                for evidence in (
                    extracted_relationship.evidence
                ):

                    assertion = RelationshipAssertion(
                        relationship_id=relationship.id,
                        extraction_run_id=extraction_run.id,
                        confidence=(
                            extracted_relationship.confidence
                        ),
                        status="active",
                        evidence_text=evidence.quote,
                    )

                    session.add(assertion)

            session.commit()

            return result

        except Exception as exc:

            session.rollback()

            extraction_run.status = "failed"
            extraction_run.error_message = str(exc)

            session.add(extraction_run)

            session.commit()

            raise
