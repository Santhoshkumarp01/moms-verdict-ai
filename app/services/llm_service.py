import google.generativeai as genai
from app.utils.logger import get_logger

logger = get_logger(__name__)


def call_llm(prompt: str) -> str:
    """Send a prompt to Gemini and return the raw text response.
    API key and model are read fresh on every call so .env changes
    take effect without restarting the server.

    Args:
        prompt: The full prompt string to send.

    Returns:
        Raw text response from the model.

    Raises:
        RuntimeError: If the API call fails.
    """
    try:
        # Import settings inside the function so the latest .env values are used
        from app.config import settings
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"Calling Gemini API (model: {settings.GEMINI_MODEL})...")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise RuntimeError(f"LLM call failed: {e}") from e
