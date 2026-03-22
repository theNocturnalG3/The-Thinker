# The Thinker

A Streamlit app that audits how a news article **reasons, frames, and persuades**.

Instead of trying to declare which political side is “correct,” this project helps the reader think more critically by:

- identifying **possible logical fallacies**
- flagging **loaded or emotionally manipulative language**
- finding **similar coverage** of the same story
- comparing **left / center / right** narratives
- producing a **more logically careful synthesis**
- surfacing **critical questions** the reader should ask

---

## Project goal

Modern news is often a mix of reporting, framing, persuasion, and interpretation. Even when an article is not factually false, it can still:

- overstate a conclusion
- present a false dichotomy
- rely on emotion more than reasoning
- blur uncertainty
- selectively emphasize one narrative over another

This app is designed to provoke thought, not to act as a final truth machine.

It should not say:

> “This is the correct political position.”

It should say:

> “Here are the reasoning patterns, competing frames, possible fallacies, and the strongest questions a critical reader should ask.”

---

## What the app does

Given a news article URL, the app:

1. **Extracts the target article**
   - title
   - source
   - domain
   - author
   - publication date
   - body text

2. **Audits the article's reasoning**
   - possible fallacies
   - headline/body mismatch
   - loaded language
   - core claims
   - neutral rewrite suggestions
   - critical questions

3. **Finds similar coverage**
   - searches Google News via Serper
   - retrieves related articles from other outlets

4. **Compares narratives across outlets**
   - left-leaning
   - center / neutral
   - right-leaning

5. **Builds a cross-source synthesis**
   - shared facts
   - disputed points
   - likely omitted context
   - a more logically careful outlook

---

## Key idea

This is **not** a bias detector in the simplistic sense.

It separates several different things that are often wrongly merged together:

- **logical fallacy**
- **rhetorical framing**
- **tone / emotional language**
- **political leaning**
- **factual uncertainty**

A source can be politically slanted without committing a formal fallacy.
A source can also use sound logic while still selectively framing the story.

---

## Current feature set

### Target article analysis
- URL-based ingestion
- metadata extraction
- body text extraction
- chunked reasoning scans
- article-level synthesis

### Reasoning audit
- possible logical fallacies
- loaded language detection
- headline assessment
- neutral headline suggestion
- neutral summary
- claim extraction
- critical-thinking questions

### Similar coverage search
- Google News retrieval via Serper
- domain normalization
- simple deduplication

### Cross-source comparison
- source leaning lookup via registry
- per-source narrative analysis
- left / center / right comparison
- more logically careful synthesis

---

## Tech stack

- **Python**
- **Streamlit** for the UI
- **OpenAI API** for structured reasoning analysis
- **Serper API** for Google News search
- **httpx** for article fetching
- **BeautifulSoup** + **trafilatura** for extraction/cleaning
- **Pydantic** for typed schemas
- **dotenv** for environment configuration

---

## Project structure

```text
news_reasoning_auditor/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   ├── fallacies.csv
│   └── source_registry.csv
├── src/
│   └── news_reasoning_auditor/
│       ├── __init__.py
│       ├── config.py
│       ├── prompts.py
│       ├── schemas.py
│       ├── utils.py
│       ├── source_registry.py
│       ├── ingest.py
│       ├── search.py
│       ├── llm.py
│       ├── analysis.py
│       ├── compare.py
│       └── pipeline.py
└── tests/
    └── test_registry.py
```

---

## How the pipeline works

```text
User URL
↓
Article ingestion
↓
Target article reasoning audit
↓
Search-plan generation
↓
Similar news retrieval
↓
Source leaning assignment
↓
Per-source comparison analysis
↓
Cross-source synthesis
↓
Streamlit output
```

### Main modules

#### `app.py`
The Streamlit UI.

Responsibilities:
- takes the URL input
- triggers the pipeline
- renders target article details, audit results, similar coverage, and cross-source comparison

#### `pipeline.py`
The orchestrator.

Responsibilities:
- coordinates ingestion, analysis, retrieval, and synthesis
- handles the end-to-end workflow

#### `ingest.py`
The article extraction layer.

Responsibilities:
- fetch HTML
- parse metadata
- extract readable article text
- return structured `ArticleContent`

#### `analysis.py`
The per-article reasoning engine.

Responsibilities:
- build the search plan
- scan article chunks
- synthesize article-level fallacies and claims
- analyze comparison articles

#### `search.py`
The news retrieval layer.

Responsibilities:
- query Serper / Google News
- return structured `NewsSearchResult` objects

#### `source_registry.py`
The source-classification helper.

Responsibilities:
- map news domains to left / center / right / unknown
- use `data/source_registry.csv`

#### `compare.py`
The final synthesis engine.

Responsibilities:
- compare the target article against the retrieved comparison articles
- produce shared facts, disputed points, omitted context, and a more logical outlook

#### `schemas.py`
The typed Pydantic models.

Responsibilities:
- define stable input/output structures
- keep the LLM responses structured and consistent

---

## Setup

### 1. Clone or extract the project

### 2. Create a virtual environment

#### Windows PowerShell

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

#### Windows

```bash
copy .env.example .env
```

#### macOS / Linux

```bash
cp .env.example .env
```

### 5. Fill in your API keys

