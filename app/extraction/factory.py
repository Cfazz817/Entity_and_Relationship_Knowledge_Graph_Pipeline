from app.config import settings
from app.extraction.base import BaseExtractor

def get_extractor() -> BaseExtractor:
    provider = settings.llm_provider.lower()
    
    if provider == "gemini":
        from app.extraction.gemini import GeminiExtractor
        return GeminiExtractor()
    elif provider == "openai":
        from app.extraction.openai_extractor import OpenAIExtractor
        return OpenAIExtractor()
    else:
        raise ValueError(f"Unknown LLM provider set in config: {provider}")
