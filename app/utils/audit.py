"""
Audit utility to validate AI output quality against expected schema and logic rules.
"""

REQUIRED_FIELDS = [
    "summary_en",
    "summary_ar",
    "pros",
    "cons",
    "sentiment_score",
    "confidence",
    "uncertainty_reason",
]


def audit_response(response: dict, input_reviews: list[str] | None = None) -> dict:
    """Validate a verdict response against quality standards.

    Args:
        response: The parsed JSON dict returned by the /analyze endpoint.
        input_reviews: Optional list of input reviews for context-aware checks.

    Returns:
        dict with keys:
            - valid (bool): True if no issues found.
            - issues (list[str]): Descriptions of any problems detected.
    """
    issues = []

    # 1. Check all required fields are present
    for field in REQUIRED_FIELDS:
        if field not in response:
            issues.append(f"Missing required field: '{field}'")

    # Stop early if structure is broken — remaining checks would error
    if issues:
        return {"valid": False, "issues": issues}

    # 2. sentiment_score must be in [-1.0, 1.0]
    sentiment = response["sentiment_score"]
    if not isinstance(sentiment, (int, float)):
        issues.append("sentiment_score must be a number")
    elif not (-1.0 <= sentiment <= 1.0):
        issues.append(f"sentiment_score out of range [-1, 1]: got {sentiment}")

    # 3. confidence must be in [0.0, 1.0]
    confidence = response["confidence"]
    if not isinstance(confidence, (int, float)):
        issues.append("confidence must be a number")
    elif not (0.0 <= confidence <= 1.0):
        issues.append(f"confidence out of range [0, 1]: got {confidence}")

    # 4. pros and cons must be lists
    if not isinstance(response["pros"], list):
        issues.append("pros must be a list")
    if not isinstance(response["cons"], list):
        issues.append("cons must be a list")

    # 5. If reviews were provided and non-empty, pros+cons should not both be empty
    has_real_input = input_reviews and any(r.strip() for r in input_reviews)
    if has_real_input:
        if isinstance(response["pros"], list) and isinstance(response["cons"], list):
            if len(response["pros"]) == 0 and len(response["cons"]) == 0:
                issues.append("Both pros and cons are empty despite non-empty input — possible hallucination or extraction failure")

    # 6. Summaries must be non-empty strings
    if not isinstance(response["summary_en"], str) or not response["summary_en"].strip():
        issues.append("summary_en is empty or not a string")
    if not isinstance(response["summary_ar"], str) or not response["summary_ar"].strip():
        issues.append("summary_ar is empty or not a string")

    # 7. uncertainty_reason must be a string (can be empty)
    if not isinstance(response["uncertainty_reason"], str):
        issues.append("uncertainty_reason must be a string")

    # 8. Hallucination indicator: empty input but model returned confident non-empty output
    if not has_real_input:
        if isinstance(response["pros"], list) and len(response["pros"]) > 0:
            issues.append("Hallucination risk: pros returned for empty input")
        if isinstance(response["cons"], list) and len(response["cons"]) > 0:
            issues.append("Hallucination risk: cons returned for empty input")
        if isinstance(confidence, (int, float)) and confidence > 0.7:
            issues.append("Hallucination risk: high confidence returned for empty input")

    return {"valid": len(issues) == 0, "issues": issues}
