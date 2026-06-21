"""
Enterprise Multi-Agent System — entry point.

Architecture:
  SupervisorAgent
    ├── RAGAgent          (enterprise knowledge retrieval)
    ├── ActionAgent       (tickets, system records, API calls)
    └── PolicyAgent       (access control, governance)

Retrieval backend: Agent Search | RAG Engine | Vector Search (set RETRIEVAL_BACKEND in .env)
Observability:     Cloud Trace + Cloud Logging via OpenTelemetry
Security:          Application Default Credentials (service account in production)
"""

import asyncio
import logging
import uuid
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from config import APP_NAME
from agents import supervisor_agent
from observability import setup_telemetry, trace_agent_call
from security.iam import get_credentials

logger = logging.getLogger(__name__)

# --- Startup: validate credentials and initialize telemetry once ---
_credentials, _detected_project = get_credentials()
logger.info("Authenticated to project=%s", _detected_project)

tracer = setup_telemetry()


async def run(
    query: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> str:
    """Run a single query through the multi-agent system.

    Args:
        query: The user's request or question.
        user_id: Optional user identifier. Defaults to a random ID.
        session_id: Optional session identifier. Defaults to a random ID.

    Returns:
        The agent's final response text.

    Raises:
        RuntimeError: If the agent returns no final response.
    """
    user_id    = user_id    or f"user-{uuid.uuid4().hex[:8]}"
    session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    runner = Runner(
        agent=supervisor_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    with trace_agent_call(tracer, "SupervisorAgent", user_id, session_id):
        message = types.Content(
            role="user",
            parts=[types.Part(text=query)],
        )
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            if event.is_final_response():
                return event.content.parts[0].text

    raise RuntimeError(
        f"Agent returned no final response for query={query!r} "
        f"user_id={user_id} session_id={session_id}"
    )


if __name__ == "__main__":
    # Phase 1: enterprise knowledge question (RAG)
    result = asyncio.run(run("What is the company policy on remote access to production systems?"))
    print("AGENT:", result)

    # Phase 2: action request (Policy → Action)
    result = asyncio.run(run("Create a P2 ticket: VPN access is broken for the payments team."))
    print("AGENT:", result)
