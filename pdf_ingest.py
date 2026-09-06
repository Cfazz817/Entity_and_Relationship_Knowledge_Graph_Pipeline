from app.database import SessionLocal
from app.ingestion.documents import ingest_pdf
from pathlib import Path


def main():
    # 1. Open a database session
    with SessionLocal() as session:

        # 2. Define the path to your PDF
        # Replace with your actual PDF path
        pdf_path = Path(
            "/home/fazzin8r/dev/entity_pipeline/pdfs/foreignconspiracy00mors.pdf")

        # 3. Call the ingestion function
        print(f"Ingesting {pdf_path}...")
        document = ingest_pdf(
            session=session,
            path=pdf_path,
            author="Samuel Morse",
            title="Foriegn Conspiracy against the United States",
            start_page=15,   # Starts right at Chapter 1 (skips ToC)
            end_page=197
        )

        print(f"Successfully ingested document ID: {document.id}")


if __name__ == "__main__":
    main()
