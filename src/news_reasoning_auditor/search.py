from __future__ import annotations

from typing import Iterable

import httpx

from .config import Settings
from .schemas import NewsSearchResult
from .utils import dedupe_preserve_order, domain_from_url


class SerperNewsSearch:
    """
    Thin Serper wrapper. The user already uses Serper in the notebook, so this keeps
    the same retrieval provider while moving to a cleaner architecture.
    """

    endpoint = "https://google.serper.dev/news"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def search_news(self, query: str, k: int = 10) -> list[NewsSearchResult]:
        headers = {
            "X-API-KEY": self.settings.serper_api_key,
            "Content-Type": "application/json",
        }
        payload = {"q": query, "num": k}
        with httpx.Client(timeout=self.settings.request_timeout_seconds) as client:
            response = client.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        news_items = data.get("news", []) or []
        results: list[NewsSearchResult] = []
        for item in news_items:
            url = item.get("link") or ""
            if not url:
                continue
            results.append(
                NewsSearchResult(
                    title=item.get("title", "Untitled result"),
                    url=url,
                    source_name=item.get("source", domain_from_url(url)),
                    snippet=item.get("snippet", "") or "",
                    published_at=item.get("date"),
                    domain=domain_from_url(url),
                )
            )
        return results

    @staticmethod
    def unique_urls(results: Iterable[NewsSearchResult]) -> list[NewsSearchResult]:
        seen: set[str] = set()
        deduped: list[NewsSearchResult] = []
        for result in results:
            if result.url in seen:
                continue
            seen.add(result.url)
            deduped.append(result)
        return deduped

    @staticmethod
    def expand_queries(base_query: str, must_have_terms: list[str]) -> list[str]:
        queries = [base_query]
        if must_have_terms:
            narrow = base_query + " " + " ".join(dedupe_preserve_order(must_have_terms[:4]))
            queries.append(narrow)
        return dedupe_preserve_order(queries)
