from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


def restore_document(
    session: Session,
    document_id: UUID,
    output_path: str | Path,
) -> Path:
    document = session.scalar(
        select(Document).where(
            Document.id == document_id
        )
    )

    if document is None:
        raise ValueError(
            f"Document not found: {document_id}"
        )

    if document.original_content is None:
        raise ValueError(
            f"Document has no stored original content: "
            f"{document_id}"
        )

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_bytes(
        document.original_content
    )

    return output
