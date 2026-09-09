from app.database import SessionLocal
from app.ingestion.documents import ingest_pdf
from pathlib import Path


def main():
    # 1. Open a database session
    with SessionLocal() as session:

        # 2. Define the path to your PDF
        # Replace with your actual PDF path
        pdf_path = Path(
            "/home/fazzin8r/dev/entity_pipeline/pdfs/a_history_of_the_inquisition_vol._iii_henry_charles_lea__1888_.pdf")

        # 3. Call the ingestion function
        print(f"Ingesting {pdf_path}...")
        document = ingest_pdf(
            session=session,
            path=pdf_path,
            author="Henry Charles Lea",
            title="A History of The Inquisition Vol. III",
            start_page=17,   # Starts right at Chapter 1 (skips ToC)
            end_page=666
        )

        print(f"Successfully ingested document ID: {document.id}")


if __name__ == "__main__":
    main()
