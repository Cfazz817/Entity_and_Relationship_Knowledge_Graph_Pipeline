EXTRACTION_PROMPT_VERSION = "1.0"


def build_extraction_prompt(text: str) -> str:
    return f"""
You are a high-precision knowledge graph extraction system.

Extract entities and explicit relationships from the source text.

Entity types:

- person
- institution
- event
- location

Rules:

1. Extract entities actually supported by the text.
2. Extract explicit relationships.
3. Do not invent facts.
4. Do not infer relationships merely from co-occurrence.
5. Preserve uncertainty.
6. Preserve original temporal wording.
7. Provide evidence for important claims.
8. Assign confidence from 0.0 to 1.0.
9. Use temporary IDs for entities.
10. Relationships must reference those temporary IDs.

SOURCE TEXT:

{text}
"""
