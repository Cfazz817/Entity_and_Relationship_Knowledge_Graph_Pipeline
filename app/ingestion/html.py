from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path

import trafilatura
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.chunking import chunk_page_text
from app.models.document import Document, DocumentChunk
from app.models.source import Source


def ingest_html(
    session: Session,
    path: str | Path | None = None,
    url: str | None = None,
    html_content: bytes | None = None,
    *,
    title: str | None = None,
    author: str | None = None,
    publisher: str | None = None,
    publication_date: str | None = None,
    max_chars: int = 6000,
) -> Document:
    """
    Parse and persist a complete HTML document from a file path, URL, or raw bytes.

    Stores:
        Source
        Document
        original HTML bytes
        DocumentChunk rows
    """

    if not any([path, url, html_content]):
        raise ValueError("Must provide one of: path, url, or html_content")

    original_content: bytes = b""
    source_url = url
    
    if path:
        html_path = Path(path)
        if not html_path.is_file():
            raise ValueError(f"HTML path is not a file: {html_path}")
        original_content = html_path.read_bytes()
    elif url and not html_content:
        # Fetch the HTML if only URL is provided
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            raise ValueError(f"Failed to fetch HTML from URL: {url}")
        original_content = downloaded.encode("utf-8")
    elif html_content:
        original_content = html_content

    if not original_content:
        raise ValueError("HTML content is empty.")

    # ---------------------------------------------------------
    # Hash the original bytes.
    # ---------------------------------------------------------
    content_hash = hashlib.sha256(original_content).hexdigest()

    # ---------------------------------------------------------
    # Prevent duplicate documents.
    # ---------------------------------------------------------
    existing_document = session.scalar(
        select(Document).where(Document.content_hash == content_hash).limit(1)
    )

    if existing_document is not None:
        return existing_document

    # ---------------------------------------------------------
    # Extract text from HTML using Trafilatura
    # ---------------------------------------------------------
    # Trafilatura extracts the main text, removing boilerplate like nav/footer
    extracted_text = trafilatura.extract(
        original_content.decode("utf-8", errors="ignore"),
        include_links=True,
        include_comments=False
    )
    
    if not extracted_text:
        raise ValueError("Failed to extract any meaningful text from the HTML.")

    # ---------------------------------------------------------
    # Create or reuse Source.
    # ---------------------------------------------------------
    source = None

    if source_url:
        source = session.scalar(
            select(Source).where(Source.url == source_url).limit(1)
        )

    if source is None:
        source = Source(
            source_type="html",
            url=source_url,
            title=title or (Path(path).stem if path else "HTML Document"),
            author=author,
            publisher=publisher,
            publication_date=publication_date,
            metadata_={
                "file_size": len(original_content),
                "path": str(Path(path).resolve()) if path else None,
            },
        )
        session.add(source)
        session.flush()

    # ---------------------------------------------------------
    # Create Document INCLUDING ORIGINAL HTML.
    # ---------------------------------------------------------
    mime_type = "text/html"
    if path:
        guessed_mime, _ = mimetypes.guess_type(Path(path).name)
        if guessed_mime:
            mime_type = guessed_mime

    document = Document(
        source_id=source.id,
        title=source.title,
        mime_type=mime_type,
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

    # Treat the entire HTML text as "page 1"
    chunks = chunk_page_text(
        extracted_text,
        page_number=1,
        max_chars=max_chars,
    )

    for chunk in chunks:
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
