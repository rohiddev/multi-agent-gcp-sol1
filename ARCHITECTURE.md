# Architecture — Plain English Guide

This document explains how the system works, piece by piece, using simple diagrams.
No technical background needed.

---

## The Big Picture

Think of this system like a **smart helpdesk with specialists**.
You ask a question or make a request. A manager (the Supervisor) reads it,
figures out who is best placed to handle it, and sends it to the right expert.
The expert does the work and sends the answer back.

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                        YOUR APPLICATION                             │
 │                  (web app, chatbot, internal tool)                  │
 └───────────────────────────────┬─────────────────────────────────────┘
                                 │
                        You type a request
                    e.g. "What is the VPN policy?"
                                 │
                                 ▼
 ┌─────────────────────────────────────────────────────────────────────┐
 │                     main.py  —  Entry Point                         │
 │                                                                     │
 │  • Checks you are logged in to Google Cloud (credentials)           │
 │  • Starts up logging and tracing so nothing is invisible            │
 │  • Passes your request into the agent system                        │
 └───────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
```

---

## Layer 1 — The Supervisor (The Manager)

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                      SUPERVISOR AGENT                               │
 │                    agents/supervisor.py                             │
 │                                                                     │
 │  "I read every request and decide who should handle it."            │
 │                                                                     │
 │  ┌─────────────────────────────────────────────────────────────┐    │
 │  │  Routing Rules (plain English)                              │    │
 │  │                                                             │    │
 │  │  Is the user asking a QUESTION?                             │    │
 │  │    → Send to RAG Agent  (the librarian)                     │    │
 │  │                                                             │    │
 │  │  Does the user want to DO something (create a ticket)?      │    │
 │  │    → First check with Policy Agent  (the compliance officer)│    │
 │  │    → If approved, send to Action Agent  (the executor)      │    │
 │  │                                                             │    │
 │  │  Is the user asking "am I allowed to do X?"                 │    │
 │  │    → Send to Policy Agent  (the compliance officer)         │    │
 │  └─────────────────────────────────────────────────────────────┘    │
 └──────┬───────────────────┬───────────────────┬───────────────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
   RAG Agent          Policy Agent         Action Agent
  (Librarian)      (Compliance Officer)    (Executor)
```

---

## Layer 2 — The Specialist Agents

### RAG Agent — "The Librarian"

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                        RAG AGENT                                    │
 │                     agents/rag_agent.py                             │
 │                                                                     │
 │  "I look things up in your company's knowledge base and give        │
 │   you answers backed by real documents — I never make things up."   │
 │                                                                     │
 │  Example requests it handles:                                       │
 │    • "What is the remote access policy?"                            │
 │    • "Show me the onboarding runbook."                              │
 │    • "What does our SLA say about P1 incidents?"                    │
 │                                                                     │
 │  How it works:                                                      │
 │    1. Receives the question                                         │
 │    2. Calls search_enterprise_knowledge tool  ──────────────────┐   │
 │    3. Gets back matching documents                               │   │
 │    4. Builds an answer using only those documents                │   │
 │    5. Cites the source so you know where it came from            │   │
 └──────────────────────────────────────────────────────────────┬──┘   │
                                                                │      │
                    ┌───────────────────────────────────────────┘      │
                    ▼                                                   │
 ┌─────────────────────────────────────────────────────────────────────┘
 │                    RETRIEVAL LAYER
 │                  retrieval/retrieval.py
 │
 │  "I am the bridge between the agent and wherever your
 │   company's documents actually live."
 │
 │  You pick ONE backend in your .env file:
 │
 │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
 │  │  Agent Search    │  │   RAG Engine     │  │  Vector Search   │
 │  │                  │  │                  │  │                  │
 │  │  Easiest to set  │  │  Google-managed  │  │  You control     │
 │  │  up. Google does │  │  production RAG. │  │  everything.     │
 │  │  the heavy       │  │  Good for most   │  │  Best for        │
 │  │  lifting.        │  │  enterprises.    │  │  custom needs.   │
 │  │  (default)       │  │                  │  │                  │
 │  └──────────────────┘  └──────────────────┘  └──────────────────┘
 │
 │  All three connect to your company's documents:
 │  policies, runbooks, SOPs, wikis, PDFs, etc.
 └─────────────────────────────────────────────────────────────────────
