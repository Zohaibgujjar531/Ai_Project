"""Timeline Agent — groups tasks into phases and produces a dependency-aware
schedule (start/end day offsets) plus milestones and total duration."""

from __future__ import annotations

from utils.llm_client import call_agent, LLMConfig
from utils.prompts import TIMELINE_AGENT_SYSTEM, build_timeline_prompt


def build_timeline(tasks: dict, config: LLMConfig | None = None) -> dict:
    user_prompt = build_timeline_prompt(tasks)
    return call_agent(TIMELINE_AGENT_SYSTEM, user_prompt, config)
