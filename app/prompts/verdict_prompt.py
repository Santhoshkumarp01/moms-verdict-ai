VERDICT_PROMPT = """You are a product review analyst. Analyze the following product reviews and return a structured JSON verdict.

REVIEWS:
{reviews}

INSTRUCTIONS:
- Be factual. Only use information present in the reviews.
- Do NOT invent pros, cons, or opinions not mentioned.
- If the reviews are too vague, noisy, or insufficient, set confidence below 0.5 and explain in uncertainty_reason.
- If you genuinely cannot determine something, say so in uncertainty_reason.
- sentiment_score must be a float between -1.0 (very negative) and 1.0 (very positive).
- confidence must be a float between 0.0 and 1.0.
- pros and cons must each be a list of short, clear strings.
- summary_en must be in English. summary_ar must be in Arabic.
- Return ONLY valid JSON. No markdown, no explanation, no code fences.

REQUIRED JSON FORMAT:
{{
  "summary_en": "...",
  "summary_ar": "...",
  "pros": ["...", "..."],
  "cons": ["...", "..."],
  "sentiment_score": 0.0,
  "confidence": 0.0,
  "uncertainty_reason": "..."
}}
"""


def build_prompt(reviews: list[str]) -> str:
    """Inject reviews into the verdict prompt."""
    formatted = "\n".join(f"- {r}" for r in reviews)
    return VERDICT_PROMPT.format(reviews=formatted)
