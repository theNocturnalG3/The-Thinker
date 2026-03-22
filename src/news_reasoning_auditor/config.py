from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    max_comparison_articles: int = int(os.getenv("MAX_COMPARISON_ARTICLES", "6"))
    per_leaning_cap: int = int(os.getenv("PER_LEANING_CAP", "2"))
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "25"))
    article_chunk_chars: int = int(os.getenv("ARTICLE_CHUNK_CHARS", "4500"))
    article_chunk_overlap: int = int(os.getenv("ARTICLE_CHUNK_OVERLAP", "400"))

    @property
    def source_registry_path(self) -> Path:
        return DATA_DIR / "source_registry.csv"

    @property
    def fallacies_path(self) -> Path:
        return DATA_DIR / "fallacies.csv"

    def validate(self) -> None:
        missing = []
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.serper_api_key:
            missing.append("SERPER_API_KEY")

        if missing:
            raise ValueError(
                "Missing environment variables: "
                + ", ".join(missing)
                + ". Copy .env.example to .env and fill them in."
            )
