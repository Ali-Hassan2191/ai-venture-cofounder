# Streamlit Community Cloud Deployment Guide

This guide details how to deploy **AI Venture Co-Founder** directly from GitHub to Streamlit Community Cloud using Python 3.12 and Groq.

---

## Prerequisites

1. A free [GitHub](https://github.com/) account.
2. A free [Streamlit Community Cloud](https://share.streamlit.io/) account connected to GitHub.
3. A [Groq API Key](https://console.groq.com/).

---

## Step 1: Upload Project to GitHub

1. Create a new GitHub repository (e.g. `ai-venture-cofounder`).
2. Push this project to your repository:
   ```bash
   git init
   git add .
   git commit -m "Production release: AI Venture Co-Founder"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/ai-venture-cofounder.git
   git push -u origin main
   ```
*(Note: `.streamlit/secrets.toml` is ignored by `.gitignore` to prevent secret exposure).*

---

## Step 2: Ensure FAISS Index Files Are Committed

Verify that the following vector index files exist in your repository:
```
data/faiss_index/
├── index.faiss
├── config.json
├── metadata.json
└── README.md
```
*(The repository includes starter venture intelligence vector files out-of-the-box).*

---

## Step 3: Deploy to Streamlit Community Cloud

1. Navigate to [share.streamlit.io](https://share.streamlit.io/).
2. Click **Create app** or **New app**.
3. Select **I already have an app**.
4. Configure application details:
   - **Repository:** `<YOUR_USERNAME>/ai-venture-cofounder`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** (Choose your custom subdomain)
5. Expand **Advanced settings**:
   - **Python version:** Select **3.12**.

---

## Step 4: Configure Streamlit Secrets

In the **Advanced settings** modal (or via **App Settings → Secrets** after creation), paste your secrets:

```toml
LLM_PROVIDER = "groq"
LLM_MODEL = "openai/gpt-oss-120b"
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"

# Optional customizations
TEMPERATURE = 0.2
```

Click **Save**.

---

## Step 5: Launch & Verify

1. Click **Deploy!**.
2. Streamlit Cloud will install dependencies from `requirements.txt` on Python 3.12.
3. Once booted, the dark dashboard will load.
4. Navigate to **Startup Idea** to submit a new startup or explore the pre-seeded venture intelligence.
5. In **Settings**, verify that:
   - LLM Provider displays `GROQ`
   - Model displays `openai/gpt-oss-120b`
   - API Key Configured displays `✅ Yes`
   - Vector Index displays `✅ Active`

---

## Important Deployment Notes

- **Zero Local Testing Required:** The application is architected directly for cloud deployment via GitHub and Streamlit Secrets.
- **SQLite Cloud Persistence:** SQLite runs directly on the Streamlit container filesystem. Container restarts will reload initial seed states unless backed up.
- **Token Budget Compliance:** All 6 agents automatically operate within the global 7,500 output token limit.
