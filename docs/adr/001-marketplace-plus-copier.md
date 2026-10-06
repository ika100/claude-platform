# ADR-001: Two-channel distribution — Claude Code marketplace + Copier templates

**Status:** Accepted
**Date:** 2026-05-22 (retroactive — predates the ADR log)

## Context

The fleet needs a way to ship Claude Code agents and project skeletons to many repos without drift. Two artifacts evolve at different speeds: agents change frequently, project skeletons rarely.

## Decision

Two independent distribution channels:

1. **Claude Code marketplace plugins** (`svc`, `gitops`, `shared`) for agents, commands, and hooks. Updates flow via `/plugin marketplace update`.
2. **Copier templates** (`service-python`, `library-python`, …) for project skeletons. Updates flow via `copier update` with conflict resolution.

## Consequences

- Agents and skeletons evolve independently — agent improvements don't require a Copier update.
- Two systems to maintain, but `copier update`'s conflict resolution is the killer feature vs. GitHub Templates' fork-and-drift model.
- This ADR is the foundation that subsequent ADRs (002 onward) extend with shape-specific and cross-cutting choices.

## References

- See [ARCHITECTURE.md](../ARCHITECTURE.md) for the longer-form rationale.
