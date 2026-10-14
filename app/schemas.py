from pydantic import BaseModel, Field


# Display order and the canonical source of truth for standard output fields.
MANDATORY_FIELD_NAMES = (
    "Year Built",
    "House Size (Square Footage)",
    "Number of Stories",
    "Roof Type",
    "Structure Type",
    "Interior Damage (Yes/No)",
    "Roof Damage (Yes/No)",
    "Type of Roof Damage",
    "Missing Shingles",
    "Hail Damage",
    "Wind Damage",
    "Rain Leakage (Yes/No)",
    "Water Damage (Yes/No)",
    "Rooms Affected by Water",
    "Affected Room Names (Kitchen, Living Room, Basement)",
    "Wall Damage",
    "Sheetrock Damage",
    "Flooring Damage",
    "Ceiling/Closet Area Damage",
    "Humidity Damage",
    "Sewer Backup / Sewer Water",
    "Lightning Damage",
    "Electrical / Electronics Damage",
    "Lights Damage",
    "HVAC / AC Damage",
    "Endorsements",
    "Deductible Type",
    "Deductible Amount",
    "Prior Losses",
    "Prior Loss Date",
    "Prior Loss Type",
    "Coverage Limits",
    "Dwelling Coverage Limit",
    "Other Structures Coverage Limit",
    "Personal Property Coverage Limit",
    "Additional Living Expenses Limit",
    "Roof Coverage Limitations",
    "Construction Type",
    "Occupancy Type",
    "Cause of Loss",
    "Loss Description",
    "ACV Policy (Yes/No)",
    "Other Structures Coverage Exclusion",
    "Non-Structural Exclusion",
)


class PriorLoss(BaseModel):
    """
    One historical property loss record prior to the current claim.
    """

    lr_number: int | None = Field(
        default=None,
        alias="LR#",
        description="Prior loss reference or claim number",
    )

    date_of_loss: str | None = Field(
        default=None,
        alias="Date of loss",
        description="Date the prior loss occurred (YYYY-MM-DD or as stated)",
    )

    type_of_loss: str | None = Field(
        default=None,
        alias="Type Of Loss",
        description="Peril or category of the prior loss (e.g. Water, Hail, Wind, Other)",
    )

    insured_item: str | None = Field(
        default=None,
        alias="Insured Item",
        description="Property address or item involved in the prior loss",
    )

    lob: str | None = Field(
        default=None,
        alias="LOB",
        description="Line of business code (e.g. HOM)",
    )

    status: str | None = Field(
        default=None,
        alias="Status",
        description="Status of the prior claim (e.g. Closed, Open)",
    )


class CoverageLimit(BaseModel):
    """
    One explicit coverage-limit record from policy terms.
    """

    coverage_type: str | None = Field(
        default=None,
        alias="Coverage Type",
        description="Coverage classification or abbreviation (e.g. DWG, APS, PL, MP)",
    )

    limit: float | None = Field(
        default=None,
        alias="Limit",
        description="Monetary coverage limit amount in USD",
    )


