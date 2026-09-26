"""Small formatting helpers shared across the dashboard."""

from __future__ import annotations

import pandas as pd

STATUS_ICONS = {
    "waiting": "○",
    "processing": "⟳",
    "completed": "✓",
    "attention": "⚠",
}


def format_currency(value: float, currency: str = "USD") -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)

    symbols = {"USD": "$", "PKR": "PKR ", "EUR": "€", "GBP": "£", "INR": "₹"}
    prefix = symbols.get(currency.upper(), f"{currency.upper()} ")

    if value >= 1_000_000:
        return f"{prefix}{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{prefix}{value / 1_000:.1f}K"
    return f"{prefix}{value:,.0f}"


def tasks_to_dataframe(tasks: list[dict]) -> pd.DataFrame:
    if not tasks:
        return pd.DataFrame(
            columns=["ID", "Task", "Description", "Priority", "Dependencies", "Status"]
        )
    rows = []
    for t in tasks:
        rows.append(
            {
                "ID": t.get("id", ""),
                "Task": t.get("name", ""),
                "Description": t.get("description", ""),
                "Priority": t.get("priority", ""),
                "Dependencies": ", ".join(t.get("dependencies", []) or []) or "—",
                "Duration (days)": t.get("duration_days", ""),
                "Status": "Planned",
            }
        )
    return pd.DataFrame(rows)


def cost_to_dataframe(line_items: list[dict]) -> pd.DataFrame:
    if not line_items:
        return pd.DataFrame(
            columns=["Item", "Category", "Quantity", "Unit Cost", "Total Cost"]
        )
    rows = []
    for li in line_items:
        rows.append(
            {
                "Item": li.get("item", ""),
                "Category": li.get("category", ""),
                "Quantity": li.get("quantity", ""),
                "Unit Cost": li.get("unit_cost", 0),
                "Total Cost": li.get("total_cost", 0),
            }
        )
    return pd.DataFrame(rows)


def risks_to_dataframe(risks: list[dict]) -> pd.DataFrame:
    if not risks:
        return pd.DataFrame(
            columns=["Risk", "Probability", "Impact", "Severity", "Mitigation"]
        )
    rows = []
    for r in risks:
        rows.append(
            {
                "Risk": r.get("risk", ""),
                "Probability": r.get("probability", ""),
                "Impact": r.get("impact", ""),
                "Severity": r.get("severity", ""),
                "Mitigation": r.get("mitigation", ""),
            }
        )
    return pd.DataFrame(rows)


def severity_color(level: str) -> str:
    return {
        "Low": "#22c55e",
        "Medium": "#f59e0b",
        "High": "#ef4444",
    }.get(level, "#64748b")
