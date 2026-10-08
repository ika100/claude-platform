---
spec_id: 033-bootstrap-a-whole-product-from-a
title: Bootstrap a whole product from a manifest
status: done
priority: P0
---

# 033 — Bootstrap a whole product from a manifest

## Stories

As a founder, I want `/shared:new-app <manifest>` to create the gitops-app repo and every component repo and wire them together, so that standing up a product is one command instead of one `new-service` per repo plus a `compose`.

**Manifest (`app.yml`):**
```yaml
app: taskboard            # name of the gitops-app repo; also the --app value of every service
org: ika100               # optional, default: your gh login
visibility: private       # optional, private|public
components:
  - name: taskboard-api
    description: Task CRUD API
    shape: service-python
    data: {needs_database: "true"}   # optional template options, same as new-service --data
  - name: taskboard-web
    description: Taskboard frontend
    shape: web-nextjs
```

## Acceptance criteria

- **AC-033.1** `--dry-run` validates everything and prints every repo, shape, topic and template option that would be created, in creation order, without any side effect (no directory, no GitHub call that writes).
- **AC-033.2** Validation runs before any side effect and aborts on the first problem with a `fix:` line: unknown keys; names not matching `^[a-z][a-z0-9-]{1,39}$`; duplicate names; a component named like the app; a shape not in `shapes.yml`, `planned`, or `gitops-app` (the app repo is implicit); unknown `data` keys (checked against the template's `copier.yml`); a target directory that exists and is not empty; a GitHub repo that already exists (`gh repo view`); `gh` missing or not logged in.
- **AC-033.3** Creation order is independent of the order in the file: gitops-app first, then libraries, then services (Python, Java, Go), then web frontends.
- **AC-033.4** Each repo is created with the same code path as `/shared:new-service` (same template rendering, bootstrap commit, topic rules, plugin auto-enable); deployable components get `--app <org>/<app>`, libraries get none.
- **AC-033.5** After the repos exist, one `compose add` pins all deployable components in the gitops-app repo and opens a single PR. Libraries are not composed.
- **AC-033.6** Failure midway stops at once and reports which repos were created, which were not, and the undo commands. Re-running with `--resume` skips repos that already exist and continues with the rest, including the compose PR.
- **AC-033.7** `--no-github` renders everything locally and prints the GitHub and compose commands instead of running them.
- **AC-033.8** The output follows the `Report` convention: what I will do (with `[outward]` marks) / what happened / next / how to undo.
- **AC-033.9** Interactive mode is out of scope for this story.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** end-to-end scenario Phase 1, UX-2, UX-3 · **Plan:** [plan/new-app.md](../../plan/new-app.md) · **Code:** `scripts/cplat/newapp.py`

## Changelog

- 2026-10-08 migrated from STORY-033 in docs/backlog.md
