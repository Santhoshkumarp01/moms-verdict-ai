import os
from pathlib import Path
from dotenv import load_dotenv

# Always resolve .env relative to this file's location (project root)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _load() -> None:
    """Reload .env from disk — called each time settings are accessed."""
    load_dotenv(dotenv_path=_ENV_PATH, override=True)


class Settings:
    @property
    def GEMINI_API_KEY(self) -> str:
        _load()
        return os.getenv("GEMINI_API_KEY", "")

    @property
    def GEMINI_MODEL(self) -> str:
        _load()
        return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    @property
    def MAX_CHUNK_SIZE(self) -> int:
        _load()
        return int(os.getenv("MAX_CHUNK_SIZE", "5"))

    MAX_RETRIES: int = 1

    def validate(self) -> None:
        if not self.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Create a .env file in the project root with:\n"
                "  GEMINI_API_KEY=your_key_here"
            )


settings = Settings()
