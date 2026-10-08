---
spec_id: 024-secrets-without-values-in-git
title: Secrets without values in git
status: done
priority: P1
---

# 024 — Secrets without values in git

## Stories

As a founder, I want secrets handled by External Secrets Operator, so that git holds references only.

## Acceptance criteria

- **AC-024.1** `secrets.generate: [KEY…]` makes ESO create stable random values once per environment; `secrets.remote` reads from the store named in `app.yaml`.
- **AC-024.2** `/gitops:secret set <service> <secret> <KEY> [--env dev]` reads the value from a hidden prompt or stdin; `list` shows which exist. Values never appear in output or git.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** ADR-018 · **Code:** `scripts/cplat/secret.py`

## Changelog

- 2026-10-08 migrated from STORY-024 in docs/backlog.md
