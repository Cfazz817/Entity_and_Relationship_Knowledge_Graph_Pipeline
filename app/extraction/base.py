from abc import ABC, abstractmethod
from app.schemas.extraction import ExtractionResult

class BaseExtractor(ABC):
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the name of the primary model being used (for logging)."""
        pass

    @abstractmethod
    def extract(self, text: str, previous_context: str | None = None) -> ExtractionResult:
        """Extracts entities and relationships from the text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for a batch of strings."""
        pass