```

---

### Policy Agent — "The Compliance Officer"

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                       POLICY AGENT                                  │
 │                    agents/policy_agent.py                           │
 │                                                                     │
 │  "Before anything is done, I check whether it is allowed.           │
 │   I am the safety gate that runs before every action."             │
 │                                                                     │
 │  Example requests it handles:                                       │
 │    • "Can a developer delete a production database?"  → DENIED      │
 │    • "Can a support agent create a P2 ticket?"        → PERMITTED   │
 │    • "Can a manager approve a refund over $10,000?"   → NEEDS REVIEW│
 │                                                                     │
 │  It always gives one of three verdicts:                             │
 │                                                                     │
 │   ✅ PERMITTED      — safe to proceed                               │
 │   ❌ DENIED         — not allowed, stops here                       │
 │   ⚠️  REQUIRES_APPROVAL — a human must sign off first               │
 │                                                                     │
 │  How it works:                                                      │
 │    1. Receives the proposed action + user's role                    │
 │    2. Calls check_policy tool  (connects to your policy engine,     │
 │       e.g. OPA, IAM, or a custom rules database)                   │
 │    3. Returns the verdict + reason                                  │
 └─────────────────────────────────────────────────────────────────────┘
```

---

### Action Agent — "The Executor"

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                       ACTION AGENT                                  │
 │                    agents/action_agent.py                           │
 │                                                                     │
 │  "Once the Policy Agent says it's OK, I do the actual work —        │
 │   talking to real systems on your behalf."                          │
 │                                                                     │
 │  Example requests it handles:                                       │
 │    • "Create a P2 ticket: VPN is broken for payments team."         │
 │    • "What is the status of ticket INC0012345?"                     │
 │    • "Look up the last deployment record."                          │
 │                                                                     │
 │  How it works:                                                      │
 │    1. Receives the approved action                                  │
 │    2. Calls the right tool:                                         │
 │         create_ticket    → creates a ticket in ServiceNow/Jira      │
 │         get_ticket_status → looks up a ticket by ID                 │
 │    3. Reports back the result (ticket ID, current state, next steps)│
 │    4. If something goes wrong, returns a structured error —         │
 │       never crashes silently                                        │
 └─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 3 — Tools (The Actual Connectors to Real Systems)

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                  TOOLS  —  tools/enterprise_tools.py                │
 │                                                                     │
 │  Tools are the hands of the agents. An agent thinks and decides;   │
 │  a tool reaches out and touches a real system.                      │
 │                                                                     │
 │  ┌───────────────────────────┐   ┌───────────────────────────────┐  │
 │  │ search_enterprise_        │   │ get_ticket_status             │  │
 │  │ knowledge                 │   │                               │  │
 │  │                           │   │ Input:  ticket ID             │  │
 │  │ Input:  a question        │   │ Output: ticket state,         │  │
 │  │ Output: matching docs     │   │         priority, assignee    │  │
 │  │         + source          │   │                               │  │
 │  └───────────────────────────┘   └───────────────────────────────┘  │
 │                                                                     │
 │  ┌───────────────────────────┐   ┌───────────────────────────────┐  │
 │  │ create_ticket             │   │ check_policy                  │  │
 │  │                           │   │                               │  │
 │  │ Input:  summary,          │   │ Input:  action, user role,    │  │
 │  │         description,      │   │         resource              │  │
 │  │         priority          │   │ Output: allowed? + reason     │  │
 │  │ Output: new ticket ID     │   │                               │  │
 │  └───────────────────────────┘   └───────────────────────────────┘  │
 │                                                                     │
 │  All tools follow the same rule:                                    │
 │    • If it works  → { "status": "success", ... }                   │
 │    • If it fails  → { "status": "error", "message": "..." }        │
 │  This means a broken tool never crashes the whole system.          │
 └─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 4 — Supporting Infrastructure

