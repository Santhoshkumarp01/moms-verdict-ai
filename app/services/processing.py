import re
from typing import List
from app.config import settings
from app.models.schema import VerdictResponse
from app.prompts.verdict_prompt import build_prompt
from app.services.llm_service import call_llm
from app.services.validation import parse_and_validate
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Patterns that suggest noisy / non-review content
_NOISE_PATTERN = re.compile(r"^[\W\d\s]{0,30}$")


def chunk_reviews(reviews: List[str]) -> List[List[str]]:
    """Split reviews into chunks of MAX_CHUNK_SIZE."""
    size = settings.MAX_CHUNK_SIZE
    return [reviews[i : i + size] for i in range(0, len(reviews), size)]


def deduplicate(items: List[str]) -> List[str]:
    """Remove exact duplicates while preserving order (case-insensitive)."""
    seen = set()
    result = []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


def is_noisy(reviews: List[str]) -> bool:
    """Return True if most reviews look like gibberish or non-review text."""
    noisy_count = sum(1 for r in reviews if _NOISE_PATTERN.match(r.strip()))
    return noisy_count >= max(1, len(reviews) * 0.6)


def adjust_confidence(
    base_confidence: float,
    reviews: List[str],
    sentiment_score: float,
    pros: List[str],
    cons: List[str],
) -> tuple[float, str]:
    """Apply post-LLM confidence adjustments based on input signals.

    Returns:
        (adjusted_confidence, uncertainty_reason)
    """
    reasons = []
    confidence = base_confidence

    # Too few reviews → reduce confidence
    if len(reviews) < 2:
        confidence = min(confidence, 0.45)
        reasons.append("Only one review provided — verdict may not be representative")

    # Noisy input → reduce confidence
    if is_noisy(reviews):
        confidence = min(confidence, 0.35)
        reasons.append("Input appears noisy or non-review content")

    # Conflicting signals: both strong pros and cons → reduce confidence
    if pros and cons and abs(sentiment_score) < 0.3:
        confidence = min(confidence, 0.55)
        reasons.append("Conflicting reviews detected — verdict reflects mixed opinions")

    return round(confidence, 3), "; ".join(reasons)


def analyze_chunk(chunk: List[str]) -> VerdictResponse:
    """Analyze a single chunk of reviews with one retry on failure."""
    prompt = build_prompt(chunk)
    for attempt in range(settings.MAX_RETRIES + 1):
        try:
            raw = call_llm(prompt)
            result = parse_and_validate(raw)

            # Post-process: deduplicate pros/cons
            result.pros = deduplicate(result.pros)
            result.cons = deduplicate(result.cons)

            # Post-process: adjust confidence based on input signals
            adjusted_conf, extra_reason = adjust_confidence(
                result.confidence, chunk, result.sentiment_score, result.pros, result.cons
            )
            result.confidence = adjusted_conf

            # Append any extra uncertainty reasons
            if extra_reason:
                existing = result.uncertainty_reason.strip()
                result.uncertainty_reason = (
                    f"{existing}; {extra_reason}" if existing else extra_reason
                )

            return result

        except ValueError as e:
            if attempt < settings.MAX_RETRIES:
                logger.warning(f"Validation failed (attempt {attempt + 1}), retrying... {e}")
            else:
                raise RuntimeError(f"Failed to get valid response after retries: {e}") from e


def merge_verdicts(verdicts: List[VerdictResponse]) -> VerdictResponse:
    """Merge multiple chunk verdicts into one combined verdict."""
    if len(verdicts) == 1:
        return verdicts[0]

    # Deduplicate across chunks
    all_pros = deduplicate([p for v in verdicts for p in v.pros])
    all_cons = deduplicate([c for v in verdicts for c in v.cons])
    avg_sentiment = sum(v.sentiment_score for v in verdicts) / len(verdicts)
    avg_confidence = sum(v.confidence for v in verdicts) / len(verdicts)
    uncertainty = "; ".join(v.uncertainty_reason for v in verdicts if v.uncertainty_reason)

    return VerdictResponse(
        summary_en=verdicts[0].summary_en,
        summary_ar=verdicts[0].summary_ar,
        pros=all_pros,
        cons=all_cons,
        sentiment_score=round(avg_sentiment, 3),
        confidence=round(avg_confidence, 3),
        uncertainty_reason=uncertainty,
    )


def analyze_reviews(reviews: List[str]) -> VerdictResponse:
    """Full pipeline: chunk → analyze → merge."""
    chunks = chunk_reviews(reviews)
    logger.info(f"Processing {len(reviews)} reviews in {len(chunks)} chunk(s)")
    verdicts = [analyze_chunk(chunk) for chunk in chunks]
    return merge_verdicts(verdicts)
