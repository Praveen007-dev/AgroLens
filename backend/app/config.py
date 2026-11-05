import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=False)


def get_setting(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def get_cors_origins() -> list[str]:
    configured = get_setting("AGROLENS_CORS_ORIGINS")
    if configured is None:
        return [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5000",
            "http://localhost:7357",
            "http://127.0.0.1:5000",
            "http://127.0.0.1:7357",
        ]
    return [origin.strip() for origin in configured.split(",") if origin.strip()]
