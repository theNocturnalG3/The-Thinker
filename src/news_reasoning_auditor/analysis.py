from __future__ import annotations

import json
from typing import Iterable

import pandas as pd

from .config import Settings
from .llm import LLMClient
from .prompts import (
    article_synthesis_prompt,
    chunk_scan_prompt,
    comparable_article_prompt,
    search_plan_prompt,
)
from .schemas import (
    ArticleAudit,
    ArticleContent,
    ChunkReasoningScan,
    ComparableArticleAnalysis,
    SearchPlan,
)
from .utils import chunk_text, safe_json_dumps


class ReasoningAnalyzer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.llm = LLMClient(self.settings)
        self.fallacies_df = pd.read_csv(self.settings.fallacies_path)

    def _fallacies_reference(self) -> str:
        return self.fallacies_df.to_csv(index=False)

    def build_search_plan(self, article: ArticleContent) -> SearchPlan:
        prompt = search_plan_prompt(
            title=article.title,
            source_name=article.source_name,
            description=article.description or "",
            article_excerpt=article.text[:3000],
        )
        return self.llm.parse(SearchPlan, prompt)

    def scan_article_chunks(self, article: ArticleContent) -> list[ChunkReasoningScan]:
        chunks = chunk_text(
            article.text,
            max_chars=self.settings.article_chunk_chars,
            overlap=self.settings.article_chunk_overlap,
        )

        scans: list[ChunkReasoningScan] = []
        fallacies_reference = self._fallacies_reference()

        for idx, chunk in enumerate(chunks, start=1):
            prompt = chunk_scan_prompt(
                chunk_id=idx,
                title=article.title,
                source_name=article.source_name,
                fallacies_reference=fallacies_reference,
                text_chunk=chunk,
            )
            scan = self.llm.parse(ChunkReasoningScan, prompt)
            # Force the chunk id from our pipeline for consistency
            scan.chunk_id = idx
            scans.append(scan)
        return scans

    def synthesize_article_audit(
        self,
        article: ArticleContent,
        chunk_scans: Iterable[ChunkReasoningScan],
    ) -> ArticleAudit:
        chunk_scans_json = safe_json_dumps([scan.model_dump() for scan in chunk_scans])
        prompt = article_synthesis_prompt(
            title=article.title,
            source_name=article.source_name,
            article_text=article.text[:12000],
            chunk_scans_json=chunk_scans_json,
        )
        return self.llm.parse(ArticleAudit, prompt)

    def analyze_target_article(self, article: ArticleContent) -> tuple[list[ChunkReasoningScan], ArticleAudit]:
        chunk_scans = self.scan_article_chunks(article)
        final_audit = self.synthesize_article_audit(article, chunk_scans)
        return chunk_scans, final_audit

    def analyze_comparable_article(
        self,
        target_article: ArticleContent,
        target_audit: ArticleAudit,
        comparison_article: ArticleContent,
        source_leaning: str,
    ) -> ComparableArticleAnalysis:
        prompt = comparable_article_prompt(
            target_title=target_article.title,
            target_summary=target_audit.article_summary,
            target_fallacies_json=json.dumps(
                [item.model_dump() for item in target_audit.dominant_fallacies],
                ensure_ascii=False,
            ),
            source_name=comparison_article.source_name,
            source_leaning=source_leaning,
            article_title=comparison_article.title,
            article_text=comparison_article.text[:9000],
        )
        analysis = self.llm.parse(ComparableArticleAnalysis, prompt)
        analysis.source_name = comparison_article.source_name
        analysis.source_domain = comparison_article.domain
        analysis.source_leaning = source_leaning
        analysis.article_url = comparison_article.url
        return analysis
