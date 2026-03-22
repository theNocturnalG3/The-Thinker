from __future__ import annotations

import json

import streamlit as st

from src.news_reasoning_auditor.pipeline import NewsReasoningPipeline

st.set_page_config(
    page_title="News Reasoning Auditor",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 News Reasoning Auditor")
st.caption(
    "Audit a news article for possible fallacies, compare left/center/right narratives, "
    "and generate a more logically careful outlook."
)

with st.sidebar:
    st.header("About")
    st.write(
        "This app is not a truth machine. It is a critical-reading assistant that shows "
        "reasoning patterns, framing differences, and open questions."
    )

url = st.text_input("Paste a news article URL")
run = st.button("Analyze article", type="primary")

if run:
    if not url.strip():
        st.error("Please provide a news article URL.")
        st.stop()

    pipeline = NewsReasoningPipeline()

    with st.spinner("Extracting article, auditing reasoning, searching similar coverage, and comparing narratives..."):
        try:
            report = pipeline.run(url.strip())
        except Exception as exc:  # pragma: no cover - UI path
            st.error(str(exc))
            st.stop()

    st.success("Analysis complete.")

    st.subheader("Target article")
    st.write(f"**Title:** {report.target_article.title}")
    st.write(f"**Source:** {report.target_article.source_name}")
    st.write(f"**Domain:** {report.target_article.domain}")
    st.write(f"**URL:** {report.target_article.url}")
    if report.target_article.published_at:
        st.write(f"**Published:** {report.target_article.published_at}")
    if report.target_article.author:
        st.write(f"**Author:** {report.target_article.author}")

    with st.expander("Extracted article text preview", expanded=False):
        st.write(report.target_article.text[:6000] + ("..." if len(report.target_article.text) > 6000 else ""))

    st.subheader("Reasoning audit")
    st.write(f"**Article summary:** {report.target_audit.article_summary}")
    st.write(f"**Headline assessment:** {report.target_audit.headline_assessment}")
    st.write(f"**Neutral headline suggestion:** {report.target_audit.neutral_headline}")
    st.write(f"**Neutral summary:** {report.target_audit.neutral_summary}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Core claims**")
        for claim in report.target_audit.core_claims:
            st.markdown(
                f"- **{claim.claim_type}**: {claim.text} "
                f"_(support: {claim.support_status})_"
            )

        st.markdown("**Critical questions**")
        for q in report.target_audit.critical_questions:
            st.markdown(f"- **{q.question}** — {q.why_ask_it}")

    with col2:
        st.markdown("**Possible fallacies**")
        for hit in report.target_audit.dominant_fallacies:
            st.markdown(
                f"- **{hit.label}** (severity: {hit.severity}, confidence: {hit.confidence:.2f})\n"
                f"  - Evidence: {hit.evidence_span}\n"
                f"  - Why: {hit.explanation}\n"
                f"  - Why it matters: {hit.why_it_matters}"
            )

        st.markdown("**Loaded language**")
        for item in report.target_audit.loaded_language:
            st.markdown(
                f"- **{item.phrase}** → {item.effect}\n"
                f"  - Tone: {item.tone}\n"
                f"  - Rewrite: {item.rewrite}"
            )

    st.subheader("Similar coverage")
    
    retrieved_by_url = {item.url: item for item in report.retrieved_articles}
    
    for article in report.comparison_articles:
        retrieved = retrieved_by_url.get(article.article_url)
        display_title = retrieved.title if retrieved else article.source_domain
    
        with st.expander(f"{article.source_name} | {display_title}"):
            st.write(f"**URL:** {article.article_url}")
            st.write(f"**Domain:** {article.source_domain}")
            st.write(f"**Leaning:** {article.source_leaning}")
            st.write(f"**Summary:** {article.summary}")
            st.write(f"**Narrative frame:** {article.narrative_frame}")
            st.write(f"**Tone:** {article.tone}")
    
            st.write("**Likely fallacies:**")
            if article.likely_fallacies:
                for fallacy in article.likely_fallacies:
                    st.markdown(f"- {fallacy}")
            else:
                st.markdown("- None identified")
    
            st.write("**Main claims:**")
            if article.main_claims:
                for claim in article.main_claims:
                    st.markdown(f"- {claim}")
            else:
                st.markdown("- None extracted")
    
            st.write("**Who is centered?**")
            if article.who_is_centered:
                for item in article.who_is_centered:
                    st.markdown(f"- {item}")
            else:
                st.markdown("- Not specified")
    
            st.write("**What may be missing or blurred?**")
            if article.who_is_blurred_or_missing:
                for item in article.who_is_blurred_or_missing:
                    st.markdown(f"- {item}")
            else:
                st.markdown("- None noted")

    st.subheader("Cross-source comparison")
    st.write(f"**Event summary:** {report.cross_source_comparison.event_summary}")
    st.write(f"**Target alignment:** {report.cross_source_comparison.target_alignment}")
    st.write(f"**Left narrative:** {report.cross_source_comparison.left_narrative}")
    st.write(f"**Center narrative:** {report.cross_source_comparison.center_narrative}")
    st.write(f"**Right narrative:** {report.cross_source_comparison.right_narrative}")

    st.markdown("**Shared facts**")
    for item in report.cross_source_comparison.shared_facts:
        st.markdown(f"- {item}")

    st.markdown("**Disputed points**")
    for item in report.cross_source_comparison.disputed_points:
        st.markdown(f"- {item}")

    st.markdown("**Likely omitted context**")
    for item in report.cross_source_comparison.likely_omitted_context:
        st.markdown(f"- {item}")

    st.markdown("**More logically careful outlook**")
    st.write(report.cross_source_comparison.more_logical_outlook)

    st.markdown("**Supporting sources for the synthesis**")
    for item in report.cross_source_comparison.supporting_sources:
        st.markdown(f"- **{item.source_name}** — {item.why_it_supports} ({item.article_url})")

    st.info(report.cross_source_comparison.cautionary_note)

    st.subheader("Raw JSON")
    st.code(json.dumps(report.model_dump(), indent=2), language="json")
