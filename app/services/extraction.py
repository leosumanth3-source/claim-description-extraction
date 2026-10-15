"""Extraction service — wraps LLMExtractor with clean interface."""

from app.config import Settings
from app.llm import LLMExtractor


class ExtractionService:
    def __init__(self, settings: Settings) -> None:
        self.model = settings.gemini_model
        self._extractor = LLMExtractor(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    async def extract(self, description: str, custom_fields: list[str]) -> dict:
        if not self._extractor.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")
        return await self._extractor.extract(
            description=description,
            custom_fields=custom_fields,
        )
