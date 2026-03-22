from __future__ import annotations

from collections import defaultdict

from .analysis import ReasoningAnalyzer
from .compare import NarrativeComparer
from .config import Settings
from .ingest import ArticleIngestor
from .schemas import ComparableArticleAnalysis, FullAnalysisReport, NewsSearchResult
from .search import SerperNewsSearch
from .source_registry import SourceRegistry


class NewsReasoningPipeline:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.settings.validate()

        self.ingestor = ArticleIngestor(self.settings)
        self.search = SerperNewsSearch(self.settings)
        self.registry = SourceRegistry(self.settings)
        self.analyzer = ReasoningAnalyzer(self.settings)
        self.comparer = NarrativeComparer(self.analyzer.llm)

    def _retrieve_comparison_candidates(self, event_query: str, must_have_terms: list[str]) -> list[NewsSearchResult]:
        combined: list[NewsSearchResult] = []
        for query in self.search.expand_queries(event_query, must_have_terms):
            combined.extend(self.search.search_news(query, k=10))
        return self.search.unique_urls(combined)

    def _select_balanced_results(self, results: list[NewsSearchResult], target_url: str, target_domain: str) -> list[NewsSearchResult]:
        by_leaning: dict[str, list[NewsSearchResult]] = defaultdict(list)

        for result in results:
            if result.url == target_url:
                continue
            if result.domain == target_domain:
                continue
            leaning = self.registry.leaning_for(result.domain)
            by_leaning[leaning].append(result)

        selected: list[NewsSearchResult] = []
        for bucket in ("left", "center", "right"):
            selected.extend(by_leaning.get(bucket, [])[: self.settings.per_leaning_cap])

        # Backfill with unknown or overflow, if needed
        if len(selected) < self.settings.max_comparison_articles:
            remaining: list[NewsSearchResult] = []
            for bucket, items in by_leaning.items():
                if bucket in {"left", "center", "right"}:
                    remaining.extend(items[self.settings.per_leaning_cap :])
                else:
                    remaining.extend(items)
            for item in remaining:
                if len(selected) >= self.settings.max_comparison_articles:
                    break
                if item not in selected:
                    selected.append(item)

        return selected[: self.settings.max_comparison_articles]

    def run(self, url: str) -> FullAnalysisReport:
        try:
            target_article = self.ingestor.extract(url)
        except Exception as exc:
            raise ValueError(
                f"Target article could not be extracted. {exc}"
            ) from exc
    
        _, target_audit = self.analyzer.analyze_target_article(target_article)
        search_plan = self.analyzer.build_search_plan(target_article)
    
        retrieved = self._retrieve_comparison_candidates(
            event_query=search_plan.event_query,
            must_have_terms=search_plan.must_have_terms,
        )
        selected = self._select_balanced_results(
            results=retrieved,
            target_url=target_article.url,
            target_domain=target_article.domain,
        )
    
        comparison_analyses: list[ComparableArticleAnalysis] = []
        for result in selected:
            try:
                article = self.ingestor.extract(result.url)
                leaning = self.registry.leaning_for(article.domain)
                comparison = self.analyzer.analyze_comparable_article(
                    target_article=target_article,
                    target_audit=target_audit,
                    comparison_article=article,
                    source_leaning=leaning,
                )
                comparison_analyses.append(comparison)
            except Exception:
                continue
            
        cross_source = self.comparer.compare(
            target_article=target_article,
            target_audit=target_audit,
            comparison_articles=comparison_analyses,
        )
    
        return FullAnalysisReport(
            target_article=target_article,
            target_audit=target_audit,
            search_plan=search_plan,
            retrieved_articles=selected,
            comparison_articles=comparison_analyses,
            cross_source_comparison=cross_source,
        )