from __future__ import annotations

import json
import re
from typing import Iterable
from urllib.parse import urlparse

import tldextract


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def chunk_text(text: str, max_chars: int = 4500, overlap: int = 400) -> list[str]:
    text = normalize_whitespace(text)
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.netloc:
        return ""
    ext = tldextract.extract(parsed.netloc)
    if ext.suffix:
        return f"{ext.domain}.{ext.suffix}".lower()
    return parsed.netloc.lower()


def safe_json_dumps(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def truncate(text: str, limit: int = 5000) -> str:
    text = normalize_whitespace(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(item.strip())
    return output
