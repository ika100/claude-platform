---
title: "Agents and orchestration"
description: "Scripts do the deterministic work; agents orchestrate and ask before anything outward-facing."
sidebar:
  order: 7
---

Two layers:

1. **`cplat`**, a tested CLI (`new-service`, `update-service`, `compose`, `promote`, `addon`, `secret`, `doctor`, `status`, `feedback`). Every command has `--dry-run` and a clear report (what it will do, what it did, how to undo).
2. **Slash commands and agents**, thin prompts that run the script, show you the preview, and relay the result. Orchestration commands (`/svc:build-feature`, `/svc:quick-task`, `/svc:fix-bug`, `/svc:release`) spawn specialised agents (product manager, architect, coder, tester, security, deployment, release) in phases, routed by shape.

Rules every agent follows: use `devbox run <recipe>` and never call tools directly; ask before pushes, pull requests, repository creation and anything that touches a cluster; stop and offer `/shared:report-issue` when a platform template or script misbehaves. The full model, including phases and context hand-offs, is in [the agent model](/sdlc-foundry/guides/agents/).
