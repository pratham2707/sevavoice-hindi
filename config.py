"""
Configuration for sevavoice-hindi.
Loads all secrets from .env (kept strictly on the server).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    # --- Agora Conversational AI ---
    # AGORA_APP_ID and AGORA_APP_CERTIFICATE are used for RTC token generation.
    # AGORA_CUSTOMER_ID and AGORA_CUSTOMER_SECRET are reserved for future Agora
    # REST API use and are optional — the agentic workflow and TTS work without them.
    AGORA_APP_ID: str = os.getenv("AGORA_APP_ID", "")
    AGORA_APP_CERTIFICATE: str = os.getenv("AGORA_APP_CERTIFICATE", "")
    AGORA_CUSTOMER_ID: str = os.getenv("AGORA_CUSTOMER_ID", "")
    AGORA_CUSTOMER_SECRET: str = os.getenv("AGORA_CUSTOMER_SECRET", "")
    AGORA_CHANNEL_NAME: str = os.getenv("AGORA_CHANNEL_NAME", "sevavoice-hindi-demo")

    # --- Murf AI (Falcon TTS) ---
    MURF_API_KEY: str = os.getenv("MURF_API_KEY", "")
    MURF_MODEL: str = os.getenv("MURF_MODEL", "falcon")
    MURF_VOICE_ID: str = os.getenv("MURF_VOICE_ID", "hi-IN-female-1")  # Hindi voice
    MURF_LOCALE: str = os.getenv("MURF_LOCALE", "hi-IN")

    # --- App ---
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LANGUAGE: str = os.getenv("LANGUAGE", "hi-IN")


settings = Settings()