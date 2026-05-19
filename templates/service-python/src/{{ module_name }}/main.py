"""FastAPI entry point for {{ project_name }}."""

from __future__ import annotations

import os

from fastapi import FastAPI
from pydantic import BaseModel

{% if needs_observability -%}
from .logging_config import configure_logging
from .metrics import REQUEST_COUNT

configure_logging(level=os.environ.get("LOG_LEVEL", "INFO"))
{%- endif %}

app = FastAPI(title="{{ project_name }}", version="0.1.0")


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe — returns 200 as long as the process is responding."""
    return HealthResponse(status="ok")


@app.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    """Readiness probe — returns 200 when the service is ready to accept traffic."""
    return HealthResponse(status="ready")


@app.get("/ping")
def ping() -> dict[str, str]:
    """Simple ping endpoint."""
{%- if needs_observability %}
    REQUEST_COUNT.labels(method="GET", endpoint="/ping", status_code="200").inc()
{%- endif %}
    return {"pong": "{{ project_name }}"}
