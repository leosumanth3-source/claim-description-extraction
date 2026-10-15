"""Gemini client — sends claim text, parses structured response, retries on failure."""

import json

from google import genai
from google.genai import types
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from app.schemas.claim_fields import DynamicLLMResponse
from app.core.logging import get_logger
from app.prompts import build_system_prompt

logger = get_logger(__name__)


def _is_retryable(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return any(t in msg for t in ("429", "rate", "quota", "503", "502", "timeout", "connection"))


class LLMExtractor:
    def __init__(self, api_key: str, model: str, max_retries: int = 3) -> None:
        self.model = model
        self.max_retries = max_retries
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key) if api_key else None

    async def extract(self, description: str, custom_fields: list[str]) -> dict:
        if not description.strip():
            raise ValueError("Claim description cannot be empty.")
        if self.client is None:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        system_prompt = build_system_prompt(custom_fields)

        retrying = AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(min=1, max=10),
            retry=retry_if_exception(_is_retryable),
            reraise=True,
        )

        async for attempt in retrying:
            with attempt:
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=description,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        response_schema=DynamicLLMResponse,
                    ),
                )

        if response.parsed is not None:
            parsed = (
                response.parsed
                if isinstance(response.parsed, DynamicLLMResponse)
                else DynamicLLMResponse.model_validate(response.parsed)
            )
        elif response.text:
            parsed = DynamicLLMResponse.model_validate_json(response.text)
        else:
            raise RuntimeError("Gemini returned an empty response.")

        result = parsed.mandatory.model_dump(by_alias=True)

        custom_values = {item.key: item.value for item in parsed.custom_fields}
        for key in custom_fields:
            result[key] = _coerce(custom_values.get(key))

        return result


def _coerce(value: str | None):
    """Try to parse string values that look like JSON numbers/lists/objects."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value
