from app.database import SessionLocal
from app.ingestion.documents import ingest_pdf
from pathlib import Path


def main():
    # 1. Open a database session
    with SessionLocal() as session:

        # 2. Define the path to your PDF
        # Replace with your actual PDF path
        pdf_path = Path(
            "/home/fazzin8r/dev/entity_pipeline/pdfs/The Vatican`s Holocaust by Avro Manhattan pdf.pdf")

        # 3. Call the ingestion function
        print(f"Ingesting {pdf_path}...")
        document = ingest_pdf(
            session=session,
            path=pdf_path,
            title="The Vatican's Holocaust",
            author="Avro Manhattan",
            start_page=19,   # Starts right at Chapter 1 (skips ToC)
            end_page=250     # Stops right before the Index/Bibliography
        )

        print(f"Successfully ingested document ID: {document.id}")


if __name__ == "__main__":
    main()
