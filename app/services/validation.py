import json
from app.models.schema import VerdictResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_and_validate(raw: str) -> VerdictResponse:
    """Parse raw LLM output and validate against VerdictResponse schema.

    Args:
        raw: Raw string output from the LLM.

    Returns:
        Validated VerdictResponse instance.

    Raises:
        ValueError: If JSON is invalid or schema validation fails.
    """
    # Strip markdown code fences if the model added them anyway
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error: {e}")
        raise ValueError(f"Invalid JSON from LLM: {e}")

    try:
        return VerdictResponse(**data)
    except Exception as e:
        logger.warning(f"Schema validation error: {e}")
        raise ValueError(f"Schema mismatch: {e}")
