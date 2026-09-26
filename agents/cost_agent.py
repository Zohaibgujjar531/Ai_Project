"""Cost Estimation Agent — produces a preliminary, clearly-labeled cost
breakdown (equipment, software, labor, installation, testing, maintenance,
contingency) using the task plan and project region/currency as context."""

from __future__ import annotations

from utils.llm_client import call_agent, LLMConfig
from utils.prompts import COST_AGENT_SYSTEM, build_cost_prompt


def estimate_cost(
    project_brief: dict,
    requirements: dict,
    tasks: dict,
    config: LLMConfig | None = None,
) -> dict:
    user_prompt = build_cost_prompt(project_brief, requirements, tasks)
    return call_agent(COST_AGENT_SYSTEM, user_prompt, config)
