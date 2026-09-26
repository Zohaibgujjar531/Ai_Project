"""Planning Agent — converts requirements into an ordered, actionable task
breakdown with priorities, dependencies, resources and durations."""

from __future__ import annotations

from utils.llm_client import call_agent, LLMConfig
from utils.prompts import PLANNING_AGENT_SYSTEM, build_planning_prompt


def build_task_plan(
    project_brief: dict, requirements: dict, config: LLMConfig | None = None
) -> dict:
    user_prompt = build_planning_prompt(project_brief, requirements)
    return call_agent(PLANNING_AGENT_SYSTEM, user_prompt, config)
