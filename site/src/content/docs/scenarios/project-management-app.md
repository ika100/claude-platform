---
title: "Worked example: a project management app"
description: "A Spring Boot API, a Next.js UI and PostgreSQL, built and run on a laptop with the platform's own commands."
---

**Situation.** You want a real, small product end to end: create, update and delete projects in a web UI, business logic in a backend, data in PostgreSQL, running on your laptop through the same GitOps flow as production. The sample lives in three public repositories: [`pm-gitops`](https://github.com/ika100/pm-gitops), [`pm-backend`](https://github.com/ika100/pm-backend) and [`pm-web-ui`](https://github.com/ika100/pm-web-ui).

## 1. Create the repositories

```text
/shared:new-service pm-gitops "Project management app: GitOps repository" --gitops --public
/shared:new-service pm-backend "Project management business logic" --type service-java --data needs_database=true --app ika100/pm-gitops --public
/shared:new-service pm-web-ui "Project management web UI" --web --app ika100/pm-gitops --public
```

`--public` is explicit because repositories are private by default; `--data needs_database=true` adds JPA, Flyway, the PostgreSQL driver and Testcontainers tests, already wired to the variables the Postgres addon provides.

## 2. Build the two services

The backend offers `/api/projects` (list with search, status filter, paging and sorting; create; update; delete), validates input, answers errors as RFC 7807 problems, rejects stale edits with `409` through optimistic locking, and requires an `X-API-Key`. The UI lists, searches, creates, edits and deletes, and calls the backend only from its own server side, so the key never reaches the browser. Both ship through the generated pipelines: tests with coverage gates, dependency and secret scans, multi-architecture images on GHCR.

## 3. Declare the application

In `pm-gitops`, one command per decision:

```text
/gitops:addon add postgres
/gitops:addon add observability --ui lgtm
/gitops:compose add pm-backend --uses postgres --generate pm-backend-auth=API_KEY
/gitops:compose add pm-web-ui --expose --env API_URL=http://pm-backend --secret-ref pm-backend-auth
```

The API key is generated inside the cluster by External Secrets; `--secret-ref` lets the UI read the Secret generated for the backend. Enabling `policies:` in `app.yaml` (Enforce in dev) switches on the Kyverno guard rails, and `devbox run validate` checks the rendered workloads against them offline.

## 4. Install it on your laptop

```text
LOCAL_HTTP_PORT=auto devbox run cluster-up
```

`auto` picks a free port when the default is taken. After a few minutes ArgoCD has synced everything, and the script prints the URLs: the UI at `http://pm-web-ui.pm-dev.localhost:<port>/` and Grafana at `http://grafana.localhost:<port>/`.

## What was verified

- Create, edit, search and delete in a real browser; a second edit with an outdated version is refused with `409`, a duplicate name too.
- The rows are in PostgreSQL, the schema comes from Flyway migration `V1`, and the data survives a restart of the backend.
- Traces of the backend arrive in Tempo; Kyverno reports every workload as passing.

## What building it improved in the platform

Building this sample found and fixed: private-only repository creation (`--public`), no way to pass template options (`--data`), no Java database support, no way to reference another service's generated Secret (`--secret-ref`), a silent clash when the default local port is busy, hard-coded ports in the docs, and pull-request titles that could not be re-checked after a fix. See the [changelog](../../reference/changelog/).

## Honest limits

The sample has no user accounts: anyone who can reach the UI can use it, which is fine on a laptop and not for a shared environment. Tasks, milestones and multi-tenancy are out of scope.
