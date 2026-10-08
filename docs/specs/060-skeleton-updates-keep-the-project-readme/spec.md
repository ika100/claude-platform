---
spec_id: 060-skeleton-updates-keep-the-project-readme
title: Skeleton updates keep the project README
status: approved
priority: P1
---

# 060 — Skeleton updates keep the project README

## Problem

Updating ika100/todo-api from platform 3.2.0 to 4.0.0 with `/shared:update-service` (2026-10-08) replaced its `README.md` with the template's version: the API, Testing and `DATABASE_URL` sections that the build had written were dropped. All six templates treat `README.md` as a skeleton file (none lists it in `_skip_if_exists`), so every repo that takes a platform update loses its README the same way; the update only lists it among "MODIFIED skeleton files" for the user to notice and restore by hand. This blocks rolling v4.0.0 out to existing repos.

## Stories

As a contributor, I want a platform update to leave my repo's README alone, so that the documentation my team and the agents wrote survives every update.

## Acceptance criteria

- **AC-060.1** Given a repo whose `README.md` differs from the template's, when `/shared:update-service` runs, then `README.md` is unchanged and not listed among the modified skeleton files.
- **AC-060.2** Given a new repo of any shape, when `/shared:new-service` or `/shared:new-app` creates it, then it still gets the template's README as its starting point.
- **AC-060.3** Given the templates, when `shapes.py check` runs, then a template that does not treat `README.md` as project-owned fails the check.
- **AC-060.4** Given an update in which the template's README changed since the repo's platform version, when `/shared:update-service` runs, then its report says the README was kept and prints the command that shows the template's current version.

## Non-goals

- Merging README changes from the template into a project's README automatically.

## Open questions

- ~~Should `README.md` be fully project-owned (seeded at creation, never updated), or should the platform keep a managed block between markers that updates while the rest stays the project's? (suggested: fully project-owned — platform-specific guidance already lives in `CLAUDE.md` and the docs; affects AC-060.1 and AC-060.4)~~ Answered: fully project-owned: README.md in _skip_if_exists of every template; the update report points to the template's version.

## References

- Found while updating todo-api to v4.0.0: [ika100/todo-api#3](https://github.com/ika100/todo-api/pull/3) (README restored by hand in its second commit).

## Changelog

- 2026-10-08 created from the todo-api update to 4.0.0
- 2026-10-08 open question answered: fully project-owned: README.md in _skip_if_exists of every template; the update report points to the template's version.
- 2026-10-08 approved
