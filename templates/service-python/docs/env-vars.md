# Environment variables

Configuration is read exclusively from environment variables. Defaults below are the application defaults. The deployed values are set per environment in the product's gitops-app repo (`services.yaml` → `env`, `replicas`, `resources`).

## Core

| Variable | Default | Description |
|---|---|---|
| `PORT` | `{{ port }}` | HTTP port the service listens on. |
| `LOG_LEVEL` | `INFO` | Logging level. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
{%- if needs_observability %}

## Observability

| Variable | Default | Description |
|---|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _(unset — tracing disabled)_ | Standard OpenTelemetry endpoint, e.g. `http://otel-collector:4318`; injected by the platform's observability addon. When set, `configure_tracing()` runs at startup. |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` | `http/protobuf` or `grpc`. |
| `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES` | _(project name)_ | Resource attributes; set by the observability addon. |
| `OTLP_ENDPOINT` | _(unset)_ | Legacy gRPC endpoint (kept for compatibility); prefer the standard variables. |
| `METRICS_PORT` | `{{ port }}` | Port serving `/metrics` (same as the main HTTP port unless overridden). |
{%- endif %}
{%- if needs_database != "none" %}

## Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | _(required)_ | Connection string for the {{ needs_database }} backend. |
{%- endif %}
