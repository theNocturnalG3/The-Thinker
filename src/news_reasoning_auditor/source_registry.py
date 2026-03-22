from __future__ import annotations

import pandas as pd

from .config import Settings
from .schemas import Leaning, SourceProfile


class SourceRegistry:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.df = pd.read_csv(self.settings.source_registry_path)

    def match(self, domain: str) -> SourceProfile | None:
        domain = (domain or "").lower().strip()
        if not domain:
            return None

        for _, row in self.df.iterrows():
            registry_domain = str(row["domain"]).lower().strip()
            if domain == registry_domain or domain.endswith("." + registry_domain):
                return SourceProfile(
                    source_name=str(row["source_name"]),
                    domain=registry_domain,
                    source_leaning=str(row["source_leaning"]),
                    country=str(row.get("country", "unknown")),
                    notes=str(row.get("notes", "")),
                )
        return None

    def leaning_for(self, domain: str) -> Leaning:
        match = self.match(domain)
        if not match:
            return "unknown"
        return match.source_leaning
