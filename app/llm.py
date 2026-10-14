import json

from google import genai
from google.genai import types

from .prompts import build_system_prompt
from .schemas import (
    ClaimExtraction,
    DynamicLLMResponse,
)


class LLMExtractor:
    """
    Sends claim descriptions to Gemini.

    All standard mandatory claim fields are extracted.

    Custom fields are supplied dynamically for the session.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:

        # Store the selected Gemini model.
        self.model = model

        # Create Gemini API client.
        self.client = genai.Client(
            api_key=api_key
        )

    async def extract(
        self,
        description: str,
        custom_fields: list[str],
    ) -> dict:
        """
        Extract mandatory + custom fields.
        """

        if not description.strip():
            raise ValueError(
                "Claim description cannot be empty."
            )

        # Create a dynamic prompt from the
        # custom keys registered by Streamlit.
        system_prompt = build_system_prompt(
            custom_fields
        )

        # Ask Gemini for our fixed internal schema.
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=description,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=DynamicLLMResponse,
            ),
        )

        # Gemini SDK may already parse the response.
        if response.parsed is not None:

            if isinstance(
                response.parsed,
                DynamicLLMResponse,
            ):
                parsed = response.parsed

            else:
                parsed = DynamicLLMResponse.model_validate(
                    response.parsed
                )

        # Fallback if Gemini gives us JSON text.
        elif response.text:
            parsed = (
                DynamicLLMResponse
                .model_validate_json(
                    response.text
                )
            )

        else:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        # Start with all standard mandatory fields.
        result = parsed.mandatory.model_dump(
            by_alias=True
        )

        # Convert custom Gemini results into a dictionary.
        custom_values = {
            item.key: item.value
            for item in parsed.custom_fields
        }

        # Add EVERY custom field requested by the user.
        #
        # If Gemini could not find the value,
        # return null.
        for key in custom_fields:
            result[key] = self._convert_value(
                custom_values.get(key)
            )

        return result

    @staticmethod
    def _convert_value(
        value: str | None,
    ):
        """
        Convert simple JSON-looking string values
        into their appropriate Python values.

        Examples:
        "1971" -> 1971
        "1.5" -> 1.5
        "[...]" -> list
        "{...}" -> dict
        "ABC123" -> "ABC123"
        """

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        # Try to interpret numbers, arrays and objects.
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

        # Otherwise keep it as a string.
        return value