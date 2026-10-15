"""Structured schema for Gemini's standard claim-field response."""

from pydantic import BaseModel, Field


MANDATORY_FIELD_NAMES = (
    "Year Built", "House Size (Square Footage)", "Number of Stories", "Roof Type",
    "Structure Type", "Interior Damage (Yes/No)", "Roof Damage (Yes/No)",
    "Type of Roof Damage", "Missing Shingles", "Hail Damage", "Wind Damage",
    "Rain Leakage (Yes/No)", "Water Damage (Yes/No)", "Rooms Affected by Water",
    "Affected Room Names (Kitchen, Living Room, Basement)", "Wall Damage",
    "Sheetrock Damage", "Flooring Damage", "Ceiling/Closet Area Damage",
    "Humidity Damage", "Sewer Backup / Sewer Water", "Lightning Damage",
    "Electrical / Electronics Damage", "Lights Damage", "HVAC / AC Damage", "Endorsements",
    "Deductible Type", "Deductible Amount", "Prior Losses", "Prior Loss Date",
    "Prior Loss Type", "Coverage Limits", "Dwelling Coverage Limit",
    "Other Structures Coverage Limit", "Personal Property Coverage Limit",
    "Additional Living Expenses Limit", "Roof Coverage Limitations", "Construction Type",
    "Occupancy Type", "Cause of Loss", "Loss Description", "ACV Policy (Yes/No)",
    "Other Structures Coverage Exclusion", "Non-Structural Exclusion",
)


class PriorLoss(BaseModel):
    lr_number: int | None = Field(default=None, alias="LR#")
    date_of_loss: str | None = Field(default=None, alias="Date of loss")
    type_of_loss: str | None = Field(default=None, alias="Type Of Loss")
    insured_item: str | None = Field(default=None, alias="Insured Item")
    lob: str | None = Field(default=None, alias="LOB")
    status: str | None = Field(default=None, alias="Status")


class CoverageLimit(BaseModel):
    coverage_type: str | None = Field(default=None, alias="Coverage Type")
    limit: float | None = Field(default=None, alias="Limit")


class ClaimExtraction(BaseModel):
    year_built: int | None = Field(default=None, alias="Year Built")
    house_size: float | None = Field(default=None, alias="House Size (Square Footage)")
    number_of_stories: float | None = Field(default=None, alias="Number of Stories")
    roof_type: str | None = Field(default=None, alias="Roof Type")
    structure_type: str | None = Field(default=None, alias="Structure Type")
    interior_damage: str | None = Field(default=None, alias="Interior Damage (Yes/No)")
    roof_damage: str | None = Field(default=None, alias="Roof Damage (Yes/No)")
    type_of_roof_damage: str | None = Field(default=None, alias="Type of Roof Damage")
    missing_shingles: str | None = Field(default=None, alias="Missing Shingles")
    hail_damage: str | None = Field(default=None, alias="Hail Damage")
    wind_damage: str | None = Field(default=None, alias="Wind Damage")
    rain_leakage: str | None = Field(default=None, alias="Rain Leakage (Yes/No)")
    water_damage: str | None = Field(default=None, alias="Water Damage (Yes/No)")
    rooms_affected_by_water: int | None = Field(default=None, alias="Rooms Affected by Water")
    affected_room_names: list[str] | None = Field(default=None, alias="Affected Room Names (Kitchen, Living Room, Basement)")
    wall_damage: str | None = Field(default=None, alias="Wall Damage")
    sheetrock_damage: str | None = Field(default=None, alias="Sheetrock Damage")
    flooring_damage: str | None = Field(default=None, alias="Flooring Damage")
    ceiling_closet_area_damage: str | None = Field(default=None, alias="Ceiling/Closet Area Damage")
    humidity_damage: str | None = Field(default=None, alias="Humidity Damage")
    sewer_backup_sewer_water: str | None = Field(default=None, alias="Sewer Backup / Sewer Water")
    lightning_damage: str | None = Field(default=None, alias="Lightning Damage")
    electrical_electronics_damage: str | None = Field(default=None, alias="Electrical / Electronics Damage")
    lights_damage: str | None = Field(default=None, alias="Lights Damage")
    hvac_ac_damage: str | None = Field(default=None, alias="HVAC / AC Damage")
    endorsements: list[str] | None = Field(default=None, alias="Endorsements")
    deductible_type: str | None = Field(default=None, alias="Deductible Type")
    deductible_amount: float | None = Field(default=None, alias="Deductible Amount")
    prior_losses: list[PriorLoss] | None = Field(default=None, alias="Prior Losses")
    prior_loss_date: str | None = Field(default=None, alias="Prior Loss Date")
    prior_loss_type: str | None = Field(default=None, alias="Prior Loss Type")
    coverage_limits: list[CoverageLimit] | None = Field(default=None, alias="Coverage Limits")
    dwelling_coverage_limit: float | None = Field(default=None, alias="Dwelling Coverage Limit")
    other_structures_coverage_limit: float | None = Field(default=None, alias="Other Structures Coverage Limit")
    personal_property_coverage_limit: float | None = Field(default=None, alias="Personal Property Coverage Limit")
    additional_living_expenses_limit: float | None = Field(default=None, alias="Additional Living Expenses Limit")
    roof_coverage_limitations: str | None = Field(default=None, alias="Roof Coverage Limitations")
    construction_type: str | None = Field(default=None, alias="Construction Type")
    occupancy_type: str | None = Field(default=None, alias="Occupancy Type")
    cause_of_loss: str | None = Field(default=None, alias="Cause of Loss")
    loss_description: str | None = Field(default=None, alias="Loss Description")
    acv_policy: str | None = Field(default=None, alias="ACV Policy (Yes/No)")
    other_structures_coverage_exclusion: str | None = Field(default=None, alias="Other Structures Coverage Exclusion")
    non_structural_exclusion: str | None = Field(default=None, alias="Non-Structural Exclusion")


class CustomExtractedField(BaseModel):
    key: str
    value: str | None = None


class DynamicLLMResponse(BaseModel):
    mandatory: ClaimExtraction
    custom_fields: list[CustomExtractedField] = Field(default_factory=list)
