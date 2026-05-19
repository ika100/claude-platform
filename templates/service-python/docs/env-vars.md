# Environment variables

Configuration is read exclusively from environment variables. Defaults below match `k8s/base/deployment.yaml` and `devbox.json`. Override per-environment via the Kustomize overlays in `k8s/overlays/`.

## Core

| Variable | Default | Description |
|---|---|---|
| `PORT` | `{{ port }}` | HTTP port the service listens on. |
| `LOG_LEVEL` | `INFO` | Logging level. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
{%- if needs_observability %}

## Observability

| Variable | Default | Description |
|---|---|---|
| `OTLP_ENDPOINT` | _(unset — tracing disabled)_ | OpenTelemetry collector OTLP gRPC endpoint. When set, `configure_tracing()` runs at startup. |
| `METRICS_PORT` | `{{ port }}` | Port serving `/metrics` (same as the main HTTP port unless overridden). |
{%- endif %}
{%- if needs_database != "none" %}

## Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | _(required)_ | Connection string for the {{ needs_database }} backend. |
{%- endif %}
