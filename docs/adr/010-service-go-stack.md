# ADR-010: `service-go` stack defaults

**Status:** Accepted
**Date:** 2026-05-22

## Context

The `service-go` shape is the second case study for the §4.1 add-a-shape contract. It needs concrete defaults across four axes — HTTP routing, logging, linting, and container image — so the Copier template and the `svc-go` plugin's agents are unambiguous. These decisions cohere into one ADR rather than four because they together define the shape's identity.

## Decision

The `service-go` template ships with:

| Axis | Choice |
|---|---|
| Language / runtime | Go 1.22+ (pinned in template per the platform's version policy) |
| HTTP router | **`github.com/go-chi/chi/v5`** |
| Logging | **stdlib `log/slog`** with `slog.JSONHandler` for production |
| Linter | **golangci-lint** with a curated `.golangci.yml` |
| Container image base | **`gcr.io/distroless/static-debian12:nonroot`** |

### HTTP router — chi

- Idiomatic stdlib-style: `chi.Router` satisfies `http.Handler`; middleware is `func(http.Handler) http.Handler`. No bespoke context type.
- Small dependency surface (a few packages), well-maintained, mature.
- Go 1.22's enhanced ServeMux (method routing) covers many use cases but lacks chi's middleware ergonomics, route groups, and sub-routers — chi remains the better default for service shape.
- Gin rejected as default: faster but uses its own context type, weaker stdlib interop, more "framework"-y feel that the rest of the platform avoids.

### Logging — stdlib `log/slog`

- Go 1.21+ canonical structured logging — no external dependency.
- Template ships `slog.JSONHandler(os.Stdout, …)` configured at startup; logs are JSON-structured by default.
- Future-proof: as stdlib it evolves with Go; ecosystem libraries increasingly accept `*slog.Logger`.
- Performance is adequate for HTTP-service workloads; zerolog/zap are faster but slog has caught up in 1.22+ and the consistency win across all services is worth more than microbenchmark differences.

### Linter — golangci-lint with curated config

- One command, many checks: `go vet`, `staticcheck`, `gosec`, `ineffassign`, `gocritic`, `revive`, `errcheck`. Single CI step.
- Template ships `.golangci.yml` listing the enabled linters and any rule overrides.
- `devbox run quality` invokes `golangci-lint run`; the `quality` agent reads its output.
- Standalone staticcheck rejected: lighter but misses security (gosec) and several correctness checks; would force the `security` agent to do work that belongs in `quality`.

### Container image — distroless/static-nonroot

- `gcr.io/distroless/static-debian12:nonroot` — ~2MB base + the static Go binary.
- Includes CA certs, `/tmp`, `/etc/passwd` entries needed by most apps. Avoids the "where are my certs?" footgun of `scratch`.
- Statically linked Go binaries (default when CGO is off) just work on this base; no libc surprises.
- Matches the `service-java` distroless choice for a uniform security posture across backend shapes.
- Alpine rejected as default: musl libc can bite when cgo is enabled (SQLite, some crypto libs), and the shell + apk surface isn't worth it for production images.

## Devbox recipes (canonical)

The template ships `devbox.json` with at least:

| Recipe | Wraps |
|---|---|
| `test` | `go test -race -cover ./...` |
| `test-fast` | `go test ./...` |
| `lint` | `golangci-lint run` |
| `lint-fix` | `gofmt -w . && goimports -w . && golangci-lint run --fix` |
| `typecheck` | `go build ./...` (no separate type-check phase in Go) |
| `quality` | `lint` then `typecheck` |
| `audit` | `govulncheck ./...` |
| `image-build` | `docker build -t <name>:scan .` |
| `image-scan` | `trivy image --severity CRITICAL,HIGH <name>:scan` |
| `dev` | `go run ./cmd/<name>` |
| `deploy` | `kubectl apply -k k8s/overlays/local/` |

## Module layout

The template scaffolds a standard Go service layout:

```
<repo>/
├── cmd/<name>/main.go      # entrypoint, wires deps
├── internal/
│   ├── server/             # http handlers, routing (chi)
│   ├── service/            # business logic
│   └── config/             # env-var loading
├── go.mod
└── Dockerfile
```

`internal/` keeps implementation private to the module — consumers can't import it, which is the right default for a service.

## Consequences

- The `svc-go` plugin's `coder` agent writes idiomatic Go (passes `golangci-lint run`), uses `chi.Router` and `slog`, and always invokes `devbox run` — never raw `go`/`golangci-lint`.
- The `tester` agent uses stdlib `testing` (plus `github.com/stretchr/testify` if a Copier prompt enables it), reads coverage from `go test -cover`.
- The `deployment` agent's Dockerfile is a multi-stage build: `golang:1.22-alpine` (or similar) build stage with `CGO_ENABLED=0` → distroless runtime stage.
- The `observability` agent (P1) wires `go.opentelemetry.io/otel` for traces, `github.com/prometheus/client_golang/prometheus/promhttp` for `/metrics`, and `slog` configured to emit `trace_id` / `span_id` via an OTel-aware handler.
- Re-evaluate this ADR if Go's stdlib ServeMux gains middleware/routing ergonomics that obsolete chi, or if a future shape needs cgo by default (which would push us off the static distroless image).

## References

- [platform-vision.md §4, §11.9](../requirements/platform-vision.md)
- [ADR-008](008-shape-detection.md) — sniffing fallback uses `go.mod` to detect this shape

## Amendment (implementation, phase 6)

Verified against rendered projects with real Go/golangci-lint/govulncheck runs:

- `.golangci.yml` uses the **golangci-lint v2 schema** (`version: "2"`, `linters.default: standard`, formatters `gofmt` + `goimports`), plus `gosec`, `gocritic`, `revive`, `misspell`, `noctx`, `bodyclose`.
- `go.mod` / `go.sum` are **shipped pre-resolved** (chi, and client_golang when `needs_observability`) so a freshly rendered project builds without network resolution; `go mod tidy` produces no diff against them. Go is pinned as `go <major.minor>.0` in `go.mod` and as `go@<major.minor>` in `devbox.json` / the `golang:<major.minor>` Docker builder.
- The runtime image is `distroless/static-debian12:nonroot` with **no `HEALTHCHECK`** (no shell); liveness/readiness are Kubernetes probes on `/health` and `/ready`.
