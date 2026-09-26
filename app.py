"""
AI Project Manager Agent — Streamlit app.

A multi-agent system that turns a natural-language project idea into a
structured, actionable project plan. The Project Manager Agent orchestrates
five specialized agents (Requirement, Planning, Cost, Risk, Timeline), each
one consuming the previous agents' output as context, and the results are
rendered as a professional project dashboard.

Run with:
    streamlit run app.py

Requires a Groq API key (GROQ_API_KEY env var or .streamlit/secrets.toml).
Without one, the app still runs fully in Demo Mode using a bundled example.
"""

from __future__ import annotations

import time
from datetime import datetime

import streamlit as st

from agents import project_manager, requirement_agent, planning_agent, cost_agent, risk_agent, timeline_agent
from utils import demo_data
from utils.llm_client import AgentError, get_config
from utils.formatting import format_currency, tasks_to_dataframe, cost_to_dataframe, risks_to_dataframe
from utils.visualization import (
    render_agent_pipeline_html,
    build_gantt_chart,
    build_cost_pie_chart,
    build_risk_matrix,
)

# --------------------------------------------------------------------------
# Page config + global styling
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Project Manager",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
:root {
    --bg-navy: #0b1220;
    --panel: #111c33;
    --panel-border: rgba(148,163,184,0.14);
    --cyan: #22d3ee;
    --text-main: #e2e8f0;
    --text-dim: #94a3b8;
}
.stApp {
    background: radial-gradient(1200px 600px at 10% -10%, #0f2138 0%, var(--bg-navy) 55%);
}
section[data-testid="stSidebar"] {
    background: #0a0f1c;
    border-right: 1px solid var(--panel-border);
}
h1, h2, h3, h4 { color: var(--text-main) !important; letter-spacing: -0.01em; }
p, li, span, label { color: var(--text-main); }
.hero {
    padding: 28px 32px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(34,211,238,0.10), rgba(59,130,246,0.06));
    border: 1px solid var(--panel-border);
    margin-bottom: 22px;
}
.hero h1 { font-size: 2rem; margin-bottom: 4px; }
.hero p { color: var(--text-dim); font-size: 1rem; margin: 0; }
.card {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 16px;
    padding: 18px 20px;
    text-align: center;
}
.card .metric-value { font-size: 1.6rem; font-weight: 700; color: var(--cyan); }
.card .metric-label { color: var(--text-dim); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; }
.section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 28px;
    margin-bottom: 6px;
}
.section-title .badge {
    background: rgba(34,211,238,0.14);
    color: var(--cyan);
    font-size: 0.72rem;
    padding: 3px 9px;
    border-radius: 999px;
    font-weight: 600;
}
.assumption-pill {
    display: inline-block;
    background: rgba(245,158,11,0.12);
    color: #fbbf24;
    border: 1px solid rgba(245,158,11,0.25);
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.82rem;
    margin: 3px 6px 3px 0;
}
.reco-card {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-left: 3px solid var(--cyan);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.reco-card .reco-title { font-weight: 600; color: var(--text-main); }
.reco-card .reco-reason { color: var(--text-dim); font-size: 0.88rem; margin-top: 2px; }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
.stButton > button {
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
}
.stButton > button:hover { opacity: 0.9; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []  # list of {"idea": str, "timestamp": str, "result": dict}
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "api_key_override" not in st.session_state:
    st.session_state.api_key_override = ""

AGENT_KEYS = ["pm", "req", "plan", "cost", "risk", "timeline", "final"]


def reset_pipeline_status():
    return {k: "waiting" for k in AGENT_KEYS}


# --------------------------------------------------------------------------
# Sidebar navigation
# --------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🧠 AI Project Manager")
    st.caption("Agentic AI project planning")
    page = st.radio(
        "Navigate",
        ["New Project", "Project History", "Settings", "About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    config = get_config(st.session_state.api_key_override or None)
    if config.api_key:
        st.success("Groq API key detected", icon="🔑")
    else:
        st.warning("No API key — Demo Mode only", icon="⚠️")
    st.caption(f"Model: `{config.model}`")

# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def run_pipeline(project_idea: str, status_placeholder, config):
    """Runs every agent in sequence, updating the live pipeline visual as it
    goes. Returns the assembled result dict, or raises AgentError."""
    statuses = reset_pipeline_status()

    def render(current_key=None, state="processing"):
        s = dict(statuses)
        if current_key:
            s[current_key] = state
        status_placeholder.markdown(render_agent_pipeline_html(s), unsafe_allow_html=True)

    # 1. Project Manager — brief
    render("pm", "processing")
    brief = project_manager.create_brief(project_idea, config)
    statuses["pm"] = "completed"
    render()

    # 2. Requirement Agent
    render("req", "processing")
    requirements = requirement_agent.analyze_requirements(brief, config)
    statuses["req"] = "completed"
    render()

    # 3. Planning Agent
    render("plan", "processing")
    tasks = planning_agent.build_task_plan(brief, requirements, config)
    statuses["plan"] = "completed"
    render()

    # 4. Cost Estimation Agent
    render("cost", "processing")
    cost = cost_agent.estimate_cost(brief, requirements, tasks, config)
    statuses["cost"] = "completed"
    render()

    # 5. Risk Agent
    render("risk", "processing")
    risks = risk_agent.analyze_risks(brief, requirements, tasks, cost, config)
    statuses["risk"] = "completed"
    render()

    # 6. Timeline Agent
    render("timeline", "processing")
    timeline = timeline_agent.build_timeline(tasks, config)
    statuses["timeline"] = "completed"
    render()

    # 7. Final synthesis by the Project Manager Agent
    render("final", "processing")
    full_context = {
        "brief": brief,
        "requirements": requirements,
        "tasks": tasks,
        "cost": cost,
        "risks": risks,
        "timeline": timeline,
    }
    final_summary = project_manager.write_final_summary(full_context, config)
    statuses["final"] = "completed"
    render()

    resources = _derive_resources(requirements, tasks)

    return {
        "brief": brief,
        "requirements": requirements,
        "tasks": tasks,
        "cost": cost,
        "risks": risks,
        "timeline": timeline,
        "final_summary": final_summary,
        "resources": resources,
    }


def _derive_resources(requirements: dict, tasks: dict) -> dict:
    """Builds the 'Required Resources' section from the task list's resource
    tags plus the requirement agent's hardware/software list, split into the
    six categories the dashboard displays."""
    human = sorted({r for t in tasks.get("tasks", []) for r in t.get("resources", [])})
    hw_sw = requirements.get("hardware_software_requirements", [])
    hardware = [x for x in hw_sw if not any(k in x.lower() for k in ["software", "app", "dashboard", "monitoring"])]
    software = [x for x in hw_sw if any(k in x.lower() for k in ["software", "app", "dashboard", "monitoring"])]
    return {
        "human_resources": human,
        "hardware": hardware,
        "software": software,
        "materials": [],
        "tools": [],
        "external_services": [],
    }


def load_demo_result() -> dict:
    return {
        "brief": demo_data.DEMO_BRIEF,
        "requirements": demo_data.DEMO_REQUIREMENTS,
        "tasks": demo_data.DEMO_TASKS,
        "cost": demo_data.DEMO_COST,
        "risks": demo_data.DEMO_RISKS,
        "timeline": demo_data.DEMO_TIMELINE,
        "final_summary": demo_data.DEMO_FINAL_SUMMARY,
        "resources": demo_data.DEMO_RESOURCES,
    }


# --------------------------------------------------------------------------
# Dashboard rendering
# --------------------------------------------------------------------------


def render_dashboard(result: dict):
    brief = result["brief"]
    requirements = result["requirements"]
    tasks = result["tasks"].get("tasks", [])
    cost = result["cost"]
    risks = result["risks"].get("risks", [])
    timeline = result["timeline"]
    resources = result["resources"]
    final_summary = result["final_summary"]
    currency = cost.get("currency", brief.get("currency", "USD"))

    # ---- Summary cards ----
    st.markdown('<div class="section-title"><h3>📊 Project Dashboard</h3></div>', unsafe_allow_html=True)
    cols = st.columns(6)
    card_data = [
        ("Project Tasks", len(tasks)),
        ("Duration", f"{timeline.get('total_duration_days', '—')} Days"),
        ("Est. Cost", format_currency(cost.get("total_estimated_cost", 0), currency)),
        ("Resources", sum(len(v) for v in resources.values())),
        ("Risks Identified", len(risks)),
        ("Milestones", len(timeline.get("milestones", []))),
    ]
    for col, (label, value) in zip(cols, card_data):
        with col:
            st.markdown(
                f'<div class="card"><div class="metric-value">{value}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    # ---- Overview ----
    st.markdown('<div class="section-title"><h3>🗂️ Project Overview</h3></div>', unsafe_allow_html=True)
    o1, o2 = st.columns([2, 1])
    with o1:
        st.markdown(f"**{brief.get('project_name', 'Untitled Project')}**")
        st.write(brief.get("description", ""))
        st.caption(f"Objective: {brief.get('objective', '—')}")
    with o2:
        st.metric("Complexity", brief.get("complexity", "—"))
        st.caption(f"Type: {brief.get('project_type', '—')}")
        st.caption(f"Region: {brief.get('region', '—')}")
    if brief.get("key_assumptions"):
        st.markdown("**Key assumptions:**")
        st.markdown(
            "".join(f'<span class="assumption-pill">⚠ {a}</span>' for a in brief["key_assumptions"]),
            unsafe_allow_html=True,
        )

    # ---- Requirements ----
    st.markdown('<div class="section-title"><h3>📋 Requirements</h3></div>', unsafe_allow_html=True)
    with st.expander("Functional, Technical & Resource Requirements", expanded=False):
        r1, r2 = st.columns(2)
        with r1:
            st.markdown("**Functional Requirements**")
            for x in requirements.get("functional_requirements", []):
                st.markdown(f"- {x}")
            st.markdown("**User Requirements**")
            for x in requirements.get("user_requirements", []):
                st.markdown(f"- {x}")
        with r2:
            st.markdown("**Technical Requirements**")
            for x in requirements.get("technical_requirements", []):
                st.markdown(f"- {x}")
            st.markdown("**Hardware / Software**")
            for x in requirements.get("hardware_software_requirements", []):
                st.markdown(f"- {x}")
        if requirements.get("missing_information"):
            st.info("**Flagged missing information:** " + "; ".join(requirements["missing_information"]))

    # ---- Tasks ----
    st.markdown('<div class="section-title"><h3>✅ Project Tasks</h3></div>', unsafe_allow_html=True)
    st.dataframe(tasks_to_dataframe(tasks), use_container_width=True, hide_index=True)

    # ---- Timeline ----
    st.markdown('<div class="section-title"><h3>📅 Timeline</h3></div>', unsafe_allow_html=True)
    t1, t2 = st.columns([2, 1])
    with t1:
        fig = build_gantt_chart(timeline.get("phases", []))
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        st.markdown("**Milestones**")
        for m in timeline.get("milestones", []):
            st.markdown(f"- Day {m.get('day', '?')}: {m.get('milestone', '')}")

    # ---- Cost ----
    st.markdown('<div class="section-title"><h3>💰 Estimated Cost</h3></div>', unsafe_allow_html=True)
    st.caption("Preliminary, AI-generated estimate — not a market quotation.")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.dataframe(cost_to_dataframe(cost.get("line_items", [])), use_container_width=True, hide_index=True)
        st.markdown(
            f"**Subtotal:** {format_currency(cost.get('subtotal', 0), currency)}  \n"
            f"**Contingency:** {cost.get('contingency_percent', 0)}%  \n"
            f"### Total: {format_currency(cost.get('total_estimated_cost', 0), currency)}"
        )
    with c2:
        st.plotly_chart(build_cost_pie_chart(cost.get("line_items", []), currency), use_container_width=True)
    if cost.get("notes"):
        st.caption(cost["notes"])

    # ---- Risk ----
    st.markdown('<div class="section-title"><h3>⚠️ Risk Analysis</h3></div>', unsafe_allow_html=True)
    k1, k2 = st.columns([1, 1])
    with k1:
        st.dataframe(risks_to_dataframe(risks), use_container_width=True, hide_index=True)
    with k2:
        st.plotly_chart(build_risk_matrix(risks), use_container_width=True)

    # ---- Resources ----
    st.markdown('<div class="section-title"><h3>🧰 Required Resources</h3></div>', unsafe_allow_html=True)
    res_cols = st.columns(3)
    res_labels = [
        ("human_resources", "👥 Human Resources"),
        ("hardware", "🔧 Hardware"),
        ("software", "💻 Software"),
        ("materials", "📦 Materials"),
        ("tools", "🛠️ Tools"),
        ("external_services", "🤝 External Services"),
    ]
    for i, (key, label) in enumerate(res_labels):
        with res_cols[i % 3]:
            st.markdown(f"**{label}**")
            items = resources.get(key, [])
            if items:
                for it in items:
                    st.markdown(f"- {it}")
            else:
                st.caption("None identified")

    # ---- Recommendations ----
    st.markdown('<div class="section-title"><h3>💡 Recommendations</h3></div>', unsafe_allow_html=True)
    st.markdown(f"**Executive summary:** {final_summary.get('executive_summary', '')}")
    st.markdown(f"**Feasibility verdict:** {final_summary.get('feasibility_verdict', '')}")
    for reco in final_summary.get("recommendations", []):
        st.markdown(
            f'<div class="reco-card"><div class="reco-title">✓ {reco.get("recommendation","")}</div>'
            f'<div class="reco-reason">{reco.get("reason","")}</div></div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

if page == "New Project":
    st.markdown(
        """
        <div class="hero">
            <h1>AI Project Manager</h1>
            <p>Transform your project idea into a complete execution plan — powered by a multi-agent AI workflow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🔎 How It Works (multi-agent workflow)", expanded=False):
        st.markdown(
            """
            **User Idea** → **AI Understanding** → **Requirement Analysis** → **Task Planning**
            → **Cost Estimation** → **Risk Analysis** → **Timeline Generation** → **Final Project Plan**

            Each specialized agent consumes the previous agents' output as context — this is
            genuine agent orchestration, not a single prompt pretending to be several agents.
            The **Project Manager Agent** opens the workflow by turning your idea into a shared
            brief, and closes it by synthesizing every agent's output into concrete recommendations.
            """
        )

    idea = st.text_area(
        "Describe your project idea…",
        placeholder="e.g. Build a 10 kW solar-powered irrigation system for a small farm.",
        height=100,
    )

    b1, b2 = st.columns([1, 1])
    generate_clicked = b1.button("🚀 Generate Project Plan", use_container_width=True)
    demo_clicked = b2.button("🎬 Load Demo Project", use_container_width=True)

    if generate_clicked:
        if not idea or not idea.strip():
            st.error("Please describe your project idea first.")
        else:
            status_placeholder = st.empty()
            status_placeholder.markdown(render_agent_pipeline_html(reset_pipeline_status()), unsafe_allow_html=True)
            try:
                with st.spinner("Agents are collaborating on your project plan…"):
                    result = run_pipeline(idea.strip(), status_placeholder, config)
                st.session_state.current_result = result
                st.session_state.history.append(
                    {
                        "idea": idea.strip(),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "result": result,
                    }
                )
                st.success("Project plan generated successfully!")
            except AgentError as e:
                st.error(f"⚠️ {e}")
                st.info("You can load the demo project below to explore the dashboard instead.")
            except Exception as e:  # noqa: BLE001 - final safety net, never crash the app
                st.error(f"⚠️ Something went wrong while generating the plan: {e}")

    if demo_clicked:
        st.session_state.current_result = load_demo_result()
        st.session_state.history.append(
            {
                "idea": demo_data.DEMO_PROJECT_IDEA,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "result": st.session_state.current_result,
            }
        )
        st.info("Loaded the demo project: solar-powered irrigation for a 5-acre farm.")

    if st.session_state.current_result:
        st.markdown("---")
        render_dashboard(st.session_state.current_result)

elif page == "Project History":
    st.markdown("## 🕘 Project History")
    if not st.session_state.history:
        st.caption("No projects generated yet in this session.")
    else:
        for i, entry in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - i
            with st.expander(f"#{idx} · {entry['timestamp']} — {entry['idea'][:70]}"):
                if st.button("View this plan", key=f"view_{idx}"):
                    st.session_state.current_result = entry["result"]
                    st.rerun()

elif page == "Settings":
    st.markdown("## ⚙️ Settings")
    st.text_input(
        "Groq API Key (overrides environment/secrets for this session)",
        type="password",
        key="api_key_override",
        help="Leave blank to use GROQ_API_KEY from the environment or .streamlit/secrets.toml.",
    )
    st.caption(
        "Your key is only kept in this browser session's memory — it is never written to disk "
        "by this app."
    )
    if st.button("Clear project history"):
        st.session_state.history = []
        st.session_state.current_result = None
        st.success("History cleared.")

else:  # About
    st.markdown("## ℹ️ About")
    st.markdown(
        """
        **AI Project Manager Agent** is a multi-agent Agentic AI application built with
        Streamlit and the Groq API.

        A single **Project Manager Agent** orchestrates five specialized agents —
        **Requirement**, **Planning**, **Cost Estimation**, **Risk**, and **Timeline** —
        each one passing its output forward as context for the next, ending with the
        Project Manager Agent synthesizing everything into an executive summary and
        practical recommendations.

        Built with: Python · Streamlit · Groq API · Pandas · Plotly

        This project is designed to be simple enough to explain in a hackathon
        presentation while remaining modular and easy to extend with additional agents.
        """
    )
