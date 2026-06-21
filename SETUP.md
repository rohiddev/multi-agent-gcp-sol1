# Setup & Run Guide

---

## Part 1 — Run Locally

### Step 1 — Prerequisites

```bash
# Install Google Cloud CLI (Mac)
brew install google-cloud-sdk
# Other platforms: https://cloud.google.com/sdk/docs/install

# Install Python dependencies
cd multi_agent_gcp_sol1
pip install -r requirements.txt

# Install ADK CLI (if not already included via requirements.txt)
pip install google-adk
```

### Step 2 — Authenticate

```bash
# Application Default Credentials — used by all code in this project
gcloud auth application-default login

# Set your default project
gcloud config set project your-project-id
```

### Step 3 — Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_ENTERPRISE=1        # tells ADK to use Vertex AI, not AI Studio
SUPERVISOR_MODEL=gemini-2.5-flash
RAG_MODEL=gemini-2.5-flash
ACTION_MODEL=gemini-2.5-flash
POLICY_MODEL=gemini-2.5-pro
```

### Step 4 — Run locally (3 options)

**Option A — Web UI (recommended)**

```bash
adk web multi_agent_gcp_sol1/
```

Opens `http://localhost:8000` — interactive chat UI showing agent routing,
tool calls, and traces in real time. Best for development and testing.

**Option B — CLI interactive**

```bash
adk run multi_agent_gcp_sol1/

# Then type your query, for example:
# > What is the company policy on remote access to production?
# > Create a P2 ticket: VPN is broken for the payments team.
```

**Option C — Direct Python**

```bash
python multi_agent_gcp_sol1/main.py
```

---

## Part 2 — Deploy to Gemini Enterprise Agent Platform (Vertex AI Agent Engine)

### Step 1 — Enable required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  logging.googleapis.com \
  cloudtrace.googleapis.com
```

### Step 2 — Create a service account for the agent

```bash
# Create service account
gcloud iam service-accounts create enterprise-agent-sa \
  --display-name="Enterprise Agent Service Account"

# Grant Vertex AI access
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:enterprise-agent-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Step 3 — Deploy via ADK CLI

```bash
adk deploy agent_engine multi_agent_gcp_sol1/ \
  --project your-project-id \
  --region us-central1
```

ADK packages the agent, pushes it to Agent Engine, and returns a resource name.

### Step 4 — Call the deployed agent

```python
import vertexai
from vertexai.preview import reasoning_engines

vertexai.init(project="your-project-id", location="us-central1")

agent = reasoning_engines.ReasoningEngine(
    "projects/.../locations/.../reasoningEngines/..."
)

response = agent.query(input="What is the company policy on remote access?")
print(response)
```

---

## Quick Reference

| Task | Command |
|---|---|
| Authenticate locally | `gcloud auth application-default login` |
| Run web UI | `adk web multi_agent_gcp_sol1/` |
| Run CLI | `adk run multi_agent_gcp_sol1/` |
| Run Python directly | `python multi_agent_gcp_sol1/main.py` |
| Deploy to Agent Engine | `adk deploy agent_engine multi_agent_gcp_sol1/ --project ... --region ...` |
| View traces | GCP Console → Cloud Trace |
| View logs | GCP Console → Cloud Logging → filter by `app.name="enterprise-multi-agent"` |

---

## Switching Retrieval Backend

Set `RETRIEVAL_BACKEND` in `.env` before running:

| Value | Backend |
|---|---|
| `agent_search` | Agent Search — fastest time-to-value (default) |
| `rag_engine` | RAG Engine — managed production RAG |
| `vector_search` | Vector Search — custom chunking and ranking |

Replace stub implementations in `retrieval/retrieval.py` with real API calls when ready.

---

## Troubleshooting

**Auth error on startup**
```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project your-project-id
```

**Model not found**
Ensure `GOOGLE_GENAI_USE_ENTERPRISE=1` is set and the model is available in your region.

**`adk web` not found**
```bash
pip install google-adk --upgrade
```
