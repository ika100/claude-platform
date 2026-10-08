---
spec_id: 012-go-template
title: Go template
status: done
priority: P1
---

# 012 — Go template

## Stories

As a founder, I want a Go service on `chi` and `log/slog`.

## Acceptance criteria

- **AC-012.1** `golangci-lint`, `govulncheck`, stdlib `testing` with `go test -cover`, optional Prometheus `/metrics`, distroless static image with the version injected by ldflags.
- **AC-012.2** `go.mod` / `go.sum` are project-owned and pre-resolved.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** ADR-010

## Changelog

- 2026-10-08 migrated from STORY-012 in docs/backlog.md
