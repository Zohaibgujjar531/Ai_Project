"""Plotly charts and the animated agent-pipeline visual used in app.py."""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.formatting import severity_color

AGENT_PIPELINE = [
    ("pm", "Project Manager Agent"),
    ("req", "Requirement Agent"),
    ("plan", "Planning Agent"),
    ("cost", "Cost Estimation Agent"),
    ("risk", "Risk Agent"),
    ("timeline", "Timeline Agent"),
    ("final", "Final Project Plan"),
]

STATUS_STYLE = {
    "waiting": {"icon": "○", "color": "#64748b", "bg": "rgba(100,116,139,0.12)"},
    "processing": {"icon": "⟳", "color": "#22d3ee", "bg": "rgba(34,211,238,0.15)"},
    "completed": {"icon": "✓", "color": "#34d399", "bg": "rgba(52,211,153,0.15)"},
    "attention": {"icon": "⚠", "color": "#f59e0b", "bg": "rgba(245,158,11,0.15)"},
}


def render_agent_pipeline_html(statuses: dict) -> str:
    """statuses: dict mapping agent key -> 'waiting'|'processing'|'completed'|'attention'"""
    rows = []
    for key, label in AGENT_PIPELINE:
        state = statuses.get(key, "waiting")
        style = STATUS_STYLE[state]
        pulse = "agent-pulse" if state == "processing" else ""
        rows.append(
            f"""
            <div class="agent-row {pulse}">
                <div class="agent-icon" style="color:{style['color']}; background:{style['bg']};">
                    {style['icon']}
                </div>
                <div class="agent-label" style="color:{'#e2e8f0' if state!='waiting' else '#94a3b8'};">
                    {label}
                </div>
            </div>
            """
        )
        if key != AGENT_PIPELINE[-1][0]:
            rows.append('<div class="agent-connector">│</div>')

    return f"""
    <style>
        .agent-pipeline {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 2px;
            padding: 18px 10px;
        }}
        .agent-row {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .agent-icon {{
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: 700;
            flex-shrink: 0;
        }}
        .agent-label {{
            font-size: 15px;
            font-weight: 500;
        }}
        .agent-connector {{
            margin-left: 16px;
            color: #334155;
            font-size: 14px;
            line-height: 8px;
        }}
        .agent-pulse .agent-icon {{
            animation: pulse 1.4s infinite ease-in-out;
        }}
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(34,211,238,0.5); }}
            70% {{ box-shadow: 0 0 0 8px rgba(34,211,238,0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(34,211,238,0); }}
        }}
    </style>
    <div class="agent-pipeline">
        {''.join(rows)}
    </div>
    """


def build_gantt_chart(phases: list[dict], project_start: datetime | None = None):
    project_start = project_start or datetime.today()
    if not phases:
        return go.Figure()

    rows = []
    for ph in phases:
        start = project_start + timedelta(days=ph.get("start_day", 0))
        end = project_start + timedelta(days=max(ph.get("end_day", 1), ph.get("start_day", 0) + 1))
        rows.append(
            {
                "Phase": ph.get("phase", "Phase"),
                "Start": start,
                "Finish": end,
            }
        )
    df = pd.DataFrame(rows)
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Phase",
        color="Phase",
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        height=max(280, 60 * len(rows)),
    )
    return fig


def build_cost_pie_chart(line_items: list[dict], currency: str = "USD"):
    if not line_items:
        return go.Figure()
    df = pd.DataFrame(line_items)
    if "category" not in df or "total_cost" not in df:
        return go.Figure()
    grouped = df.groupby("category", as_index=False)["total_cost"].sum()
    fig = px.pie(
        grouped,
        names="category",
        values="total_cost",
        hole=0.55,
        color_discrete_sequence=px.colors.sequential.Teal,
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        showlegend=False,
        height=320,
    )
    return fig


def build_risk_matrix(risks: list[dict]):
    if not risks:
        return go.Figure()
    level_to_num = {"Low": 1, "Medium": 2, "High": 3}
    xs, ys, texts, colors = [], [], [], []
    for r in risks:
        xs.append(level_to_num.get(r.get("probability", "Medium"), 2))
        ys.append(level_to_num.get(r.get("impact", "Medium"), 2))
        texts.append(r.get("risk", ""))
        colors.append(severity_color(r.get("severity", "Medium")))

    fig = go.Figure(
        data=go.Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            text=texts,
            textposition="top center",
            marker=dict(size=18, color=colors, line=dict(width=1, color="#0f172a")),
        )
    )
    fig.update_layout(
        xaxis=dict(
            tickvals=[1, 2, 3],
            ticktext=["Low", "Medium", "High"],
            title="Probability",
            range=[0.5, 3.5],
            gridcolor="rgba(148,163,184,0.15)",
        ),
        yaxis=dict(
            tickvals=[1, 2, 3],
            ticktext=["Low", "Medium", "High"],
            title="Impact",
            range=[0.5, 3.5],
            gridcolor="rgba(148,163,184,0.15)",
        ),
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="rgba(15,23,42,0.4)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        height=380,
    )
    return fig
