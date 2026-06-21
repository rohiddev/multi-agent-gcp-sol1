"""
Observability setup: OpenTelemetry + Cloud Trace + Cloud Logging.
Call setup_telemetry() once at application startup.
"""

import logging
import google.cloud.logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from config import PROJECT_ID, APP_NAME, LOG_LEVEL


def setup_telemetry() -> trace.Tracer:
    # Cloud Logging — structured logs visible in Cloud Console
    log_client = google.cloud.logging.Client(project=PROJECT_ID)
    log_client.setup_logging(log_level=getattr(logging, LOG_LEVEL))

    # Cloud Trace via OpenTelemetry — distributed tracing across all agents
    exporter = CloudTraceSpanExporter(project_id=PROJECT_ID)
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    return trace.get_tracer(APP_NAME)


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
