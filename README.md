# 👶 Mom's Verdict AI

**Track A — AI Engineering Intern | Mumzworld Take-Home Assessment**

An AI system that synthesizes product reviews into a structured "Mom's Verdict" — bilingual (English + Arabic), grounded in the input, with explicit uncertainty handling and a full evaluation suite.

---

## One-Paragraph Summary

Mom's Verdict AI takes a list of product reviews and returns a structured verdict: a bilingual summary (EN + AR), extracted pros and cons, a sentiment score, a confidence score, and an uncertainty reason. It is built on FastAPI + Google Gemini, uses Pydantic for schema validation, includes a post-LLM confidence adjustment layer, a quality audit utility, a Streamlit demo UI, and a 12-case evaluation suite. The system is designed to say "I don't know" rather than hallucinate — low-quality or noisy input explicitly lowers confidence and populates the uncertainty field.

---

## Setup (under 5 minutes)

```bash
# 1. Enter the project
cd moms-verdict-ai

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your_key_here

# 5. Run the API
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)

# 6. Run the Streamlit UI (separate terminal)
streamlit run ui.py
# → http://localhost:8501
```

**Quick API test:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"reviews": ["Great product!", "Broke after one day."]}'
```

---

## Architecture

```
POST /analyze
     │
     ▼
[main.py] — validates request, strips empty reviews
     │
     ▼
[processing.py] — chunks reviews (default: 5 per chunk)
     │
     ▼
[verdict_prompt.py] — builds structured prompt with anti-hallucination rules
     │
     ▼
[llm_service.py] — calls Google Gemini API
     │
     ▼
[validation.py] — parses JSON, strips code fences, validates Pydantic schema
     │             (retries once on failure)
     ▼
[processing.py] — deduplicates pros/cons, adjusts confidence based on:
     │               • number of reviews
     │               • noise detection
     │               • sentiment conflict
     ▼
[merge_verdicts] — averages scores across chunks if multiple
     │
     ▼
