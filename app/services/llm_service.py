import google.generativeai as genai
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)


def call_llm(prompt: str) -> str:
    """Send a prompt to Gemini and return the raw text response.

    Args:
        prompt: The full prompt string to send.

    Returns:
        Raw text response from the model.

    Raises:
        RuntimeError: If the API call fails.
    """
    try:
        logger.info("Calling Gemini API...")
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise RuntimeError(f"LLM call failed: {e}") from e
