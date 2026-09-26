"""
Thin wrapper around the Groq API used by every agent.

Centralizing this here means:
- One place to handle missing API keys, network failures, malformed JSON,
  and empty responses.
- Every agent calls `call_agent(...)` and gets back a plain Python dict,
  never a raw string it has to parse itself.
- If anything goes wrong, we raise a single `AgentError` with a short,
  user-friendly message that app.py can show without a stack trace.
"""

from __future__ import annotations

import json
import re
import os
from dataclasses import dataclass
from typing import Optional

try:
    from groq import Groq
except ImportError:  # pragma: no cover - handled gracefully at runtime
    Groq = None

DEFAULT_MODEL = "openai/gpt-oss-120b"


class AgentError(Exception):
    """Raised whenever an agent step fails in a way the UI should explain
    to the user in plain language, instead of crashing."""


@dataclass
class LLMConfig:
    api_key: Optional[str]
    model: str = DEFAULT_MODEL
    temperature: float = 0.4
    max_tokens: int = 4096


def get_config(api_key_override: Optional[str] = None) -> LLMConfig:
    api_key = api_key_override or os.environ.get("GROQ_API_KEY")
    try:
        import streamlit as st  # local import: avoids hard dependency for non-UI use

        if not api_key:
            api_key = st.secrets.get("GROQ_API_KEY", None)
    except Exception:
        pass
    return LLMConfig(api_key=api_key)


def _extract_json(raw_text: str) -> dict:
    """Best-effort extraction of a JSON object from a model response, even
    if it wrapped the JSON in markdown fences or added stray text."""
    if not raw_text or not raw_text.strip():
        raise AgentError("The AI returned an empty response. Please try again.")

    text = raw_text.strip()
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text.strip()).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fall back to grabbing the outermost { ... } block.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise AgentError(
                "The AI's response could not be understood (malformed JSON). "
                "Please try generating the plan again."
            ) from exc

    raise AgentError(
        "The AI's response could not be understood (malformed JSON). "
        "Please try generating the plan again."
    )


def call_agent(
    system_prompt: str,
    user_prompt: str,
    config: Optional[LLMConfig] = None,
) -> dict:
    """Call the Groq chat completion endpoint and return a parsed dict.

    Raises AgentError on any failure — missing key, network issue, API
    error, empty response, or malformed JSON — with a friendly message.
    """
    config = config or get_config()

    if Groq is None:
        raise AgentError(
            "The 'groq' package is not installed. Run: pip install groq"
        )

    if not config.api_key:
        raise AgentError(
            "No Groq API key found. Add GROQ_API_KEY to your environment "
            "or to .streamlit/secrets.toml to enable live AI generation."
        )

    try:
        client = Groq(api_key=config.api_key)
        response = client.chat.completions.create(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:  # network failure, auth error, rate limit, etc.
        # Some models/tiers don't support response_format=json_object — retry
        # once without it rather than failing outright.
        if "response_format" in str(exc).lower():
            try:
                client = Groq(api_key=config.api_key)
                response = client.chat.completions.create(
                    model=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
            except Exception as exc2:
                raise AgentError(f"AI service request failed: {exc2}") from exc2
        else:
            raise AgentError(f"AI service request failed: {exc}") from exc

    try:
        raw_text = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
    except (IndexError, AttributeError) as exc:
        raise AgentError("The AI returned an unexpected response format.") from exc

    if finish_reason == "length":
        raise AgentError(
            "The AI's response was cut off before it finished (output too "
            "long). Try again — this step will retry with room to complete."
        )

    return _extract_json(raw_text)
