from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


Leaning = Literal["left", "center", "right", "unknown"]
ClaimType = Literal["factual", "interpretive", "causal", "prediction", "value_judgment"]
SupportStatus = Literal["supported_in_article", "asserted_without_support", "unclear"]
Severity = Literal["low", "medium", "high"]


class SourceProfile(BaseModel):
    source_name: str
    domain: str
    source_leaning: Leaning
    country: str = "unknown"
    notes: str = ""


class ArticleContent(BaseModel):
    url: str
    title: str
    source_name: str
    domain: str
    author: Optional[str] = None
    published_at: Optional[str] = None
    description: Optional[str] = None
    text: str


class ClaimItem(BaseModel):
    text: str
    claim_type: ClaimType
    support_status: SupportStatus


class FallacyHit(BaseModel):
    label: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_span: str
    explanation: str
    why_it_matters: str


class LoadedLanguageHit(BaseModel):
    phrase: str
    tone: str
    effect: str
    rewrite: str


class CriticalQuestion(BaseModel):
    question: str
    why_ask_it: str


class ChunkReasoningScan(BaseModel):
    chunk_id: int
    chunk_summary: str
    claims: list[ClaimItem] = Field(default_factory=list)
    fallacies: list[FallacyHit] = Field(default_factory=list)
    loaded_language: list[LoadedLanguageHit] = Field(default_factory=list)


class ArticleAudit(BaseModel):
    article_summary: str
    headline_assessment: str
    core_claims: list[ClaimItem] = Field(default_factory=list)
    dominant_fallacies: list[FallacyHit] = Field(default_factory=list)
    loaded_language: list[LoadedLanguageHit] = Field(default_factory=list)
    strongest_counterpoints: list[str] = Field(default_factory=list)
    critical_questions: list[CriticalQuestion] = Field(default_factory=list)
    neutral_headline: str
    neutral_summary: str


class SearchPlan(BaseModel):
    event_query: str
    must_have_terms: list[str] = Field(default_factory=list)
    named_entities: list[str] = Field(default_factory=list)
    rationale: str


class NewsSearchResult(BaseModel):
    title: str
    url: str
    source_name: str
    snippet: str = ""
    published_at: Optional[str] = None
    domain: str


class ComparableArticleAnalysis(BaseModel):
    source_name: str
    title: str
    source_domain: str
    source_leaning: Leaning
    article_url: str
    summary: str
    narrative_frame: str
    main_claims: list[str] = Field(default_factory=list)
    likely_fallacies: list[str] = Field(default_factory=list)
    tone: str
    who_is_centered: list[str] = Field(default_factory=list)
    who_is_blurred_or_missing: list[str] = Field(default_factory=list)


class SupportingSource(BaseModel):
    source_name: str
    article_url: str
    why_it_supports: str


class CrossSourceComparison(BaseModel):
    event_summary: str
    target_alignment: str
    left_narrative: str
    center_narrative: str
    right_narrative: str
    shared_facts: list[str] = Field(default_factory=list)
    disputed_points: list[str] = Field(default_factory=list)
    likely_omitted_context: list[str] = Field(default_factory=list)
    more_logical_outlook: str
    supporting_sources: list[SupportingSource] = Field(default_factory=list)
    cautionary_note: str


class FullAnalysisReport(BaseModel):
    target_article: ArticleContent
    target_audit: ArticleAudit
    search_plan: SearchPlan
    retrieved_articles: list[NewsSearchResult] = Field(default_factory=list)
    comparison_articles: list[ComparableArticleAnalysis] = Field(default_factory=list)
    cross_source_comparison: CrossSourceComparison
