# 🧠 AI Project Manager Agent

A multi-agent **Agentic AI** application that turns a natural-language project
idea into a complete, structured project plan — built with **Streamlit** and
the **Groq API**.

> Input one project idea → AI agents analyze it → agents collaborate → a
> structured project plan → a professional interactive dashboard.

---

## ✨ Features

- **Genuine multi-agent orchestration** — six agents each consume the
  previous agents' output as context, coordinated by a Project Manager Agent
  (not one prompt pretending to be several agents).
- **Live agent pipeline visualization** — watch each agent go from
  `○ Waiting` → `⟳ Processing` → `✓ Completed` while the plan is generated.
- **Professional dashboard** — summary cards, requirements, task table,
  Gantt-style timeline, cost breakdown with pie chart, risk matrix, resource
  list, and AI-written recommendations.
- **Demo Mode** — a full bundled example (solar-powered irrigation system)
  so the app is explorable even without an API key.
- **Graceful error handling** — missing API key, network failures, and
  malformed AI responses are all caught and shown as friendly messages
  instead of crashing.

---

## 🧩 Agent Architecture

```
USER PROJECT IDEA
       ↓
Project Manager Agent   (orchestrator: builds shared brief)
       ↓
Requirement Agent       (functional / technical / resource requirements)
       ↓
Planning Agent          (ordered, actionable task breakdown)
       ↓
Cost Estimation Agent   (preliminary cost breakdown)
       ↓
Risk Agent              (risks, severity, mitigation)
       ↓
Timeline Agent          (phases, schedule, milestones)
       ↓
Project Manager Agent   (final synthesis + recommendations)
       ↓
FINAL PROJECT PLAN
```

Each agent lives in its own file under `agents/`, with its own strict JSON
output contract defined in `utils/prompts.py`. `app.py` owns the
orchestration loop and the dashboard rendering.

---

## 📁 Project Structure

```
ai-project-manager/
│
├── app.py                    # Streamlit app: orchestration + dashboard
├── requirements.txt
├── README.md
├── .gitignore
│
├── agents/
│   ├── project_manager.py    # Orchestrator: brief + final synthesis
│   ├── requirement_agent.py
│   ├── planning_agent.py
│   ├── cost_agent.py
│   ├── risk_agent.py
│   └── timeline_agent.py
│
├── utils/
│   ├── prompts.py            # All system/user prompt templates
│   ├── llm_client.py         # Groq API wrapper + JSON parsing + errors
│   ├── formatting.py         # Currency/table formatting helpers
│   ├── visualization.py      # Plotly charts + agent pipeline HTML
│   └── demo_data.py          # Bundled demo project (offline mode)
│
└── assets/
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your Groq API key

Get a free key at [console.groq.com](https://console.groq.com), then either:

**Option A — environment variable**

```bash
export GROQ_API_KEY="your-key-here"
```

**Option B — Streamlit secrets**

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-key-here"
```

You can also paste a key directly into the **Settings** page inside the app
for the current session only.

No key? The app still runs — use **🎬 Load Demo Project** on the New Project
page to explore the full dashboard with bundled example data.

### 3. Run the app

```bash
streamlit run app.py
```

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app
   pointing at `app.py`.
3. In the app's **Secrets** settings, add:
   ```toml
   GROQ_API_KEY = "your-key-here"
   ```
4. Deploy — no other configuration needed.

---

## 🛠️ Extending

- **Add a new agent:** create a file in `agents/`, add its prompt pair to
  `utils/prompts.py`, and call it inside `run_pipeline()` in `app.py`,
  passing in whatever upstream context it needs.
- **Swap the model:** change `DEFAULT_MODEL` in `utils/llm_client.py`.
- **Change the theme:** edit the `CUSTOM_CSS` block at the top of `app.py`.

---

## ⚠️ Disclaimer

Cost estimates produced by this application are preliminary, AI-generated
approximations for planning purposes only — always confirm with vendor
quotations before committing a budget.
