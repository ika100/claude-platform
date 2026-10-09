---
spec_id: 062-dev-runs-every-merged-build
title: dev runs every merged build
status: building
priority: P1
---

# 062 — dev runs every merged build

## Problem

In end-to-end run 2 (2026-10-09) todo-api#5 and todo-web#6 were merged and their new images published, but the `dev` environment kept running the old code: `dev` pins `:latest` with `imagePullPolicy: Always`, and nothing restarts the pods when a new `latest` is pushed. The feature only appeared after the operator ran `kubectl rollout restart`. The docs and the agents say "dev tracks latest", and `/app:build` told the user so after merging, so a user cannot tell whether a merged feature runs. `render.py` already forbids `latest` outside dev for the same reason: a moving tag does not trigger a rollout.

## Stories

As a developer, I want every merge to `main` to reach `dev` without a manual step, so that what I check in `dev` is what I just merged.

## Acceptance criteria

- **AC-062.1** Given a service composed in a gitops-app, when a commit is merged to the service's `main` and its image is published, then the service's CI opens a PR in the gitops-app that pins `dev` to that image's `sha-<7>` tag, the PR merges itself once the gitops-app CI passes, and `dev` runs the image within 10 minutes without a manual command.
- **AC-062.2** Given the change reaching `dev`, when someone looks at the gitops-app repo, then the image `dev` runs is visible there as an immutable tag (`sha-<7>` or a version), not `latest`.
- **AC-062.3** Given a published image whose rollout fails in `dev`, when the user runs `/shared:status`, then the service shows the image that was intended and that it is not healthy.
- **AC-062.4** Given a freshly generated gitops-app and service, when both are created, then the mechanism of AC-062.1 is set up without extra steps, except the one token the service repo needs to write to the gitops-app, which `/shared:new-service` asks for or names with the exact command to add it.
- **AC-062.5** Given the docs (USER-JOURNEY, HOW-IT-WORKS, the gitops-app CLAUDE.md) and the agents, when they describe `dev`, then they describe the mechanism actually used.
- **AC-062.6** Given a pin PR whose gitops-app CI fails, when it does not merge, then `dev` keeps the previous image and the failure is visible on the PR.

## Non-goals

- Automatic promotion to `staging` or `prod`; promotion stays a reviewed PR.

## Open questions

~~How does `dev` follow `main`? (a) the service's CI opens and auto-merges a PR in the gitops-app that pins `dev` to `sha-<7>`, (b) Argo CD Image Updater writes the pin back to git, (c) keep `latest` and restart the deployment on a new digest. (suggested: (a) — no new cluster component, the pin is reviewable history, and it works for every cluster; needs a token in the service repo that can write to the gitops-app; affects AC-062.1, AC-062.2, AC-062.4)~~ Answered: (a) the service's CI opens a pin PR to `sha-<7>` in the gitops-app.
~~If (a): auto-merge the pin PR, or leave it for a human? (suggested: auto-merge after the gitops-app CI passes; dev is meant to follow main; affects AC-062.1)~~ Answered: auto-merge once the gitops-app CI passes.

## References

- [run 2 log](../../e2e/2026-10-09-todo-second-feature.md), findings 3 and 17.

## Changelog

- 2026-10-09 created from end-to-end run 2
- 2026-10-09 open questions answered: the service's CI opens a pin PR to sha-<7> in the gitops-app, auto-merged after its CI passes (AC-062.6 added)
- 2026-10-09 approved
- 2026-10-09 building
