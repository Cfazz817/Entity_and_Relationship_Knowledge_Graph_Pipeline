from __future__ import annotations

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.schemas.extraction import ExtractionResult
from app.extraction.base import BaseExtractor


class GeminiExtractor(BaseExtractor):
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )

        self.model = settings.gemini_model
        # Use gemini-embedding-001 / gemini-embedding-001 for embeddings
        self.embedding_model = (
            "models/gemini-embedding-001"  # "models/gemini-embedding-2"
        )

    @property
    def model_name(self) -> str:
        return self.model

    @retry(
        stop=stop_after_attempt(10), wait=wait_exponential(multiplier=2, min=4, max=60)
    )
    def extract(
        self,
        text: str,
        previous_context: str | None = None,
    ) -> ExtractionResult:

        context_section = ""
        if previous_context:
            context_section = f"""
PREVIOUS CONTEXT (for coreference only, do not extract entities from this):

{previous_context}
"""

        prompt = f"""
You are a high-precision knowledge graph extraction system.

Your task is to extract entities and explicit relationships
from the supplied source text.

ENTITY TYPES:

- person
- institution
- event
- location

RULES:

1. Extract every clearly identifiable entity that is relevant
   to the text.

2. Extract people, institutions, events, and locations.

3. Extract relationships explicitly supported by the text.

4. Do NOT invent relationships.

5. Do NOT infer that two people know each other merely because
   they appear in the same paragraph.

6. Every relationship must reference entities using the
   temporary IDs assigned in the entity list.

7. Preserve uncertainty.

8. If the source says "approximately 1942", do not turn that
   into an exact date.

9. Preserve the original wording of temporal information.

10. Every important extraction should contain evidence.

11. Confidence must represent confidence that the extraction
    is actually supported by the source text.

12. Do not use outside knowledge.
{context_section}
SOURCE TEXT:

{text}
"""

        safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ]

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResult,
                safety_settings=safety_settings,
            ),
        )

        if not response.text:
            print(
                "Warning: Gemini returned an empty response. Likely blocked by safety filters. Skipping chunk."
            )
            return ExtractionResult(entities=[], relationships=[])

        return ExtractionResult.model_validate_json(response.text)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    def embed(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=text,
        )

        embeddings = response.embeddings
        if not embeddings:
            raise RuntimeError("Gemini failed to generate embedding.")

        first_emb = embeddings[0]
        if not first_emb.values:
            raise RuntimeError("Gemini failed to generate embedding values.")

        return first_emb.values

    @retry(
        stop=stop_after_attempt(10), wait=wait_exponential(multiplier=2, min=4, max=60)
    )
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=texts,
        )

        embeddings = response.embeddings
        if not embeddings:
            raise RuntimeError("Gemini failed to generate embeddings.")

        result: list[list[float]] = []
        for emb in embeddings:
            if not emb.values:
                raise RuntimeError(
                    "Gemini failed to generate embedding values in batch."
                )
            result.append(emb.values)

        return result
