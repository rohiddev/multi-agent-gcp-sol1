"""
Observability setup: OpenTelemetry + Cloud Trace + Cloud Logging.

Call setup_telemetry() once at application startup (module level in main.py).
Subsequent calls are safe — the function is idempotent.
"""

import logging
import google.cloud.logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from config import PROJECT_ID, APP_NAME, LOG_LEVEL

_tracer: trace.Tracer | None = None


def setup_telemetry() -> trace.Tracer:
    """Initialize Cloud Logging and Cloud Trace. Safe to call multiple times.

    Returns:
        A named OpenTelemetry Tracer for the application.
    """
    global _tracer
    if _tracer is not None:
        return _tracer

    # Cloud Logging — structured logs visible in Cloud Console
    log_client = google.cloud.logging.Client(project=PROJECT_ID)
    log_client.setup_logging(log_level=getattr(logging, LOG_LEVEL))

    # Cloud Trace via OpenTelemetry — distributed tracing across all agents
    exporter = CloudTraceSpanExporter(project_id=PROJECT_ID)
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    _tracer = trace.get_tracer(APP_NAME)
    return _tracer


def trace_agent_call(tracer: trace.Tracer, agent_name: str, user_id: str, session_id: str):
    """Context manager: wraps an agent invocation in a named trace span."""
    return tracer.start_as_current_span(
        f"agent.{agent_name}",
        attributes={
            "agent.name": agent_name,
            "user.id": user_id,
            "session.id": session_id,
            "app.name": APP_NAME,
        },
    )
