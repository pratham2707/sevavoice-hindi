"""
Agent orchestration layer: Agora Conversational AI + Murf AI Falcon TTS.
Secrets are read from config (environment variables) and never exposed to the client.
"""

import requests
from typing import Dict, Any, Optional
from config import settings


class AgoraService:
    """Wrapper around Agora Conversational AI session / token management."""

    def __init__(self):
        self.app_id = settings.AGORA_APP_ID
        self.app_certificate = settings.AGORA_APP_CERTIFICATE
        # Reserved for future Agora REST API use; not required for local demo.
        self.customer_id = settings.AGORA_CUSTOMER_ID
        self.customer_secret = settings.AGORA_CUSTOMER_SECRET

    def generate_rtc_token(self, channel_name: str, user_id: str) -> Optional[str]:
        """
        Generate an Agora RTC token.
        In production, use the official Agora token server / SDK.
        """
        if not self.app_id or not self.app_certificate:
            return None  # dev mode: token not required
        # TODO: Implement actual Agora token generation (HMAC/SHA256) here.
        return "dev-token-placeholder"

    def start_conversation_session(self, channel_name: str, user_id: str) -> Dict[str, Any]:
        """Start an Agora conversational AI session."""
        return {
            "status": "started",
            "channel": channel_name,
            "user_id": user_id,
            "token": self.generate_rtc_token(channel_name, user_id),
            "message": "अगोरा वार्तालाप सत्र प्रारंभ किया गया।",
        }

    def stop_conversation_session(self, session_id: str) -> Dict[str, Any]:
        """Stop an Agora conversational AI session."""
        return {
            "status": "stopped",
            "session_id": session_id,
            "message": "अगोरा वार्तालाप सत्र समाप्त किया गया।",
        }


class MurfService:
    """Wrapper around Murf AI Falcon TTS for Hindi speech synthesis."""

    def __init__(self):
        self.api_key = settings.MURF_API_KEY
        self.model = settings.MURF_MODEL
        self.voice_id = settings.MURF_VOICE_ID
        self.locale = settings.MURF_LOCALE
        self.base_url = "https://api.murf.ai/v1/speech/generate"

    def synthesize(self, text: str) -> Optional[bytes]:
        """
        Synthesize Hindi text to speech using Murf Falcon.
        Returns audio bytes or None if no API key is configured.
        """
        if not self.api_key:
            return None  # dev mode: no audio
        try:
            payload = {
                "model": self.model,
                "voiceId": self.voice_id,
                "locale": self.locale,
                "text": text,
            }
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "api-key": self.api_key,
            }
            resp = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:  # noqa: BLE001
            print(f"[Murf TTS error] {exc}")
            return None


class AgentService:
    """Top-level agent orchestration for the Hindi voice agent."""

    def __init__(self):
        self.agora = AgoraService()
        self.murf = MurfService()

    def start_session(self, user_id: str) -> Dict[str, Any]:
        return self.agora.start_conversation_session(settings.AGORA_CHANNEL_NAME, user_id)

    def stop_session(self, session_id: str) -> Dict[str, Any]:
        return self.agora.stop_conversation_session(session_id)

    def speak(self, text: str) -> Optional[bytes]:
        """Convert Hindi text to speech via Murf Falcon."""
        return self.murf.synthesize(text)