```env
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
OPENAI_MODEL=gpt-5.4-mini
MAX_COMPARISON_ARTICLES=6
PER_LEANING_CAP=2
REQUEST_TIMEOUT_SECONDS=25
ARTICLE_CHUNK_CHARS=4500
ARTICLE_CHUNK_OVERLAP=400
```

---

## Run the app

```bash
streamlit run app.py
```

Then paste a news article URL into the input box and click **Analyze article**.

---

## Example output

For a single article, the app can return:

### Target article
- title
- source
- domain
- author
- date
- extracted text preview

### Reasoning audit
- article summary
- headline assessment
- neutral headline
- neutral summary
- core claims
- possible fallacies
- loaded language
- critical questions

### Similar coverage
- source name
- source leaning
- article summary
- narrative frame
- tone
- likely fallacies
- who is centered
- what may be missing

### Cross-source comparison
- event summary
- target alignment
- left narrative
- center narrative
- right narrative
- shared facts
- disputed points
- likely omitted context
- more logical outlook
- supporting sources

---

## How to customize it

### 1. Edit media leanings

Update:

```text
data/source_registry.csv
```

This controls how outlets are grouped into:
- left
- center
- right
- unknown

These labels are a starting taxonomy, not objective truth.

### 2. Edit the fallacy list

Update:

```text
data/fallacies.csv
```

This lets you expand or refine the fallacy vocabulary used in prompts and analysis.

### 3. Adjust prompt behavior

Update:

```text
src/news_reasoning_auditor/prompts.py
```

This is where you can make the app:
- more cautious
- more skeptical
- more focused on rhetoric
- less eager to label something as a fallacy

### 4. Tune retrieval settings

Update `.env`:

- `MAX_COMPARISON_ARTICLES`
- `PER_LEANING_CAP`
- `REQUEST_TIMEOUT_SECONDS`
- `ARTICLE_CHUNK_CHARS`
- `ARTICLE_CHUNK_OVERLAP`

---

## Known limitations

### 1. Fallacy detection is probabilistic
This app should say:
- “possible fallacy”
- “likely framing issue”
- “possible false dichotomy”

It should not pretend to be a final judge of truth.

### 2. Some websites block extraction
Certain news sites may return:
- 403 Forbidden
- login walls
- paywalls
- JavaScript-only pages
- anti-bot pages

So extraction can fail even when the URL works in a normal browser.

### 3. Source labels are inherently debatable
Media leaning is not a perfect science.
The registry is editable because classification is contextual and often disputed.

### 4. Similar article search is only as good as the query
The app builds a search plan, but retrieval may still miss important coverage, especially for niche or regional stories.

### 5. “Balanced” does not mean “true”
A middle-ground summary is not automatically the correct interpretation.
The goal is higher reasoning quality, not false neutrality.

---

## Troubleshooting

### Missing environment variables
If you see an error about missing keys, make sure `.env` exists and includes:

- `OPENAI_API_KEY`
- `SERPER_API_KEY`

### `HTTPStatusError` or fetch failure
If article extraction fails, the site may be:
- blocking bots
- paywalled
- redirecting to a non-article page
- returning a temporary server error

Try:
- pasting the final clean article URL
- avoiding search-result pages or shortened links
- testing a different publisher

### `ModuleNotFoundError`
Usually means:
- you ran `app.py` without the full project structure
- or you are not running from the project root

Run:

```bash
streamlit run app.py
```

from the main project folder.

### Pydantic field mismatch / UI attribute errors
If the UI references a field that does not exist in the schema, update the UI to match the Pydantic model definitions in:

```text
src/news_reasoning_auditor/schemas.py
```

---

## Suggested next upgrades

### Product improvements
- sentence-level highlighting in the UI
- article clustering by event
- side-by-side source comparison table
- export to PDF / HTML / Markdown
- saved analysis history
- dashboard of repeated fallacies by source

### Technical improvements
- stronger retry and fallback extraction logic
- caching for article content and search results
- async retrieval for faster multi-source analysis
- evaluation dataset for calibration
- logging and observability
- unit tests for ingestion and pipeline steps

### Research extensions
- stance detection
- argument mining
- quote attribution
- omission analysis
- fact-check integration
- RAG over prior analyses

---

## Safety and ethics note

This project deals with political and media narratives, so it should be designed carefully.

Good design principles:
- avoid claiming absolute truth
- distinguish facts from interpretation
- surface uncertainty clearly
- explain why each fallacy label was assigned
- cite or link comparison sources
- avoid treating “centrist” output as inherently superior

The purpose is to sharpen the reader’s critical thinking, not to replace it.

---

## Why this project is interesting

This is more than a simple LLM summarizer.

It sits at the intersection of:
- NLP
- argument analysis
- media framing analysis
- information literacy
- human-centered AI

That makes it a strong portfolio project because it combines:
- data extraction
- retrieval
- structured LLM reasoning
- UI design
- product philosophy

---

## Future product vision

A mature version of this app could:

- take a single article URL
- identify sentence-level rhetorical weaknesses
- compare the event across multiple ideological lenses
- distinguish hard facts from contested interpretation
- produce a transparent, evidence-backed reasoning report
- help users become more reflective readers of media

---

## License
MIT License

---

## Author

Built by Goutham Manoharan.

---
###Updates to look forward to:
- add sentence-level text highlighting in the UI
- add article clustering by event
- add fact-check source integration
- add report export to PDF / HTML
- add RAG over saved prior analyses
- add evaluation datasets for calibration
- turning this into a tool, easy for you to access