class ClaimExtraction(BaseModel):
    """
    Mandatory insurance claim extraction schema.
    """

    year_built: int | None = Field(
        default=None,
        alias="Year Built",
        description="Explicit year property was constructed/built (e.g. 1995). Null if unstated.",
    )

    house_size: float | None = Field(
        default=None,
        alias="House Size (Square Footage)",
        description="Total living area or footage risk in square feet. Null if unstated.",
    )

    number_of_stories: float | None = Field(
        default=None,
        alias="Number of Stories",
        description="Explicit number of stories or levels (e.g. 1.0, 1.5, 2.0). Null if unstated.",
    )

    roof_type: str | None = Field(
        default=None,
        alias="Roof Type",
        description="Roof material or type (e.g. Composition shingle, Fiberglass, Tile, Metal).",
    )

    structure_type: str | None = Field(
        default=None,
        alias="Structure Type",
        description="Classification of structure (e.g. Residential home, Dwelling, CommercialProperty).",
    )

    interior_damage: str | None = Field(
        default=None,
        alias="Interior Damage (Yes/No)",
        description="'Yes' if interior components (walls, ceiling, flooring) are confirmed damaged; 'No' if explicitly stated undamaged; otherwise null.",
    )

    roof_damage: str | None = Field(
        default=None,
        alias="Roof Damage (Yes/No)",
        description="'Yes' if roof or shingles are confirmed damaged; 'No' if explicitly stated undamaged; otherwise null.",
    )

    type_of_roof_damage: str | None = Field(
        default=None,
        alias="Type of Roof Damage",
        description="Specific roof damage observed (e.g. missing shingles, hail impacts, lifted shingles, broken tiles).",
    )

    missing_shingles: str | None = Field(
        default=None,
        alias="Missing Shingles",
        description="'Yes' or description if missing shingles are reported; 'No' if explicitly stated absent; otherwise null.",
    )

    hail_damage: str | None = Field(
        default=None,
        alias="Hail Damage",
        description="'Yes' or description if physical hail damage is reported; 'No' if explicitly stated absent; otherwise null.",
    )

    wind_damage: str | None = Field(
        default=None,
        alias="Wind Damage",
        description="'Yes' or description if physical wind damage is reported; 'No' if explicitly stated absent; otherwise null.",
    )

    rain_leakage: str | None = Field(
        default=None,
        alias="Rain Leakage (Yes/No)",
        description="'Yes' if rain entered or roof leaked from rain; 'No' if explicitly denied; otherwise null.",
    )

    water_damage: str | None = Field(
        default=None,
        alias="Water Damage (Yes/No)",
        description="'Yes' if water intrusion, leaks, or sewer backup caused water damage; 'No' if explicitly denied; otherwise null.",
    )

    rooms_affected_by_water: int | None = Field(
        default=None,
        alias="Rooms Affected by Water",
        description="Explicit numeric count of rooms damaged by water stated in text. Do NOT count room names or calculate; return null if no explicit number is given.",
    )

    affected_room_names: list[str] | None = Field(
        default=None,
        alias="Affected Room Names (Kitchen, Living Room, Basement)",
        description="List of room names explicitly affected by water damage (e.g. ['Kitchen', 'Basement']). Do not include rooms affected only by other perils.",
    )

    wall_damage: str | None = Field(
        default=None,
        alias="Wall Damage",
        description="Confirmed damage to interior or exterior walls, or null.",
    )

    sheetrock_damage: str | None = Field(
        default=None,
        alias="Sheetrock Damage",
        description="Confirmed damage to sheetrock, drywall, or gypsum board, or null.",
    )

    flooring_damage: str | None = Field(
        default=None,
        alias="Flooring Damage",
        description="Confirmed damage to flooring, carpets, tile, or hardwood, or null.",
    )

    ceiling_closet_area_damage: str | None = Field(
        default=None,
        alias="Ceiling/Closet Area Damage",
        description="Confirmed damage to ceilings or closet areas, or null.",
    )

    humidity_damage: str | None = Field(
        default=None,
        alias="Humidity Damage",
        description="Confirmed humidity, dampness, or moisture damage with affected areas if stated, or null.",
    )

    sewer_backup_sewer_water: str | None = Field(
        default=None,
        alias="Sewer Backup / Sewer Water",
        description="Confirmed sewage backup or sewer water presence/damage, or null.",
    )

    lightning_damage: str | None = Field(
        default=None,
        alias="Lightning Damage",
        description="Confirmed physical damage caused by lightning strike, or null.",
    )

    electrical_electronics_damage: str | None = Field(
        default=None,
        alias="Electrical / Electronics Damage",
        description="Confirmed damaged or non-working electronics, wiring, appliances, fans, or electrical systems. Exclude items confirmed working or unverified.",
    )

    lights_damage: str | None = Field(
        default=None,
        alias="Lights Damage",
        description="Confirmed damaged or non-working lights, bulbs, or lighting fixtures, or null.",
    )

    hvac_ac_damage: str | None = Field(
        default=None,
        alias="HVAC / AC Damage",
        description="Confirmed damage to HVAC, air conditioner, mini-split, or heating equipment, or null.",
    )

    endorsements: list[str] | None = Field(
        default=None,
        alias="Endorsements",
        description="List of policy endorsement form numbers or codes stated (e.g. ['HO-9R(02) (07-08)']).",
    )

    deductible_type: str | None = Field(
        default=None,
        alias="Deductible Type",
        description="Type of deductible applicable to the current loss peril (e.g. Wind Hail Deductible, All Other Perils Deductible).",
    )

    deductible_amount: float | None = Field(
        default=None,
        alias="Deductible Amount",
        description="Monetary dollar amount of the applicable deductible. Do not calculate from percentage.",
    )

    prior_losses: list[PriorLoss] | None = Field(
        default=None,
        alias="Prior Losses",
        description="List of prior historical property losses occurring before the current claim.",
    )

    prior_loss_date: str | None = Field(
        default=None,
        alias="Prior Loss Date",
        description="Date of the most recent prior loss, or null.",
    )

    prior_loss_type: str | None = Field(
        default=None,
        alias="Prior Loss Type",
        description="Peril or type of the most recent prior loss, or null.",
    )

    coverage_limits: list[CoverageLimit] | None = Field(
        default=None,
        alias="Coverage Limits",
        description="List of explicit policy coverage limits stated (e.g. DWG, APS, PL, MP).",
    )

    dwelling_coverage_limit: float | None = Field(
        default=None,
        alias="Dwelling Coverage Limit",
        description="Dwelling (Coverage A / DWG) policy coverage limit amount in USD.",
    )

    other_structures_coverage_limit: float | None = Field(
        default=None,
        alias="Other Structures Coverage Limit",
        description="Other structures / Appurtenant structures (Coverage B / APS) coverage limit amount in USD.",
    )

    personal_property_coverage_limit: float | None = Field(
        default=None,
        alias="Personal Property Coverage Limit",
        description="Unscheduled personal property / contents (Coverage C) coverage limit amount in USD.",
    )

    additional_living_expenses_limit: float | None = Field(
        default=None,
        alias="Additional Living Expenses Limit",
        description="Additional Living Expenses (Coverage D / Loss of Use) coverage limit amount in USD.",
    )

    roof_coverage_limitations: str | None = Field(
        default=None,
        alias="Roof Coverage Limitations",
        description="Roof coverage limitations, restrictions, or exclusions stated in policy.",
    )

    construction_type: str | None = Field(
        default=None,
        alias="Construction Type",
        description="Construction classification (e.g. Frame, Joisted Masonry, Brick).",
    )

    occupancy_type: str | None = Field(
        default=None,
        alias="Occupancy Type",
        description="Occupancy or use type (e.g. Owner Occupied, Tenant Occupied, LRO).",
    )

    cause_of_loss: str | None = Field(
        default=None,
        alias="Cause of Loss",
        description="Primary assigned peril or cause of the current loss (e.g. Hail, Wind, Lightning, Sewer Water, Water Damage).",
    )

    loss_description: str | None = Field(
        default=None,
        alias="Loss Description",
        description="Concise description of the current loss incident and damages.",
    )

    acv_policy: str | None = Field(
        default=None,
        alias="ACV Policy (Yes/No)",
        description="'Yes' if Actual Cash Value policy is explicitly stated; 'No' if replacement cost is stated; otherwise null.",
    )

    other_structures_coverage_exclusion: str | None = Field(
        default=None,
        alias="Other Structures Coverage Exclusion",
        description="Explicit exclusion on other structures coverage, or null.",
    )

    non_structural_exclusion: str | None = Field(
        default=None,
        alias="Non-Structural Exclusion",
        description="Explicit non-structural exclusion mentioned, or null.",
    )


class CustomExtractedField(BaseModel):
    """
    Dynamic user-defined field extracted from claim text.
    """

    key: str = Field(
        description="Exact custom field name requested",
    )

    value: str | None = Field(
        default=None,
        description="Extracted value for this custom field, or null if unsupported by text",
    )


class DynamicLLMResponse(BaseModel):
    """
    Fixed internal schema sent to Gemini for structured extraction.
    """

    mandatory: ClaimExtraction = Field(
        description="Extracted values for the standard mandatory insurance claim fields",
    )

    custom_fields: list[CustomExtractedField] = Field(
        default_factory=list,
        description="Extracted values for user-requested custom fields",
    )
