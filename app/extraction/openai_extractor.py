from app.config import settings
from app.extraction.base import BaseExtractor
from app.schemas.extraction import ExtractionResult

class OpenAIExtractor(BaseExtractor):
    def __init__(self) -> None:
        # self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.embedding_model = "text-embedding-3-small"

    @property
    def model_name(self) -> str:
        return self.model

    def extract(self, text: str, previous_context: str | None = None) -> ExtractionResult:
        raise NotImplementedError("OpenAI extraction is not yet implemented.")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("OpenAI embedding is not yet implemented.")