### Configuration — "The Settings File"

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                     CONFIG  —  config.py                            │
 │                                                                     │
 │  Reads all settings from your .env file at startup.                 │
 │  If a required setting is missing, it stops immediately and         │
 │  tells you exactly what to fix — no cryptic errors.                 │
 │                                                                     │
 │  Key settings:                                                      │
 │    GOOGLE_CLOUD_PROJECT    ← your GCP project ID (required)         │
 │    RETRIEVAL_BACKEND       ← which search system to use             │
 │    SUPERVISOR_MODEL        ← which Gemini model the manager uses    │
 │    POLICY_MODEL            ← which model the compliance officer uses│
 │    LOG_LEVEL               ← how much logging output you want       │
 └─────────────────────────────────────────────────────────────────────┘
```

### Security — "The ID Badge Check"

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                   SECURITY  —  security/iam.py                      │
 │                                                                     │
 │  Every call the system makes to Google Cloud is authenticated.      │
 │  Think of it like showing an ID badge before entering a building.   │
 │                                                                     │
 │  On your laptop (development):                                      │
 │    Uses your personal gcloud login                                  │
 │    (gcloud auth application-default login)                          │
 │                                                                     │
 │  In production (Cloud Run / GKE):                                   │
 │    Uses a service account — a dedicated identity for the agent,     │
 │    with only the minimum permissions it needs                       │
 │                                                                     │
 │  This is checked at startup, so you find out immediately            │
 │  if credentials are missing — not halfway through a request.        │
 └─────────────────────────────────────────────────────────────────────┘
```

### Observability — "The Flight Recorder"

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │              OBSERVABILITY  —  observability/telemetry.py           │
 │                                                                     │
 │  Every request leaves a trail so you can see exactly what happened. │
 │                                                                     │
 │  Cloud Logging                                                      │
 │    Like a detailed diary. Every agent action, tool call, and        │
 │    error is written to Google Cloud Logging.                        │
 │    You can search and filter in the GCP Console.                    │
 │                                                                     │
 │  Cloud Trace                                                        │
 │    Like a stopwatch for every step. Shows you a timeline of the     │
 │    entire request — Supervisor → Policy Agent → Action Agent —      │
 │    so you can spot slowdowns and failures instantly.                │
 │                                                                     │
 │  Both are set up once at startup (not once per request),            │
 │  so there is no duplicate logging.                                  │
 └─────────────────────────────────────────────────────────────────────┘
```

---

## Full End-to-End Flow

Here is what happens from the moment you type a request to the moment you get an answer.

```
  YOU
   │
   │  "Create a P2 ticket: VPN is broken for payments team."
   │
   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  main.py                                                             │
│  • Wraps the request in a trace span (flight recorder starts)        │
│  • Sends it to the Supervisor Agent                                  │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR AGENT                                                    │
│  Reads: "This is an action request → need Policy check first"        │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               │  "Is creating a ticket allowed for this user?"
               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  POLICY AGENT                                                        │
│  Calls check_policy("create_ticket", user_role, "ticketing-system")  │
│  Result: ✅ PERMITTED                                                │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               │  "Approved — go ahead"
               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ACTION AGENT                                                        │
│  Calls create_ticket(summary="VPN broken...", priority="P2")         │
│  Result: { "status": "success", "ticket_id": "INC0099999" }         │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               │  "Ticket INC0099999 created successfully."
               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR AGENT                                                    │
│  Synthesizes the result into a clear, friendly reply                 │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               ▼
  YOU  ←  "Ticket INC0099999 has been created at P2 priority.
           The payments team VPN issue is now tracked."

  (Meanwhile, Cloud Logging recorded every step and Cloud Trace
   shows the full timeline in GCP Console.)
```

---

## What Lives Where — File Map

```
  multi-agent-gcp-sol1/
  │
  ├── main.py              ← START HERE. Runs the system. Wires everything together.
  ├── agent.py             ← Used by the ADK web/CLI tool for interactive testing.
  ├── config.py            ← All settings. Fails loudly if something is missing.
  ├── .env                 ← Your private settings (never committed to git).
  ├── .env.example         ← Template showing every setting you can configure.
  ├── pyproject.toml       ← Declares Python 3.11+ requirement and dependencies.
  │
  ├── agents/
  │   ├── supervisor.py    ← The manager. Reads requests, routes to specialists.
  │   ├── rag_agent.py     ← The librarian. Looks things up. Never guesses.
  │   ├── action_agent.py  ← The executor. Does things in real systems.
  │   └── policy_agent.py  ← The compliance officer. Permits or denies actions.
  │
  ├── tools/
  │   └── enterprise_tools.py  ← The connectors. Each function calls a real API.
  │                               Replace stubs with real API calls to go live.
  │
  ├── retrieval/
  │   └── retrieval.py     ← The document search switch. Pick your backend in .env.
  │
  ├── observability/
  │   └── telemetry.py     ← Logging + tracing. Set up once, runs everywhere.
  │
  └── security/
      └── iam.py           ← Credential validation. Checked at startup.
