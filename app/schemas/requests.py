"""Input parsing for the plain-text extraction request."""

import re

from pydantic import BaseModel, Field, field_validator


class ClaimExtractionRequest(BaseModel):
    """A claim narrative with one optional additional field to extract."""

    claim_description: str = Field(
        ...,
        min_length=1,
        max_length=100_000,
        description="Raw, unstructured insurance claim text.",
    )
    custom_field: str | None = Field(
        default=None,
        description="One additional field to extract alongside the standard claim fields.",
    )

    @field_validator("claim_description")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Claim description cannot be blank.")
        return value.strip()

    @field_validator("custom_field")
    @classmethod
    def clean_custom_field(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @classmethod
    def from_plain_text(cls, body: str) -> "ClaimExtractionRequest":
        """Parse the endpoint's two-label text format.

        The claim description may span multiple lines.  The optional custom field
        begins at a line labelled ``custom_field:``.
        """
        text = body.strip()
        match = re.match(
            r"^claim(?:_| )description\s*:\s*([\s\S]*)\Z",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Text must start with 'claim_description:'.")

        content = match.group(1)
        custom_marker = re.search(
            r"^custom_field\s*:\s*(.*)$", content, re.IGNORECASE | re.MULTILINE
        )
        if custom_marker is None:
            return cls(claim_description=content)

        description = content[:custom_marker.start()].strip()
        custom_field = custom_marker.group(1).strip()
        return cls(
            claim_description=description,
            custom_field=custom_field or None,
        )
