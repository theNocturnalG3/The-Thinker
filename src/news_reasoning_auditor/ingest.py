from __future__ import annotations

import json
from typing import Optional

import httpx
import trafilatura
from bs4 import BeautifulSoup

from .config import Settings
from .schemas import ArticleContent
from .utils import domain_from_url, normalize_whitespace


class ArticleIngestor:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def fetch_html(self, url: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }

        try:
            with httpx.Client(
                timeout=self.settings.request_timeout_seconds,
                follow_redirects=True,
                headers=headers,
            ) as client:
                response = client.get(url)

            if response.status_code >= 400:
                raise ValueError(
                    f"Could not fetch article. "
                    f"HTTP {response.status_code} from {response.url}. "
                    f"This usually means the site blocks scraping, requires login, "
                    f"is behind a paywall, or the URL is invalid."
                )

            return response.text

        except httpx.TimeoutException as exc:
            raise ValueError(
                f"Timed out while fetching the article: {url}"
            ) from exc
        except httpx.RequestError as exc:
            raise ValueError(
                f"Network error while fetching the article: {url}. Details: {exc}"
            ) from exc

    def _parse_metadata(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")

        def meta_value(*names: str) -> Optional[str]:
            for name in names:
                tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
                if tag and tag.get("content"):
                    return normalize_whitespace(tag["content"])
            return None

        title = (
            meta_value("og:title", "twitter:title")
            or normalize_whitespace(soup.title.string if soup.title and soup.title.string else "")
            or "Untitled article"
        )
        description = meta_value("description", "og:description", "twitter:description")
        author = meta_value("author", "article:author")
        published_at = meta_value("article:published_time", "pubdate", "date")

        source_name = meta_value("og:site_name") or domain_from_url(url)
        return {
            "title": title,
            "description": description,
            "author": author,
            "published_at": published_at,
            "source_name": source_name,
        }

    def _extract_text(self, html: str, url: str) -> str:
        extracted_json = trafilatura.extract(
            html,
            url=url,
            with_metadata=True,
            include_comments=False,
            include_tables=False,
            output_format="json",
        )
        if extracted_json:
            payload = json.loads(extracted_json)
            text = normalize_whitespace(payload.get("text", ""))
            if text:
                return text

        fallback = trafilatura.extract(
            html,
            url=url,
            with_metadata=False,
            include_comments=False,
            include_tables=False,
        )
        text = normalize_whitespace(fallback or "")
        if text:
            return text

        soup = BeautifulSoup(html, "html.parser")
        text = normalize_whitespace(" ".join(soup.stripped_strings))
        return text

    def extract(self, url: str) -> ArticleContent:
        html = self.fetch_html(url)
        metadata = self._parse_metadata(html, url)
        text = self._extract_text(html, url)

        if len(text) < 500:
            raise ValueError(
                "The article text extraction returned too little content. "
                "This can happen with paywalls, script-heavy pages, or blocked scraping."
            )

        return ArticleContent(
            url=url,
            title=metadata["title"],
            source_name=metadata["source_name"],
            domain=domain_from_url(url),
            author=metadata.get("author"),
            published_at=metadata.get("published_at"),
            description=metadata.get("description"),
            text=text,
        )