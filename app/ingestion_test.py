from __future__ import annotations
import sys

from app.database import SessionLocal
from app.ingestion.documents import ingest_pdf


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  uv run python -m app.ingestion_test /path/to/file.pdf"
        )
        raise SystemExit(1)

    pdf_path = sys.argv[1]

    with SessionLocal() as session:
        document = ingest_pdf(
            session=session,
            path=pdf_path,
        )

        print()
        print("PDF ingestion successful.")
        print(f"Document ID: {document.id}")
        print(f"Title:       {document.title}")
        print(f"Hash:        {document.content_hash}")
        print()
