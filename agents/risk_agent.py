"""Risk Agent — identifies project-specific risks with probability, impact,
severity and a concrete mitigation strategy for each."""

from __future__ import annotations

from utils.llm_client import call_agent, LLMConfig
from utils.prompts import RISK_AGENT_SYSTEM, build_risk_prompt


def analyze_risks(
    project_brief: dict,
    requirements: dict,
    tasks: dict,
    cost: dict,
    config: LLMConfig | None = None,
) -> dict:
    user_prompt = build_risk_prompt(project_brief, requirements, tasks, cost)
    return call_agent(RISK_AGENT_SYSTEM, user_prompt, config)
