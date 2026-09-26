"""
Project Manager Agent — the orchestrator.

It does two jobs in this codebase:
1. `create_brief()` — turns the user's raw idea into a structured brief that
   every downstream agent receives as shared context.
2. `write_final_summary()` — after every other agent has run, synthesizes
   their outputs into an executive summary + practical recommendations.

The orchestration LOOP itself (calling each agent in order, passing one
agent's output into the next agent's input, updating live status) lives in
app.py, since that is also where the UI needs to react to each step. This
module only owns the Project Manager's own two LLM calls.
"""

from __future__ import annotations

from utils.llm_client import call_agent, LLMConfig
from utils.prompts import (
    PROJECT_MANAGER_SYSTEM,
    PROJECT_MANAGER_FINAL_SYSTEM,
    build_project_manager_prompt,
    build_final_summary_prompt,
)


def create_brief(project_idea: str, config: LLMConfig | None = None) -> dict:
    """Understand the user's idea and produce the shared project brief that
    the Requirement, Planning, Cost, Risk and Timeline agents will all read."""
    user_prompt = build_project_manager_prompt(project_idea)
    return call_agent(PROJECT_MANAGER_SYSTEM, user_prompt, config)


def write_final_summary(full_context: dict, config: LLMConfig | None = None) -> dict:
    """Combine every agent's output into an executive summary and concrete,
    context-aware recommendations."""
    user_prompt = build_final_summary_prompt(full_context)
    return call_agent(PROJECT_MANAGER_FINAL_SYSTEM, user_prompt, config)
