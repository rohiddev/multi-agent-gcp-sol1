import os
from dotenv import load_dotenv

load_dotenv()

VALID_RETRIEVAL_BACKENDS = {"agent_search", "rag_engine", "vector_search"}


def _require(key: str) -> str:
    """Return the value of a required environment variable, or raise with a helpful message."""
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Copy .env.example to .env and fill in your values."
        )
    return val


def _optional(key: str, default: str) -> str:
    """Return the value of an optional environment variable, falling back to default."""
    return os.getenv(key, default)


# --- Required ---
PROJECT_ID = _require("GOOGLE_CLOUD_PROJECT")

# --- Google Cloud ---
LOCATION = _optional("GOOGLE_CLOUD_LOCATION", "us-central1")

# --- Model selection ---
SUPERVISOR_MODEL = _optional("SUPERVISOR_MODEL", "gemini-2.5-flash")
RAG_MODEL        = _optional("RAG_MODEL",        "gemini-2.5-flash")
ACTION_MODEL     = _optional("ACTION_MODEL",     "gemini-2.5-flash")
POLICY_MODEL     = _optional("POLICY_MODEL",     "gemini-2.5-pro")

# --- Retrieval backend ---
RETRIEVAL_BACKEND = _optional("RETRIEVAL_BACKEND", "agent_search")

if RETRIEVAL_BACKEND not in VALID_RETRIEVAL_BACKENDS:
    raise EnvironmentError(
        f"RETRIEVAL_BACKEND='{RETRIEVAL_BACKEND}' is invalid. "
        f"Valid values: {sorted(VALID_RETRIEVAL_BACKENDS)}"
    )

AGENT_SEARCH_ENGINE_ID = _optional("AGENT_SEARCH_ENGINE_ID", "")
RAG_CORPUS_NAME        = _optional("RAG_CORPUS_NAME", "")

# Vector Search (only needed when RETRIEVAL_BACKEND=vector_search)
VECTOR_SEARCH_INDEX_ENDPOINT    = _optional("VECTOR_SEARCH_INDEX_ENDPOINT", "")
VECTOR_SEARCH_DEPLOYED_INDEX_ID = _optional("VECTOR_SEARCH_DEPLOYED_INDEX_ID", "")

# --- Application ---
APP_NAME  = _optional("APP_NAME",  "enterprise-multi-agent")
LOG_LEVEL = _optional("LOG_LEVEL", "INFO")
