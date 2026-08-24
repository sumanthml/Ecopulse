"""
EcoPulse Groq AI Client
Integration with Groq API for environmental intelligence.

Rules:
    - Only used for AI-generated explanations/insights
    - NOT used for AQI calculation, numerical analytics, or basic operations
    - System continues functioning if Groq is unavailable
    - Inputs are compact analytical summaries, not raw data
    - AI outputs are treated as interpretation, not numerical truth
"""
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def get_groq_client():
    """Get or create the Groq client (lazy initialization)."""
    global _client
    if _client is None and settings.has_groq:
        try:
            from groq import Groq
            _client = Groq(api_key=settings.groq_api_key)
            logger.info("Groq client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
    return _client


async def generate_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> Optional[str]:
    """
    Generate a completion using the Groq API.
    
    Returns None if Groq is unavailable (graceful degradation).
    """
    client = get_groq_client()
    if client is None:
        logger.warning("Groq unavailable — skipping AI generation")
        return None

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        logger.info(f"Groq completion generated ({len(content)} chars)")
        return content
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return None


async def check_groq_health() -> dict:
    """Check if Groq API is available."""
    if not settings.has_groq:
        return {"status": "not_configured", "message": "GROQ_API_KEY not set"}
    
    client = get_groq_client()
    if client is None:
        return {"status": "unavailable", "message": "Failed to initialize client"}

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        return {"status": "available", "model": settings.groq_model}
    except Exception as e:
        return {"status": "unavailable", "error": str(e)}
