from __future__ import annotations

from textwrap import dedent


def system_guardrails() -> str:
    return dedent(
        """
        You are a critical-reading and reasoning assistant for news analysis.

        Rules:
        1. Do NOT claim political truth or moral finality.
        2. Treat all fallacy labels as "possible" or "likely", not absolute verdicts.
        3. Separate factual claims, interpretation, rhetoric, and omission.
        4. Prefer careful, evidence-aware language over ideological language.
        5. If evidence is weak or ambiguous, say so plainly.
        6. Focus on reasoning quality, framing, and narrative differences.
        7. Never invent article details that are not present in the input.
        """
    ).strip()


def search_plan_prompt(title: str, source_name: str, description: str, article_excerpt: str) -> str:
    return dedent(
        f"""
        Create a Google News search plan for finding coverage of the same event.

        Target article title: {title}
        Source: {source_name}
        Description: {description or "n/a"}

        Article excerpt:
        {article_excerpt}

        Produce:
        - one concise event query
        - a short list of must-have search terms
        - named entities
        - one short rationale

        Optimize the query for retrieving articles about the same event, not opinion pieces on broad ideology.
        """
    ).strip()


def chunk_scan_prompt(chunk_id: int, title: str, source_name: str, fallacies_reference: str, text_chunk: str) -> str:
    return dedent(
        f"""
        Analyze the following article chunk for reasoning quality.

        Target article title: {title}
        Source: {source_name}
        Chunk id: {chunk_id}

        Fallacies reference:
        {fallacies_reference}

        Text chunk:
        {text_chunk}

        Return:
        - a short chunk summary
        - the key claims in this chunk
        - possible logical fallacies in this chunk
        - emotionally loaded language or manipulative wording in this chunk

        IMPORTANT:
        - Only flag fallacies when there is a real textual basis
        - Use low confidence when uncertain
        - Do not over-label
        """
    ).strip()


def article_synthesis_prompt(
    title: str,
    source_name: str,
    article_text: str,
    chunk_scans_json: str,
) -> str:
    return dedent(
        f"""
        Synthesize a final reasoning audit for one article.

        Article title: {title}
        Source: {source_name}

        Full article text:
        {article_text}

        Chunk-level scans:
        {chunk_scans_json}

        Produce:
        - overall summary of the article
        - headline assessment (including mismatch or overclaim risk)
        - consolidated core claims
        - dominant possible fallacies
        - loaded language worth noting
        - strongest counterpoints a critical reader should consider
        - critical questions a careful reader should ask
        - a less biased headline
        - a more logically careful summary

        IMPORTANT:
        - Keep the tone analytical, not partisan
        - Do not claim certainty where the text is ambiguous
        - This is a reasoning audit, not fact-checking
        """
    ).strip()


def comparable_article_prompt(
    target_title: str,
    target_summary: str,
    target_fallacies_json: str,
    source_name: str,
    source_leaning: str,
    article_title: str,
    article_text: str,
) -> str:
    return dedent(
        f"""
        Compare this article's narrative to a target article about the same event.

        Target article title: {target_title}
        Target summary: {target_summary}
        Target article's possible fallacies: {target_fallacies_json}

        Comparison source: {source_name}
        Comparison source leaning: {source_leaning}
        Comparison article title: {article_title}

        Comparison article text:
        {article_text}

        Produce:
        - a short summary
        - the narrative frame used by this source
        - the main claims it makes
        - likely fallacies or reasoning weaknesses
        - overall tone
        - who is centered in the narrative
        - what is blurred, omitted, or backgrounded

        IMPORTANT:
        - Do not force ideological differences where none are visible
        - Stay grounded in the text only
        """
    ).strip()


def cross_source_prompt(
    target_article_json: str,
    target_audit_json: str,
    comparisons_json: str,
) -> str:
    return dedent(
        f"""
        Build a cross-source reasoning comparison from the following inputs.

        Target article:
        {target_article_json}

        Target reasoning audit:
        {target_audit_json}

        Comparison articles:
        {comparisons_json}

        Produce:
        - a short event summary
        - how the target source aligns or differs from surrounding coverage
        - summary of left narrative
        - summary of center narrative
        - summary of right narrative
        - facts shared across sources
        - points that remain disputed
        - likely omitted context
        - a more logically careful outlook that strips away loaded framing
        - supporting sources for that outlook
        - one cautionary note reminding the user not to confuse synthesis with final truth

        IMPORTANT:
        - The "more logical outlook" is NOT the political middle by default
        - It should instead preserve the most widely supported claims, state uncertainty, and avoid manipulative framing
        """
    ).strip()
