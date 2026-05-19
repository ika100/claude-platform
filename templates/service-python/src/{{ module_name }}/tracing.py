{%- if not needs_observability -%}
# Observability scaffolding was disabled at template time.
{%- else -%}
"""OpenTelemetry tracing for {{ project_name }}.

The OTLP endpoint is read from the OTLP_ENDPOINT env var (default
http://localhost:4317). Tracing is a no-op until configure_tracing()
is called from the application entrypoint.
"""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracing(service_name: str = "{{ project_name }}") -> None:
    """Configure OpenTelemetry tracing with an OTLP exporter."""
    endpoint = os.environ.get("OTLP_ENDPOINT", "http://localhost:4317")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)
{%- endif %}
