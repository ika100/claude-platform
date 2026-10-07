---
title: "Build a feature with the agent pipeline"
description: "Use the orchestration commands to turn a request into a tested pull request in any shape."
---

**Situation.** `shop-api` exists; you want "customers can save a wishlist".

## Steps

Pick the command by size:

| Size | Command | What runs |
|---|---|---|
| Plan only | `/svc:plan-feature wishlist` | Product manager and architect: stories and an implementation plan, no code |
| Small, clear change | `/svc:quick-task add a wishlist count to the profile endpoint` | Coder, quality, tester with a fix loop, then a pull request |
| Real feature | `/svc:build-feature customers can save a wishlist` | Product manager, architect, parallel coders, quality, tester and security in parallel, image check, pull request. `--no-pm` skips the product-manager phase for precise requests |
| Bug | `/svc:fix-bug saving twice duplicates the entry` | Coder and tester in a tight loop with a regression test |

The commands detect the repository's shape (Python, Java, Go, Next.js) and route to the matching coder, tester, deployment, observability and release agents. Every phase runs `devbox run <recipe>`, so CI and agents see the same results.

## What you get

- A branch with a conventional commit history and a pull request whose body lists exactly which checks ran.
- Tests added with the code; the security and image checks are part of the pipeline for `build-feature`.
- Nothing is pushed without your confirmation.

## Across repositories

`/app:build-feature` run in the GitOps repository plans a feature that spans several services (stories, a validated and topologically sorted plan, per-repository hand-off commands) and `/app:plans` tracks it. It is plan-only by design: you run the per-repository commands yourself ([ADR-007](/sdlc-foundry/reference/adr/007/)).

See the [agent model](/sdlc-foundry/guides/agents/) for how the phases fit together.
