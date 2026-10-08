---
spec_id: 059-security-scans-are-quiet-and-the-base
title: Security scans are quiet and the base image is tracked
status: draft
priority: P2
---

# 059 — Security scans are quiet and the base image is tracked

## Problem

The web template's security recipe printed 61 "No plugins to scan with!" lines from detect-secrets but passed, which hides whether files were scanned. todo-api's image scan reported 44 HIGH CVEs in `python:3.12-slim`, all without released fixes, as a warning in the build report only.

## Stories

As a founder, I want security output I can read in a minute, so that real findings stand out and unfixable base-image findings are tracked instead of repeated.

## Acceptance criteria

- **AC-059.1** Given the web template, when `devbox run security` runs, then detect-secrets scans with its configured plugins and prints no "No plugins to scan with!" lines.
- **AC-059.2** Given an image scan whose HIGH findings all have no released fix, when the security agent reports, then it summarises them as unfixed base-image findings with the base image and count, separately from fixable findings.

## Non-goals

- Changing base images.

## Open questions

None.

## References

- [End-to-end run 2026-10-08, issue 17](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 17 of the todo end-to-end run
