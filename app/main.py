import concurrent.futures
from sqlalchemy import select, exists

from app.database import SessionLocal
from app.models.document import DocumentChunk
from app.models.extraction import ExtractionRun
from app.pipeline import KnowledgePipeline


def process_single_chunk(chunk_id):
    pipeline = KnowledgePipeline()
    with SessionLocal() as session:
        chunk = session.scalar(
            select(DocumentChunk).where(DocumentChunk.id == chunk_id)
        )
        if not chunk:
            return None

        try:
            result = pipeline.process_chunk(
                session=session,
                chunk=chunk,
            )
            print(f"Chunk {chunk_id} processed\n'{chunk.text[:21]}...'")
            return result
        except Exception as e:
            print(f"Error processing chunk {chunk_id}: {e}")
            return None


def main() -> None:

    with SessionLocal() as session:
        pipeline = KnowledgePipeline()

        # 5. Sweep stuck runs
        stuck_reset = pipeline.reset_stuck_runs(session)
        if stuck_reset > 0:
            print(f"Reset {stuck_reset} stuck extraction runs.")

        # 1. Fetch chunks to process (skipping completed/running ones)
        chunks = session.scalars(
            select(DocumentChunk)
            .where(
                ~exists(
                    select(ExtractionRun.id).where(
                        ExtractionRun.chunk_id == DocumentChunk.id,
                        ExtractionRun.status.in_(["completed", "running"])
                    )
                )
            )
            .order_by(DocumentChunk.chunk_number)
        ).all()

        if not chunks:
            print("No document chunks exist yet.")
            return

        chunk_ids = [chunk.id for chunk in chunks]

    # 1. Concurrency Fix
    print(f"Processing {len(chunk_ids)} chunks concurrently...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(process_single_chunk, chunk_ids))

    successful = [r for r in results if r is not None]

    for i, result in enumerate(successful):
        print(
            f"Chunk {i+1} - Entities extracted: "
            f"{len(result.entities)} | "
            f"Relationships: {len(result.relationships)}"
        )


if __name__ == "__main__":
    main()
