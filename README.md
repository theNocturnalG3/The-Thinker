# News Reasoning Auditor

A Streamlit app that takes a news URL and produces a **reasoning audit** rather than a “truth verdict”.

It does four things:

1. Extracts the target article
2. Detects **possible logical fallacies**, loaded language, and headline/body mismatch
3. Searches for **similar coverage** on Google News via Serper
4. Compares narratives across **left / center / right** source groups and generates a **more logically careful outlook**

## Why this project exists

The goal is not to tell the user which political side is correct.

The goal is to help the user think more critically by showing:

- where reasoning may break down
- how different outlets frame the same event
- what facts are shared across coverage
- what points remain uncertain or contested
- what a more logically careful synthesis looks like

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

## Setup

Create a virtual environment and install the requirements:

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file from `.env.example`.

```bash
copy .env.example .env
```

or

```bash
cp .env.example .env
```

---

## Required environment variables

```env
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
OPENAI_MODEL=gpt-5.4-mini
MAX_COMPARISON_ARTICLES=6
PER_LEANING_CAP=2
REQUEST_TIMEOUT_SECONDS=25
```

---

## Run the app

```bash
streamlit run app.py
```

---

## What the app returns

For a given article URL, the app returns:

- extracted article metadata
- per-article reasoning audit
- similar article coverage
- left / center / right narrative comparison
- a more logically careful synthesis
- critical questions for the reader

---

## Notes and limitations

1. **Fallacy detection is probabilistic**
   - the app should speak in terms like “possible fallacy” or “likely framing issue”
   - it should not pretend to be a final arbiter of truth

2. **Media leaning labels are editable**
   - the registry in `data/source_registry.csv` is only a starting point
   - change the labels to match your preferred taxonomy

3. **Paywalls can break extraction**
   - some sites will not yield enough body text
   - the app handles this gracefully, but a few sources may still fail

4. **Do not collapse “bias” and “fallacy” into one concept**
   - a source can be slanted without containing a formal fallacy
   - a source can also use clean logic but selective framing

---

## Suggested next upgrades

- add sentence-level text highlighting in the UI
- add article clustering by event
- add fact-check source integration
- add report export to PDF / HTML
- add RAG over saved prior analyses
- add evaluation datasets for calibration

---

## Design philosophy

This app should not say:

> “Here is the true political position.”

It should say:

> “Here are the reasoning patterns, competing frames, and the strongest questions a critical reader should ask.”
