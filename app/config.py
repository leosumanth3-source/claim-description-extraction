"""Application settings loaded from .env"""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-lite"
    app_name: str = "Claim Field Extractor"
    app_version: str = "1.0.0"
    app_env: str = "production"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return Settings(
        gemini_api_key=api_key,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip(),
        app_name=os.getenv("APP_NAME", "Claim Field Extractor").strip(),
        app_version=os.getenv("APP_VERSION", "1.0.0").strip(),
        app_env=os.getenv("APP_ENV", "production").strip(),
        api_prefix=os.getenv("API_PREFIX", "/api/v1").strip(),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper().strip(),
        host=os.getenv("HOST", "0.0.0.0").strip(),
        port=int(os.getenv("PORT", "8000")),
    )
