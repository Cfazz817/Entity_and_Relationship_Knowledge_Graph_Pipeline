from app.database import SessionLocal
from app.models.source import Source
from sqlalchemy import select

with SessionLocal() as session:
    sources = session.scalars(select(Source)).all()
    for s in sources:
        print(f"Source: {s.title}, Path: {s.metadata_.get('path')}")
