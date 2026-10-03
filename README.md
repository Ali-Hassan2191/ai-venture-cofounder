# AI Venture Co-Founder

> **An AI-powered virtual co-founder platform that conducts deep market research, competitive intelligence, financial modeling, Go-To-Market planning, technical architecture, and executive venture assessments.**

---

## 1. Executive Overview

**AI Venture Co-Founder** functions as an autonomous, multi-agent founding board for early-stage entrepreneurs. Rather than providing generic chatbot advice, the platform orchestrates six specialized AI co-founders powered by **CrewAI** and **Groq** (`openai/gpt-oss-120b`). 

Grounded with an Advanced Retrieval-Augmented Generation (**RAG**) pipeline utilizing **FAISS**, the founding team validates consumer demand, identifies competitors' vulnerabilities, models 12-month unit economics, architects software infrastructure, and delivers an authoritative **Startup Blueprint** with a **Dynamic Execution Roadmap**.

---

## 2. Core Capabilities

- **AI Founding Board (6 Specialized Agents):** 
  - *Market Research Strategist:* TAM/SAM/SOM sizing, customer pain points, and local demand signals.
  - *Competitor Intelligence Lead:* Direct/indirect teardowns, pricing analysis, and defensible USP discovery.
  - *Chief Financial Analyst:* Unit economics, runway, break-even targets, and burn modeling using Pandas.
  - *Head of Growth:* Channel acquisition strategy, launch campaigns, viral referral loops, and retention.
  - *Chief Technology Officer:* Modern tech stack, database schemas, core feature scoping, and system safeguards.
  - *Lead Co-Founder (CEO):* Cross-functional venture synthesis, 8-dimensional risk matrix, difficulty rating, and scoring.
- **Dynamic Execution Roadmap:** 
  - Roadmaps are **never hardcoded to 30 days**. Duration dynamically scales (e.g. 15, 21, 30, 45, 60, 90, 120 days) based on technical complexity, capital, and founder experience.
- **Global 7,500 Output Token Manager:**
  - Enforces a centralized, hard workflow limit of 7,500 total output tokens across all six agents combined.
  - Dynamically transfers unused token surplus from earlier agents to deepen the final CEO synthesis.
- **Interactive Dark Dashboard:**
  - Recreates a modern venture studio aesthetic using Streamlit, Plotly charts, and custom CSS.
- **Investor-Ready PDF Dossier:**
  - One-click generation of multi-page PDF blueprints utilizing ReportLab 5.0.
- **Context-Aware Co-Founder Chat:**
  - Ongoing strategic discussions backed by SQLite chat persistence and RAG vector context.

---

## 3. Technology Stack

- **Language:** Python 3.12 (Strict 2026 compatibility)
- **Agent Orchestration:** CrewAI (Version 1.15+)
- **LLM Provider:** Groq
- **Primary Model:** `openai/gpt-oss-120b` (Provider-agnostic centralized abstraction)
- **Vector Retrieval (RAG):** FAISS CPU (`IndexFlatIP` cosine metric)
- **Frontend / UI:** Streamlit & Plotly
- **Data Engineering:** Pandas & NumPy
- **Persistence:** SQLite3 (WAL mode, relational foreign keys)
- **Document Generation:** ReportLab 5.0

---

## 4. System Architecture

```
Streamlit Secrets (.streamlit/secrets.toml)
                  │
                  ▼
   Centralized LLM Configuration (config/llm_config.py)
   & Global Token Budget Manager (7,500 max output tokens)
                  │
                  ▼
           CrewAI LLM Interface
                  │
 ┌────────────────┴────────────────┐
 │     RAG Vector Knowledge        │ (data/faiss_index/)
 │  FAISS Index + Metadata Records │
 └────────────────┬────────────────┘
                  │
                  ▼
       Sequential CrewAI Pipeline
  [Market Research] ──> [Competitor Intelligence]
          │                       │
          ▼                       ▼
    [Finance Model] ───> [Marketing Growth]
          │                       │
          ▼                       ▼
     [CTO Tech]   ───>   [CEO Synthesis]
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
      SQLite Database Persistence       Interactive Streamlit UI
  (Startups, Scores, Dynamic Roadmap)  (Cards, Plotly Gauges, PDF)
```

