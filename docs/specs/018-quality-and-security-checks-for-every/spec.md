---
spec_id: 018-quality-and-security-checks-for-every
title: Quality and security checks for every shape
status: done
priority: P0
---

# 018 — Quality and security checks for every shape

## Stories

As a contributor, I want `/shared:check-quality` to audit my repo read-only.

## Acceptance criteria

- **AC-018.1** Runs the shape's `quality` and `security` devbox recipes (Python ruff/mypy/pip-audit, web ESLint/tsc/audit, Java Spotless/Checkstyle/OWASP or trivy, Go gofmt/vet/staticcheck/govulncheck) plus detect-secrets and trivy, in parallel.
- **AC-018.2** Produces one combined report and changes no code.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** PRD E1

## Changelog

- 2026-10-08 migrated from STORY-018 in docs/backlog.md
