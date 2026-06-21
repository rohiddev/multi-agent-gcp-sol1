# Multi-Agent Enterprise Template — Google ADK + Gemini Enterprise Agent Platform

Enterprise-ready multi-agent template. Easy to understand, extend, and deploy to production.

**Author:** Rohid Dev · github.com/rohiddev

---

## Architecture

```
User Request
    ↓
SupervisorAgent         — routes to the right specialist
    ├── RAGAgent        — retrieves from enterprise knowledge
    ├── ActionAgent     — executes against enterprise systems
    └── PolicyAgent     — governs access and risk

Retrieval Layer
    ├── Agent Search    — Google-quality, out-of-the-box RAG
    ├── RAG Engine      — managed production RAG orchestration
    └── Vector Search   — custom retrieval, full design control

Observability
    ├── Cloud Trace + OpenTelemetry — distributed tracing
    └── Cloud Logging               — structured execution logs

Security
    ├── Application Default Credentials + service accounts
    ├── VPC Service Controls (perimeter)
    └── CMEK (encryption)
```

---

## Quickstart

```bash
# 1. Install dependencies (Python 3.11+ required)
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — at minimum set GOOGLE_CLOUD_PROJECT

# 3. Authenticate
gcloud auth application-default login

# 4. Run
python main.py
```

---

## Folder Structure

```
multi_agent_gcp_sol1/
├── main.py                      # Entry point — startup validation, wires everything together
├── agent.py                     # ADK CLI entry point (adk run / adk web)
├── config.py                    # Centralized config with fail-fast validation
├── requirements.txt
├── pyproject.toml               # Python version pin (>=3.11), dev dependencies
├── .env.example
├── agents/
│   ├── supervisor.py            # Supervisor — routes to specialist agents
│   ├── rag_agent.py             # RAG agent — enterprise knowledge retrieval
│   ├── action_agent.py          # Action agent — tickets, APIs, system records
│   └── policy_agent.py          # Policy agent — access control, governance
├── retrieval/
│   └── retrieval.py             # Abstraction: Agent Search | RAG Engine | Vector Search
├── tools/
│   └── enterprise_tools.py      # All tool definitions — error-handled, consistent return schema
├── observability/
│   └── telemetry.py             # Idempotent Cloud Trace + Cloud Logging via OpenTelemetry
└── security/
    └── iam.py                   # IAM credential validation, called at startup
```

---

## Switching Retrieval Backend

Set `RETRIEVAL_BACKEND` in `.env`:

| Value | Backend |
|---|---|
| `agent_search` | Agent Search — fastest time-to-value (default) |
| `rag_engine` | RAG Engine — managed production RAG |
| `vector_search` | Vector Search — custom chunking and ranking |

Replace the stub implementations in `retrieval/retrieval.py` with real API calls.
An invalid value will raise an `EnvironmentError` at startup.

---

## Adding a New Agent

1. Create `agents/my_agent.py` following the pattern in `rag_agent.py`
2. Add your tools to `tools/enterprise_tools.py` — follow the error-handling convention
3. Export your tool from `tools/__init__.py`
4. Import and add to `supervisor.py` `sub_agents=` list
5. Update supervisor instructions to describe when to route to it

---

## Tool Error Handling Convention

All tools return a dict with a `"status"` key:

```python
# Success
{"status": "success", ...}

# Failure — never raises, always returns structured error
{"status": "error", "message": "..."}
```

Agents check `status` before proceeding. This prevents a single tool failure from crashing the session.

---

## Phased Rollout

| Phase | What to build | Risk |
|---|---|---|
| 1 | RAGAgent only — read-only knowledge answers | Low |
| 2 | Add ActionAgent — tickets, lookups | Medium |
| 3 | Add PolicyAgent — govern all actions | Low (adds safety) |
| 4 | Add domain specialists — HR, ops, finance | Medium |

---

## Production Deployment

Deploy to **Agent Runtime** (managed scaling + sessions) or **Cloud Run** / **GKE**.

For Agent Runtime:
```bash
# Package and deploy via Vertex AI SDK
# cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy
```

For Cloud Run:
```bash
gcloud run deploy enterprise-agent \
  --source . \
  --region us-central1 \
  --service-account agent-sa@your-project.iam.gserviceaccount.com
```
