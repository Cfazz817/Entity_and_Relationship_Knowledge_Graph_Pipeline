from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.chunking import chunk_page_text
from app.ingestion.pdf import extract_pdf_pages
from app.models.document import Document, DocumentChunk
from app.models.source import Source


def calculate_file_hash(path: str | Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    """
    file_path = Path(path)

    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


def ingest_pdf(
    session: Session,
    path: str | Path,
    *,
    title: str | None = None,
    author: str | None = None,
    publisher: str | None = None,
    publication_date: str | None = None,
    source_url: str | None = None,
    max_chars: int = 6000,
) -> Document:
    """
    Parse and persist a complete PDF.

    Stores:

        Source
        Document
        original PDF bytes
        DocumentChunk rows

    The original PDF is stored in PostgreSQL as BYTEA.
    """

    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"PDF path is not a file: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, got: {pdf_path.suffix}"
        )

    # ---------------------------------------------------------
    # Read the COMPLETE original PDF.
    # ---------------------------------------------------------

    original_content = pdf_path.read_bytes()

    if not original_content:
        raise ValueError(
            f"PDF is empty: {pdf_path}"
        )

    # ---------------------------------------------------------
    # Hash the original bytes.
    # ---------------------------------------------------------

    content_hash = hashlib.sha256(
        original_content
    ).hexdigest()

    # ---------------------------------------------------------
    # Prevent duplicate documents.
    # ---------------------------------------------------------

    existing_document = session.scalar(
        select(Document)
        .where(
            Document.content_hash == content_hash
        )
        .limit(1)
    )

    if existing_document is not None:
        return existing_document

    # ---------------------------------------------------------
    # Extract PDF pages.
    # ---------------------------------------------------------

    pages = extract_pdf_pages(pdf_path)

    # ---------------------------------------------------------
    # Create or reuse Source.
    # ---------------------------------------------------------

    source = None

    if source_url:
        source = session.scalar(
            select(Source)
            .where(Source.url == source_url)
            .limit(1)
        )

    if source is None:
        source = Source(
            source_type="pdf",
            url=source_url,
            title=title or pdf_path.stem,
            author=author,
            publisher=publisher,
            publication_date=publication_date,
            metadata_={
                "filename": pdf_path.name,
                "path": str(pdf_path.resolve()),
                "file_size": len(original_content),
            },
        )

        session.add(source)
        session.flush()

    # ---------------------------------------------------------
    # Create Document INCLUDING ORIGINAL PDF.
    # ---------------------------------------------------------

    mime_type, _ = mimetypes.guess_type(
        pdf_path.name
    )

    document = Document(
        source_id=source.id,
        title=title or pdf_path.stem,
        mime_type=mime_type or "application/pdf",
        language=None,
        content_hash=content_hash,
        original_content=original_content,
    )

    session.add(document)
    session.flush()

    # ---------------------------------------------------------
    # Create DocumentChunks.
    # ---------------------------------------------------------

    chunk_number = 1

    for page in pages:
        page_chunks = chunk_page_text(
            page.text,
            page.page_number,
            max_chars=max_chars,
        )

        for chunk in page_chunks:
            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_number=chunk_number,
                text=chunk.text,
                page_number=chunk.page_number,
                paragraph_number=chunk.paragraph_number,
                char_start=chunk.char_start,
                char_end=chunk.char_end,
            )

            session.add(document_chunk)

            chunk_number += 1

    session.commit()
    session.refresh(document)

    return document
