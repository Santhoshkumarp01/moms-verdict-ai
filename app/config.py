import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project root (works regardless of cwd)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "5"))
    MAX_RETRIES: int = 1

    def validate(self):
        if not self.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Create a .env file in the project root with:\n"
                "  GEMINI_API_KEY=your_key_here"
            )


settings = Settings()
settings.validate()
