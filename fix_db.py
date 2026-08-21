import sys

from app.database import SessionLocal
from app.models.document import Document
from sqlalchemy import select

def main():
    with SessionLocal() as session:
        # Find the document with the bad title
        docs = session.scalars(select(Document).where(Document.title == "My Sample Document")).all()
        
        if not docs:
            print("No documents found with the title 'My Sample Document'.")
            return

        for doc in docs:
            # Update Document title
            doc.title = "Operation Gladio"
            
            # Update the corresponding Source metadata
            if doc.source:
                doc.source.title = "Operation Gladio"
                doc.source.author = "Paul Williams"
                
            print(f"Successfully updated Document ID {doc.id} to Operation Gladio by Paul Williams.")
            
        session.commit()

if __name__ == "__main__":
    main()