VerdictResponse (Pydantic) → JSON response
```

**Audit layer** (`audit.py`) runs independently in the UI and evaluator to validate output quality without modifying the response.

---

## Features

- **Bilingual output** — summary in English and Arabic, generated natively (not translated)
- **Structured JSON** — validated against a Pydantic schema; failures are explicit
- **Uncertainty handling** — confidence is adjusted post-LLM based on input signals; `uncertainty_reason` is always populated when confidence is low
- **Deduplication** — duplicate pros/cons removed across chunks
- **Retry logic** — one automatic retry on JSON parse or schema failure
- **Evaluation suite** — 12 labeled test cases with pass/fail criteria
- **Quality audit** — 8 structural and semantic checks on every response
- **Streamlit UI** — demo interface with sample inputs, confidence bars, and audit display

---

## API

### `POST /analyze`

**Request:**
```json
{
  "reviews": ["Great product!", "Broke after one day."]
}
```

**Response:**
```json
{
  "summary_en": "Reviews are mixed — praised for quality but criticized for durability.",
  "summary_ar": "الآراء متباينة — أُشيد بالجودة لكن انتُقد المنتج بسبب ضعف المتانة.",
  "pros": ["Good quality"],
  "cons": ["Broke after one day"],
  "sentiment_score": -0.05,
  "confidence": 0.55,
  "uncertainty_reason": "Conflicting reviews detected — verdict reflects mixed opinions"
}
```

**Error cases:**
- `422` — all reviews are empty/whitespace
- `500` — LLM call failed after retries

---

## Evaluation Results

Run with: `python evaluator.py`

| # | Test Case | Expected | Key Check |
|---|-----------|----------|-----------|
| 1 | all_positive | sentiment > 0 | ✅ |
| 2 | all_negative | sentiment < 0 | ✅ |
| 3 | mixed_reviews | both pros & cons | ✅ |
| 4 | empty_input | low confidence | ✅ handled at API layer |
| 5 | noisy_input | low confidence + uncertainty | ✅ |
| 6 | short_input (1 review) | low confidence + uncertainty | ✅ |
| 7 | long_input (12 reviews) | sentiment > 0 | ✅ |
| 8 | conflicting_reviews | both pros & cons | ✅ |
| 9 | duplicate_reviews | deduped pros/cons | ✅ |
| 10 | irrelevant_reviews | low confidence + uncertainty | ✅ |
| 11 | multilingual_input | sentiment > 0 | ✅ |
| 12 | edge_case_unclear | low confidence + uncertainty | ✅ |

**Eval rubric:**
- Sentiment direction matches expectation (positive/negative)
- Low-confidence cases return `confidence < 0.5`
- Uncertain cases return non-empty `uncertainty_reason`
- Mixed/conflicting cases return both pros and cons
- All outputs pass the 8-point structural audit

---

## Tradeoffs

**Why this problem?**
Review synthesis is one of the highest-leverage AI features for an e-commerce platform. Moms reading 200 reviews before buying a stroller is a real friction point. A structured, bilingual verdict directly reduces that friction.

**Why prompt-based, not fine-tuned?**
Fine-tuning requires labeled data and infrastructure that doesn't exist yet. A well-engineered prompt with schema enforcement and post-processing achieves production-quality results in hours, not weeks. Fine-tuning would be the next step once output patterns are stable.

**Why Gemini Flash?**
Fast, cheap, and capable enough for structured extraction. The free tier is sufficient for prototyping and evaluation. Gemini 2.5 Flash is the current stable model on the free tier.

**Why chunking?**
Gemini has context limits and latency increases with input size. Chunking keeps each call focused and allows parallel processing in a future version.

**What was cut:**
- Parallel chunk processing (sequential is simpler and sufficient for ~200 reviews)
- Semantic deduplication (exact match is good enough; embedding-based similarity adds latency)
- Caching (not needed for a prototype)
- Auth on the API (out of scope)

**What's next:**
- Parallel chunk processing with `asyncio`
- Streaming responses for large review sets
- Product category context in the prompt
- A/B testing the prompt against a fine-tuned classifier

---

## Known Failure Cases

| Failure | Behavior |
|---------|----------|
| Gibberish / noisy input | Confidence reduced to ≤0.35, uncertainty_reason populated |
| Single vague review ("ok") | Confidence reduced to ≤0.45, uncertainty_reason populated |
| Conflicting reviews | Confidence capped at 0.55, both pros and cons extracted |
| Irrelevant text (not product reviews) | Low confidence, uncertainty flagged |
| Multi-chunk summary merging | Only first chunk's summary used — approximate for large sets |
| API rate limit | No exponential backoff yet — will surface as 500 error |

---

## Tooling & AI Workflow

| Tool | Role |
|------|------|
| Google Gemini 2.5 Flash | Structured extraction and bilingual generation |
| FastAPI | REST API layer |
| Pydantic v2 | Schema validation and type enforcement |
| Streamlit | Demo UI |
| python-dotenv | Environment variable management |
| Kiro (AI IDE) | Project scaffolding and iterative development |

**How I used them:**
Gemini was prompted with strict JSON format instructions and anti-hallucination rules to produce structured verdicts including summaries, pros/cons, sentiment, and confidence. Prompts were iteratively refined to enforce "I don't know" behavior on uncertain inputs and to generate natural Arabic rather than literal translations. Kiro was used to bootstrap the project structure; validation logic, chunking, confidence adjustment, and the eval rubric were all written and tuned manually.

**What worked:**
Structured prompting significantly improved output reliability. Chunking made 200-review inputs tractable. Adding post-LLM confidence adjustment based on input signals (noise, review count, sentiment conflict) made uncertainty handling trustworthy.

**What didn't work initially:**
Early prompts produced invalid JSON — fixed with stricter format enforcement. Arabic output was initially literal — fixed by explicitly instructing natural language generation. The model was sometimes overconfident on weak inputs — addressed by the confidence adjustment layer.

**Where I intervened:**
Added the validation and retry layer to catch malformed outputs. Designed the 12 eval test cases manually to cover real failure modes. Rewrote the confidence scoring logic after the agent's first version didn't account for sentiment conflict.

---

## Project Structure

```
moms-verdict-ai/
├── app/
│   ├── main.py              # FastAPI app + /analyze endpoint
│   ├── config.py            # Settings from .env with validation
│   ├── models/schema.py     # Pydantic input/output schemas
│   ├── prompts/
│   │   └── verdict_prompt.py  # Prompt template with anti-hallucination rules
│   ├── services/
│   │   ├── llm_service.py   # Gemini API wrapper
│   │   ├── processing.py    # Chunking, confidence adjustment, merging
│   │   └── validation.py    # JSON parse + schema validation with retry
│   └── utils/
│       ├── audit.py         # 8-point quality audit
│       └── logger.py        # Structured logging
├── evals/
│   └── test_cases.py        # 12 labeled test cases
├── data/
│   └── sample_reviews.json  # Sample input data
├── evaluator.py             # Eval runner + report printer
├── ui.py                    # Streamlit demo UI
├── requirements.txt
├── .env.example
└── README.md
```
