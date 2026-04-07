"""Shared OpenAI LLM client with retry, timeout, and JSON parsing."""

from __future__ import annotations

import json
import logging
import time
from typing import cast

from openai import OpenAI, OpenAIError

from services.shared.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
LLM_AVAILABLE: bool = bool(settings.openai_api_key)


def get_llm_client() -> OpenAI:
    """Return a configured OpenAI client."""
    return OpenAI(api_key=settings.openai_api_key)


def llm_json_call(
    prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 400,
) -> dict[str, object]:
    """Call the LLM and return parsed JSON dict.

    Retries once on failure. Raises on second failure.
    """
    logger.debug("llm_json_call prompt=%s", prompt[:200])

    client = get_llm_client()
    last_exc: Exception | None = None

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30,
            )
            content = response.choices[0].message.content or "{}"
            logger.debug("llm_json_call response=%s", content[:500])
            return cast(dict[str, object], json.loads(content))
        except (OpenAIError, json.JSONDecodeError, Exception) as exc:
            last_exc = exc
            logger.warning("llm_json_call attempt %d failed: %s", attempt + 1, exc)
            if attempt == 0:
                time.sleep(1)

    raise RuntimeError(f"llm_json_call failed after 2 attempts: {last_exc}") from last_exc
