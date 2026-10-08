---
spec_id: 056-criteria-stay-environment-neutral
title: Criteria stay environment-neutral
status: building
priority: P2
---

# 056 — Criteria stay environment-neutral

## Problem

AC-001.1 of the todo product spec named the local port `:8088`; on the test host that port was taken (`cluster-up` stopped with a clear fix and ran on 8089), so the criterion no longer matched the running system.

## Stories

As a founder, I want criteria that hold in every environment, so that a spec stays true on another laptop, in CI and in the cluster.

## Acceptance criteria

- **AC-056.1** Given the spec format reference, when the product-manager writes criteria, then it is told not to name host ports, local hostnames or machine paths, and to describe the observable behaviour instead.
- **AC-056.2** Given `devbox run cluster-up` with port 8088 taken, when it runs, then it chooses the next free port, prints the URL it chose and continues; an explicit `LOCAL_HTTP_PORT` still wins.

## Non-goals

- None.

## Open questions

- ~~Pick a free port automatically by default, or keep stopping with the fix as today? (suggested: automatic, the URL is printed anyway; affects AC-056.2)~~ Answered: automatic; an explicit LOCAL_HTTP_PORT still wins.

## References

- [End-to-end run 2026-10-08, issue 14](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 14 of the todo end-to-end run
- 2026-10-08 open question answered: automatic; an explicit LOCAL_HTTP_PORT still wins.
- 2026-10-08 approved
- 2026-10-08 building
