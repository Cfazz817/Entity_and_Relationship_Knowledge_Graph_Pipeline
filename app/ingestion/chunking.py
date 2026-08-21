from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextChunk:
    chunk_number: int
    text: str
    page_number: int | None
    paragraph_number: int | None
    char_start: int | None
    char_end: int | None


def _split_large_text(text: str, max_chars: int) -> list[str]:
    """
    Split oversized text into chunks without exceeding max_chars
    whenever reasonably possible.
    """
    words = text.split()

    if not words:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for word in words:
        additional_length = len(word)

        if current:
            additional_length += 1

        if current and current_length + additional_length > max_chars:
            chunks.append(" ".join(current))
            current = [word]
            current_length = len(word)
        else:
            current.append(word)
            current_length += additional_length

    if current:
        chunks.append(" ".join(current))

    return chunks


def chunk_page_text(
    text: str,
    page_number: int,
    *,
    max_chars: int = 6000,
    overlap_chars: int = 500,
) -> list[TextChunk]:
    """
    Convert one PDF page into semantically reasonable chunks.

    The initial implementation uses paragraphs as the primary
    boundary and falls back to word-based splitting for very
    large paragraphs.

    overlap_chars is currently reserved for the next iteration
    of the chunker. It is accepted now so the API can evolve
    without changing callers.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero")

    if overlap_chars < 0:
        raise ValueError("overlap_chars cannot be negative")

    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    if not normalized:
        return []

    raw_paragraphs = normalized.split("\n\n")

    chunks: list[TextChunk] = []
    chunk_number = 1

    character_cursor = 0

    for paragraph_number, raw_paragraph in enumerate(
        raw_paragraphs,
        start=1,
    ):
        paragraph = raw_paragraph.strip()

        if not paragraph:
            character_cursor += len(raw_paragraph) + 2
            continue

        paragraph_start = normalized.find(
            paragraph,
            character_cursor,
        )

        if paragraph_start == -1:
            paragraph_start = character_cursor

        paragraph_end = paragraph_start + len(paragraph)

        if len(paragraph) <= max_chars:
            chunks.append(
                TextChunk(
                    chunk_number=chunk_number,
                    text=paragraph,
                    page_number=page_number,
                    paragraph_number=paragraph_number,
                    char_start=paragraph_start,
                    char_end=paragraph_end,
                )
            )

            chunk_number += 1

        else:
            pieces = _split_large_text(
                paragraph,
                max_chars=max_chars,
            )

            local_cursor = paragraph_start

            for piece in pieces:
                piece_start = normalized.find(
                    piece,
                    local_cursor,
                )

                if piece_start == -1:
                    piece_start = local_cursor

                piece_end = piece_start + len(piece)

                chunks.append(
                    TextChunk(
                        chunk_number=chunk_number,
                        text=piece,
                        page_number=page_number,
                        paragraph_number=paragraph_number,
                        char_start=piece_start,
                        char_end=piece_end,
                    )
                )

                chunk_number += 1
                local_cursor = piece_end

        character_cursor = paragraph_end

    return chunks
