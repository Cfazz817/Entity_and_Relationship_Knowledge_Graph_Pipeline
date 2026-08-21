from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF


@dataclass(slots=True)
class PDFPage:
    page_number: int
    text: str


def extract_pdf_pages(path: str | Path) -> list[PDFPage]:
    """
    Extract text from a PDF one page at a time.

    Page numbers exposed by this function are 1-based.
    """
    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not pdf_path.is_file():
        raise ValueError(f"Path is not a file: {pdf_path}")

    pages: list[PDFPage] = []

    with fitz.open(pdf_path) as document:
        if document.is_encrypted:
            raise ValueError(
                f"PDF is encrypted and cannot be processed: {pdf_path}"
            )

        for index in range(len(document)):
            page = document[index]

            # --- NEW LOGIC: SPATIAL CROP ---
            top_margin = 50
            bottom_margin = 50

            rect = fitz.Rect(
                0,
                top_margin,
                page.rect.width,
                page.rect.height - bottom_margin
            )

            text = page.get_textbox(rect)
            # -------------------------------

            # get_text can return other types depending on arguments, but we know it's a str here.
            assert isinstance(text, str)

            # Normalize line endings but otherwise preserve the
            # extracted text.
            text = text.replace("\r\n", "\n").replace("\r", "\n")

            pages.append(
                PDFPage(
                    page_number=index + 1,
                    text=text,
                )
            )

    return pages
