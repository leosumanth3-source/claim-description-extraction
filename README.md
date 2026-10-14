# Claim Field Extractor — Using Gemini

A self-contained Streamlit application that extracts a fixed set of claim fields from unstructured claim text using Gemini.

## Project structure

```text
app/
├── config.py                       # Environment-based configuration
├── llm.py                          # Gemini client and structured-response parsing
├── prompts.py                      # Prompt construction
├── schemas.py                      # Pydantic response models and standard fields
├── services/
│   └── claim_extraction.py          # Framework-independent extraction service
└── streamlit_app.py                 # Streamlit user interface
```

## Model

Default model: `gemini-3.1-flash-lite`

The model is controlled by `GEMINI_MODEL`, so it can be changed without changing application code.

## Required output

The service always returns exactly these fields:

- Year Built
- House Size (Square Footage)
- Number of Stories
- Roof Type
- Structure Type
- Interior Damage (Yes/No)
- Roof Damage (Yes/No)
- Type of Roof Damage
- Missing Shingles
- Hail Damage
- Wind Damage
- Rain Leakage (Yes/No)
- Water Damage (Yes/No)
- Rooms Affected by Water
- Affected Room Names (Kitchen, Living Room, Basement)
- Wall Damage
- Sheetrock Damage
- Flooring Damage
- Ceiling/Closet Area Damage
- Humidity Damage
- Sewer Backup / Sewer Water
- Lightning Damage
- Electrical / Electronics Damage
- Lights Damage
- HVAC / AC Damage
- Endorsements
- Deductible Type
- Deductible Amount
- Prior Losses
- Prior Loss Date
- Prior Loss Type
- Coverage Limits
- Dwelling Coverage Limit
- Other Structures Coverage Limit
- Personal Property Coverage Limit
- Additional Living Expenses Limit
- Roof Coverage Limitations
- Construction Type
- Occupancy Type
- Cause of Loss
- Loss Description
- ACV Policy (Yes/No)
- Other Structures Coverage Exclusion
- Non-Structural Exclusion

Missing evidence is returned as `null`.

## Why Gemini Flash-Lite

- Low-latency response performance
- High-throughput execution
- Cost-efficient processing
- Structured output support
- Large context capacity for long claim descriptions
- Stronger performance than previous Flash-Lite generations

## Design notes

- Gemini remains the separate inference provider.
- Pydantic validates the structured Gemini response.
- The model and API key are configured through environment variables.
- The Streamlit interface extracts the standard claim schema and optional session-only custom fields without a separate backend process.

For production traffic above the Gemini free-tier limits, move the same code to a paid Gemini tier rather than rewriting the extraction logic.

## Run the standalone Streamlit app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Put your Gemini API key into .env
streamlit run app/streamlit_app.py
```

Only the `streamlit run` command is required. The Streamlit app keeps custom fields in the active browser session and sends extraction requests directly to Gemini.

## Important data-policy note

Google's current Gemini API pricing page says the Free tier may use submitted content to improve Google products. For real insurance/PII production workloads, review the applicable data-processing terms and use a paid/enterprise configuration when required.
