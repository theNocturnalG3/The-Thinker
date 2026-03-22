from __future__ import annotations

from .llm import LLMClient
from .prompts import cross_source_prompt
from .schemas import (
    ArticleAudit,
    ArticleContent,
    ComparableArticleAnalysis,
    CrossSourceComparison,
)
from .utils import safe_json_dumps


class NarrativeComparer:
    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def compare(
        self,
        target_article: ArticleContent,
        target_audit: ArticleAudit,
        comparison_articles: list[ComparableArticleAnalysis],
    ) -> CrossSourceComparison:
        prompt = cross_source_prompt(
            target_article_json=safe_json_dumps(target_article.model_dump()),
            target_audit_json=safe_json_dumps(target_audit.model_dump()),
            comparisons_json=safe_json_dumps([item.model_dump() for item in comparison_articles]),
        )
        return self.llm.parse(CrossSourceComparison, prompt)
