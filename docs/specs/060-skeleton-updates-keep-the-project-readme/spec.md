---
spec_id: 060-skeleton-updates-keep-the-project-readme
title: Skeleton updates keep the project README and devbox recipes
status: done
priority: P1
---

# 060 — Skeleton updates keep the project README and devbox recipes

## Problem

Updating ika100/todo-api from platform 3.2.0 to 4.0.0 with `/shared:update-service` (2026-10-08) replaced its `README.md` with the template's version: the API, Testing and `DATABASE_URL` sections that the build had written were dropped. All six templates treat `README.md` as a skeleton file (none lists it in `_skip_if_exists`), so every repo that takes a platform update loses its README the same way; the update only lists it among "MODIFIED skeleton files" for the user to notice and restore by hand. The same update removed project recipes from `devbox.json`: in end-to-end run 2 (2026-10-08) todo-web lost its `bundle-check` recipe, the proof for AC-001.25, because `devbox.json` is overwritten as a whole although projects are told to add their own recipes to it. This blocks rolling v4.0.0 out to existing repos.

## Stories

As a contributor, I want a platform update to leave my repo's README alone, so that the documentation my team and the agents wrote survives every update.

As a contributor, I want the recipes I added to `devbox.json` to survive an update, while the platform's recipes still get updated.

## Acceptance criteria

- **AC-060.1** Given a repo whose `README.md` differs from the template's, when `/shared:update-service` runs, then `README.md` is unchanged and not listed among the modified skeleton files.
- **AC-060.2** Given a new repo of any shape, when `/shared:new-service` or `/shared:new-app` creates it, then it still gets the template's README as its starting point.
- **AC-060.3** Given the templates, when `shapes.py check` runs, then a template that does not treat `README.md` as project-owned fails the check.
- **AC-060.4** Given an update in which the template's README changed since the repo's platform version, when `/shared:update-service` runs, then its report says the README was kept and prints the command that shows the template's current version.
- **AC-060.5** Given a repo whose `devbox.json` has a script or package that the template does not define, when `/shared:update-service` runs, then that script or package is still in `devbox.json` afterwards.
- **AC-060.6** Given a script or package the template defines, when the template's version changed since the repo's platform version, then `/shared:update-service` updates it in `devbox.json`, also when the project had changed that entry (the template's version wins).
- **AC-060.7** Given an update that changed or kept anything in `devbox.json` other than taking the template's file, when it reports, then it lists the kept project entries and, for each template recipe it replaced, the project's old line.

## Non-goals

- Merging README changes from the template into a project's README automatically.
- Merging other JSON or YAML skeleton files; `devbox.json` is the one file projects are told to extend.

## Open questions

- ~~Should `README.md` be fully project-owned (seeded at creation, never updated), or should the platform keep a managed block between markers that updates while the rest stays the project's? (suggested: fully project-owned — platform-specific guidance already lives in `CLAUDE.md` and the docs; affects AC-060.1 and AC-060.4)~~ Answered: fully project-owned: README.md in _skip_if_exists of every template; the update report points to the template's version.

~~When the project changed a recipe that the template also defines (e.g. added a flag to `test`), whose version wins on update? (suggested: the template's, listed in the report with the project's old line, so platform fixes always arrive and nothing is lost silently; affects AC-060.6, AC-060.7)~~ Answered: the template's version wins; the report shows the project's old line.

## References

- Found while updating todo-api to v4.0.0: [ika100/todo-api#3](https://github.com/ika100/todo-api/pull/3) (README restored by hand in its second commit).
- [End-to-end run 2 log](../../e2e/2026-10-09-todo-second-feature.md), finding 2 (`devbox.json` recipes) and finding 16 (report line).

## Changelog

- 2026-10-08 created from the todo-api update to 4.0.0
- 2026-10-08 open question answered: fully project-owned: README.md in _skip_if_exists of every template; the update report points to the template's version.
- 2026-10-08 approved
- 2026-10-09 amended from end-to-end run 2: devbox.json project recipes survive updates (AC-060.5–7); back to draft for re-approval
- 2026-10-09 open question answered: the template's recipe wins on update; the report shows the project's old line
- 2026-10-09 approved
- 2026-10-09 building
- 2026-10-09 done
