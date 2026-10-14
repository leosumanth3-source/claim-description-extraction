"""Framework-independent claim extraction use case."""

from app.config import Settings
from app.llm import LLMExtractor


class ClaimExtractionService:
    """Coordinates Gemini extraction for the Streamlit application."""

    def __init__(self, settings: Settings) -> None:
        self.model = settings.gemini_model
        self._extractor = LLMExtractor(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    async def extract(
        self,
        description: str,
        custom_fields: list[str],
    ) -> dict:
        """Extract all standard and requested custom claim fields."""

        return await self._extractor.extract(
            description=description,
            custom_fields=custom_fields,
        )
