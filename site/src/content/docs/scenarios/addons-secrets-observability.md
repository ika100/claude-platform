---
title: "Add Postgres, secrets and observability"
description: "Give a service a database, credentials and telemetry with three declarations."
---

**Situation.** `shop-api` needs a Postgres database, a signing key, a payment-provider key and traces, and you do not want a project for each.

## Steps

In the GitOps repository:

```text
/gitops:addon add postgres
/gitops:addon add observability --ui lgtm
/gitops:compose add shop-api --uses postgres --generate shop-api-auth=JWT_KEY --secret shop-api-stripe=STRIPE_KEY
```

(For an existing service, edit its entry in `services.yaml`: add `uses: [postgres]` and the `secrets:` list; the command shows the diff.) Merge the pull requests, then locally:

```bash
devbox run cluster-up                                   # installs the operators the declarations need
/gitops:secret set shop-api shop-api-stripe STRIPE_KEY  # hidden prompt; value goes to the local secret store only
```

## What you get

| You declared | The platform renders |
|---|---|
| `addons.postgres` + `uses: [postgres]` | A CloudNativePG cluster per environment where a service uses it; `DATABASE_URL` and `PG*` reach the service from the operator's Secret |
| `generate: [JWT_KEY]` | An `ExternalSecret` plus a password generator: ESO creates a random value in the cluster, once per environment. Nothing in git |
| `remote: {keys: [STRIPE_KEY]}` | An `ExternalSecret` that reads the value from your secret store (locally the `secrets-store` namespace; in production Vault, AWS or GCP) |
| `addons.observability` | An OpenTelemetry Collector per environment; every service gets the standard `OTEL_*` variables; with `--ui lgtm` a local Grafana at `http://grafana.localhost:8088` |

## Check it

- `/shared:status` lists the addons next to the services with their ArgoCD health.
- `/shared:doctor` warns when an operator is missing in the cluster you are pointed at.
- Tracing: call the service, open Grafana, find the trace with `service.name` and `deployment.environment` already set.

## Limits to know

The Postgres addon has no backups, point-in-time recovery or connection pooling; removing it never deletes the data. Observability forwards telemetry but ships no alert rules. See [Addons](/claude-platform/concepts/addons/), [Secrets](/claude-platform/concepts/secrets/) and [ADR-020](/claude-platform/reference/adr/020/), [021](/claude-platform/reference/adr/021/).