```

---

## Glossary — Plain English Definitions

| Term | What it actually means |
|---|---|
| **Agent** | A piece of AI that can think, make decisions, and call tools |
| **Supervisor Agent** | The manager agent that reads requests and routes them |
| **RAG** | "Retrieval-Augmented Generation" — fancy term for "look it up before answering" |
| **Tool** | A Python function the agent can call to interact with a real system |
| **Policy Engine** | A system that says yes/no to actions based on rules (like an access control list) |
| **ADK** | Google Agent Development Kit — the framework that runs the agents |
| **Gemini** | Google's AI model that powers the agents' reasoning |
| **Vertex AI** | Google Cloud's AI platform — where Gemini runs in production |
| **Cloud Trace** | A GCP tool that shows a timeline of every step in a request |
| **Cloud Logging** | A GCP tool that stores all log messages from your system |
| **Service Account** | A dedicated identity (like a user account, but for software) with its own permissions |
| **ADC** | Application Default Credentials — how code authenticates to Google Cloud automatically |
| **CMEK** | Customer-Managed Encryption Keys — you control the encryption key for your data |
| **VPC Service Controls** | A GCP security perimeter that prevents data from leaving your defined boundary |

---

## Key Design Decisions — Interview Guide

This section explains the important architectural choices made in this system and the reasoning
behind each one. These are the questions you are most likely to face in a technical interview.

---

### 1. Why use Google ADK as the agent framework?

**Decision:** Google ADK orchestrates all agents, even on GCP.

**Why:**
ADK provides a production-grade agent loop out of the box — session management, tool
calling, streaming responses, sub-agent delegation, and a built-in web UI for testing.
Building this from scratch would take weeks. ADK also integrates natively with Vertex AI
and Gemini, which eliminates authentication boilerplate.

**Interview angle:** "We chose ADK over LangChain or a custom loop because it handles
the agent lifecycle (sessions, retries, streaming) as infrastructure, not application code.
That lets the team focus on business logic rather than plumbing."

---

### 2. Why a Supervisor + specialist agent pattern instead of one big agent?

**Decision:** One SupervisorAgent routes to three specialist agents (RAG, Action, Policy).

**Why:**
A single agent given all responsibilities becomes unreliable — the model tries to do
everything and does nothing well. Separating concerns means:
- Each agent has a narrow, well-defined prompt — easier to test and tune
- Each agent can use a different model (e.g. Gemini Pro for Policy, Flash for RAG)
- Failures are isolated — a broken Action agent does not affect knowledge retrieval
- New specialists can be added without touching existing agents

**Interview angle:** "This is the same principle as microservices applied to AI agents —
separation of concerns, independent deployability, and fault isolation."

---

### 3. Why is PolicyAgent always checked before ActionAgent?

**Decision:** Every write action must pass through PolicyAgent before ActionAgent executes.

**Why:**
Without a policy gate, the Action agent could create tickets, modify records, or trigger
workflows for any user regardless of their role. The Policy agent acts as an explicit
authorization layer — it mirrors how real enterprise systems work (IAM policies, RBAC).
If the policy check is skipped, the system has no auditability for who was allowed to do what.

**Interview angle:** "We applied the principle of least privilege at the agent level.
No action executes without an explicit PERMITTED verdict. This creates an audit trail and
prevents privilege escalation through the AI layer."

---

### 4. Why does the RAG agent never answer from its own knowledge?

**Decision:** RAGAgent is instructed to only use retrieved content — it never answers from
the model's training data.

**Why:**
In an enterprise context, the model's general knowledge is a liability, not an asset.
Company policies, runbooks, and SOPs change frequently. A model answering from training
data could give confidently wrong answers (e.g. an outdated security policy).
Grounding every answer in retrieved documents means every claim is traceable to a source.

**Interview angle:** "This is the core guarantee of RAG — not just better answers, but
auditable answers. Every response can be traced back to a specific document version.
That is critical for compliance and incident response."

---

### 5. Why three retrieval backend options (Agent Search, RAG Engine, Vector Search)?

**Decision:** The retrieval backend is switchable via a single environment variable.

**Why:**
Different enterprises are at different stages of maturity. Agent Search is the fastest
path to production — no infrastructure to manage. RAG Engine adds production-grade
orchestration. Vector Search gives full control for teams with specific chunking or
ranking requirements. Locking in one backend would make the template unusable for most
organisations. The abstraction layer (retrieval.py) means agents never know or care
which backend is running.

**Interview angle:** "We applied the strategy pattern here — a common interface with
swappable implementations. This is how you build templates that work across different
enterprise maturity levels without forcing a rewrite."

---

### 6. Why is setup_telemetry() called once at module level, not inside run()?

**Decision:** Telemetry is initialised once at startup, not per request.

**Why:**
If called per request, every invocation of run() would register a new TracerProvider
and a new Cloud Logging handler. After 100 requests, there are 100 handlers writing
duplicate log entries. In a long-running service (Cloud Run, GKE) this causes memory
growth and log flooding. Module-level initialisation is idiomatic for any shared
resource (database connections, logging, tracing).

**Interview angle:** "This is a classic singleton pattern applied to infrastructure
setup. The rule is: initialise once, use everywhere. The same principle applies to
database connection pools."

---

### 7. Why does credential validation happen at startup, not on the first request?

**Decision:** get_credentials() (GCP) / get_identity() (AWS) is called at module load time.

**Why:**
Failing at startup is far better than failing mid-request. If credentials are wrong,
the service should refuse to start and emit a clear error — not silently start, serve
a few requests, then crash with a confusing auth error when a real user is waiting.
This is the "fail fast" principle applied to infrastructure dependencies.

**Interview angle:** "In production systems, you want the health check to fail at boot,
not at runtime. Early failure surfaces configuration problems in staging before they
reach production users."

---

### 8. Why does run() raise RuntimeError instead of returning "No response."?

**Decision:** If no final response event arrives, the function raises an exception.

**Why:**
Returning a silent fallback string like "No response." hides failures. The caller has
no way to distinguish between a real agent response and a failure. Raising an exception
forces the caller to handle the failure explicitly — log it, retry it, or surface it to
the user with a proper error message. Silent failures are the hardest bugs to diagnose
in production.

**Interview angle:** "This follows the principle of making errors visible. A string that
looks like a normal response but isn't is a silent failure — the worst kind in a
distributed system."

---

### 9. Why are user_id and session_id generated with UUID instead of hardcoded?

**Decision:** run() generates random user_id and session_id per call if not provided.

**Why:**
The original code had USER_ID = "user-001" — a hardcoded constant. In a real system,
every user and every session must be distinct. Hardcoded IDs mean all requests share
the same session state, which causes context bleed between users. UUID generation is
the minimum viable approach for correctness; in production these would come from the
authenticated user's identity token.

**Interview angle:** "Session isolation is a fundamental correctness requirement for
any multi-user system. Hardcoded session IDs are a correctness bug, not just a
design smell."

---

### 10. Why are all tools wrapped in try/except with structured return values?

**Decision:** Every tool returns {"status": "success"|"error"|"blocked"} and never raises.

**Why:**
If a tool raises an uncaught exception, the ADK agent loop crashes and the user gets
nothing. By catching all exceptions and returning a structured error dict, the agent
can decide what to do — retry, apologise to the user, or escalate. This is the same
principle as HTTP status codes: a structured signal is always better than an unhandled
exception. It also makes tool behaviour testable — you can assert on the returned dict
without mocking exception flows.

**Interview angle:** "Tools are the boundary between the AI layer and real systems.
Boundaries must be hardened. The agent should always receive a signal it can reason
about, never a raw exception."
