from app.database import SessionLocal
from app.ingestion.documents import ingest_pdf
from pathlib import Path


def main():
    # 1. Open a database session
    with SessionLocal() as session:

        # 2. Define the path to your PDF
        # Replace with your actual PDF path
        pdf_path = Path(
            "/home/fazzin8r/dev/entity_pipeline/pdfs/Rulers of Evil, Frederick Tupper Saussy.pdf")

        # 3. Call the ingestion function
        print(f"Ingesting {pdf_path}...")
        document = ingest_pdf(
            session=session,
            path=pdf_path,
            title="Rulers of Evil",  # Optional metadata
            author="Frederick Tupper Saussy III"           # Optional metadata
        )

        print(f"Successfully ingested document ID: {document.id}")


if __name__ == "__main__":
    main()