---

## 5. Repository File Structure

```
ai_venture_cofounder/
├── app.py                      # Main Streamlit application entrypoint
├── requirements.txt            # Production dependencies (Python 3.12 verified)
├── README.md                   # Project documentation
├── DEPLOYMENT.md               # GitHub & Streamlit Community Cloud guide
├── .gitignore                  # Git ignore rules (secrets, caches, local dbs)
│
├── .streamlit/
│   ├── config.toml             # Dark theme and server parameters
│   └── secrets.example.toml    # Secrets template
│
├── agents/                     # The 6 distinct AI co-founders
│   ├── __init__.py
│   ├── market_research_agent.py
│   ├── competitor_analysis_agent.py
│   ├── finance_agent.py
│   ├── marketing_agent.py
│   ├── cto_agent.py
│   └── ceo_agent.py
│
├── tasks/                      # CrewAI task definitions
│   ├── __init__.py
│   ├── market_tasks.py
│   ├── competitor_tasks.py
│   ├── finance_tasks.py
│   ├── marketing_tasks.py
│   ├── cto_tasks.py
│   └── ceo_tasks.py
│
├── crew/                       # CrewAI orchestration pipeline
│   ├── __init__.py
│   └── startup_crew.py
│
├── config/                     # Centralized LLM & Token Budget layer
│   ├── __init__.py
│   └── llm_config.py
│
├── rag/                        # Advanced RAG with FAISS
│   ├── __init__.py
│   ├── document_loader.py
│   ├── retriever.py
│   ├── embeddings.py
│   └── faiss_manager.py
│
├── data/
│   ├── faiss_index/            # Vector assets
│   │   ├── index.faiss
│   │   ├── config.json
│   │   ├── metadata.json
│   │   └── README.md
│   └── venture_cofounder.db    # SQLite runtime database
│
├── database/                   # SQLite schema & repository
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   └── repository.py
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── startup_service.py
│   ├── analysis_service.py
│   ├── roadmap_service.py
│   ├── financial_service.py
│   └── report_service.py
│
├── ui/                         # Streamlit modular views
│   ├── __init__.py
│   ├── styles.py
│   ├── sidebar.py
│   ├── dashboard.py
│   ├── startup_form.py
│   ├── agents_view.py
│   ├── market_view.py
│   ├── competitor_view.py
│   ├── finance_view.py
│   ├── blueprint_view.py
│   ├── execution_view.py
│   ├── progress_view.py
│   ├── chat_view.py
│   └── reports_view.py
│
├── utils/                      # Validation, formatting, and constants
│   ├── __init__.py
│   ├── constants.py
│   ├── formatters.py
│   └── validators.py
│
└── assets/
    └── README.md
```

---

## 6. Streamlit Secrets Configuration

Configure your credentials in `.streamlit/secrets.toml` or directly in Streamlit Cloud Secrets:

```toml
LLM_PROVIDER = "groq"
LLM_MODEL = "openai/gpt-oss-120b"
GROQ_API_KEY = "gsk_your_groq_api_key_here"

# Optional overrides
TEMPERATURE = 0.2
```

---

## 7. Deployment Instructions

Follow `DEPLOYMENT.md` for complete step-by-step instructions:
1. Push this repository to GitHub.
2. Connect your repository to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Set Python version to **3.12**.
4. Set main file to `app.py`.
5. Add your `GROQ_API_KEY` in the App Secrets.
6. Click **Deploy**.

---

## 8. Important Architectural Considerations

- **Global Output Token Allocation:** The six agents strictly share a maximum of 7,500 total output tokens. This ensures rapid response times and eliminates context exhaustion.
- **SQLite Storage on Ephemeral Cloud:** SQLite is isolated and zero-config. On Streamlit Community Cloud, changes persist during active sessions but may reset upon container rebuilds.
- **Modular Provider Swapping:** Switching between Groq, Gemini, or OpenRouter only requires changing `LLM_PROVIDER` and `LLM_MODEL` in Secrets without modifying agent or business logic.
