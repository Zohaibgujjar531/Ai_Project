"""Requirement Agent — analyzes the project brief and produces functional,
technical, user and hardware/software requirements, plus assumptions,
dependencies and flagged missing information."""

from __future__ import annotations

from utils.llm_client import call_agent, LLMConfig
from utils.prompts import REQUIREMENT_AGENT_SYSTEM, build_requirement_prompt


def analyze_requirements(project_brief: dict, config: LLMConfig | None = None) -> dict:
    user_prompt = build_requirement_prompt(project_brief)
    return call_agent(REQUIREMENT_AGENT_SYSTEM, user_prompt, config)
