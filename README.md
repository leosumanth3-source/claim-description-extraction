# Claim Field Extractor

A small FastAPI service that extracts structured insurance-claim fields with Google Gemini.

## Routes

Only two routes are exposed:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health check |
| `POST` | `/api/v1/claims/extract` | Extract fields from one claim narrative |

There are no batch, cache, metrics, examples, field-listing, readiness, liveness, or metadata endpoints.

## Project layout

```text
app/
├── api/                 # HTTP handlers: health and extract only
├── core/                # Logging and error handling
├── schemas/             # Request, response, and Gemini structured-output models
├── services/            # Extraction business logic
├── config.py            # Environment settings
├── llm.py               # Gemini client
├── prompts.py           # Extraction instructions
└── main.py              # FastAPI application factory
```

## Setup and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set GEMINI_API_KEY in .env
uvicorn app.main:app --reload
```

## Extract one claim

```bash
curl -X POST http://localhost:8000/api/v1/claims/extract \
  -H 'Content-Type: text/plain' \
  --data-binary $'claim_description: The 1985 home has roof damage from hail.\ncustom_field: Adjuster Name'
```

The response contains the extracted standard fields. Missing evidence is returned as `null`.

Each successful response contains a generated UUID `request_id` and a `performance` object:

```json
{
  "success": true,
  "request_id": "10ba8588-593e-4470-adeb-1288417de09f",
  "data": {"Year Built": 1985},
  "performance": {
    "model": "gemini-3.1-flash-lite",
    "latency_seconds": 1.24,
    "populated_fields": 1,
    "total_fields": 44
  }
}
```

Send plain text, not a JSON object. `claim_description:` is required; `custom_field:` is an optional single text value for one extra field to extract. The claim description can span multiple lines.

## Test

```bash
pytest -q
```
