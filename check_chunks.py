from app.database import SessionLocal
from app.models.document import DocumentChunk
from sqlalchemy import select

with SessionLocal() as session:
    chunks = session.scalars(select(DocumentChunk).limit(10)).all()
    for c in chunks:
        print(f"Chunk {c.id} (Page {c.page_number}):\n{repr(c.text[:150])}\n")
