{%- if not needs_observability -%}
# Observability scaffolding was disabled at template time.
{%- else -%}
"""Prometheus metrics for {{ project_name }}."""

from __future__ import annotations

from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

ERROR_COUNT = Counter(
    "application_errors_total",
    "Total application errors",
    ["error_type"],
)
{%- endif %}
