---
title: "Build a feature with the agent pipeline"
description: "Turn a request into an approved spec, failing acceptance tests, code that passes them and a verified pull request, in any shape."
---

**Situation.** `shop-api` exists; you want "customers can save a wishlist".

## Steps

Pick the command by size:

| Size | Command | What runs |
|---|---|---|
| Small, clear change | `/svc:quick-task add a wishlist count to the profile endpoint` | Coder, quality, tester with a fix loop, then a pull request |
| Real feature, step 1 | `/svc:spec customers can save a wishlist` | Product manager writes `docs/specs/<NNN>-wishlist/spec.md` with acceptance criteria `AC-<NNN>.<n>`; you answer its open questions and approve |
| Real feature, step 2 | `/svc:plan <NNN>` | Architect: `design.md` (contract) and `plan.md` (tasks covering every criterion) |
| Real feature, step 3 | `/svc:build <NNN>` | Failing acceptance tests first, parallel coders until they pass, quality, tester and security in parallel, a reviewer checks every criterion, image check, pull request |
| Bug | `/svc:fix-bug saving twice duplicates the entry` | Coder and tester in a tight loop with a regression test |

The commands detect the repository's shape (Python, Java, Go, Next.js) and route to the matching coder, tester, deployment, observability and release agents. Every phase runs `devbox run <recipe>`, so CI and agents see the same results.

## What you get

- A branch with a conventional commit history and a pull request whose body lists exactly which checks ran.
- A spec you approved, acceptance tests written from it before the code, and `verification.md` showing each criterion with its test and code; the security and image checks are part of `/svc:build`. `/svc:specs` shows where every spec stands.
- Nothing is pushed without your confirmation.

## Across repositories

`/app:build-feature` run in the GitOps repository plans a feature that spans several services (a product spec, a validated and topologically sorted plan, per-repository hand-off commands) and `/app:plans` tracks it. Each repository turns its part into its own spec with `/svc:spec --from-plan`, or `/app:run-plan` does that for every ready repository; nothing merges without you ([ADR-007](/sdlc-foundry/reference/adr/007/), [ADR-023](/sdlc-foundry/reference/adr/023/)).

See the [agent model](/sdlc-foundry/guides/agents/) for how the phases fit together.
