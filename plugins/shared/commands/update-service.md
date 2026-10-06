---
description: Pull the latest skeleton (CI workflow, devbox recipes, Dockerfile, CLAUDE.md, k8s base, lint config) from the platform template into an existing repo, on a review branch. Also re-applies the template with changed answers. Usage: /shared:update-service [--ref <git-ref>] [--data key=value ...]
---

You are the **skeleton update orchestrator**. Bring a repo created from a platform template up to date with the current template, safely: on a branch, as one reviewable commit, never touching project-owned files.

**Arguments:** $ARGUMENTS

Why this command exists: `copier update` needs the template's git history, which repos bootstrapped by `/shared:new-service` do not have (the template lives in a subdirectory of the platform repo). This command re-applies the template with the repo's recorded answers instead; the review happens in the git diff.

---

## Parsing

- `--ref <git-ref>` → `PLATFORM_REF` (default `main`; use a release tag such as `v1.1.0` to pin).
- `--data key=value` (repeatable) → `EXTRA_DATA`, passed to Copier. Use it to change an answer, e.g. `--data needs_observability=true` or `--data needs_migrations=true`.

## Phase 1 — Preflight

1. The repo must be a git repo with a clean working tree (`git status --porcelain` empty); otherwise stop and say to commit or stash first.
2. Detect the shape per `plugins/shared/fragments/shape-detection.md`; it needs `.copier-answers.yml` at the repo root. If the file is missing, stop and point to `docs/ADOPTING.md` ("Adopt Copier for skeleton updates") — do not guess answers.
3. `copier` must be installed (`uv tool install copier` if `uv` exists; else stop). Locate it at `~/.local/bin/copier` if not on `PATH`.
4. Not on `main`/`master`: create the review branch `chore/platform-update-<YYYYMMDD>` (`git checkout -b …`). If already on a non-default branch, stay on it.

## Phase 2 — Re-apply the template

Run the snippet below as one single Bash call (the temp-dir cleanup `trap` and variables live in that shell), with `SHAPE`, `PLATFORM_REF` and `EXTRA_DATA` substituted from Phase 1.

```bash
PLATFORM_DIR=$(mktemp -d); trap 'rm -rf "$PLATFORM_DIR"' EXIT
git clone --depth 1 --branch "${PLATFORM_REF:-main}" https://github.com/ika100/claude-platform.git "$PLATFORM_DIR"
TEMPLATE=$(uv run "$PLATFORM_DIR/scripts/shapes.py" get "$SHAPE" template)

copier copy "$PLATFORM_DIR/templates/$TEMPLATE" . \
  --data-file .copier-answers.yml --overwrite --defaults --trust --skip-tasks \
  ${EXTRA_DATA}   # each as: --data key=value
```

- Recorded answers are reused; questions the template gained since get their defaults (tell the user which new answers took defaults — compare the old and new `.copier-answers.yml`).
- Files the template marks project-owned (`_skip_if_exists`: `k8s/base/deployment.yaml`, `src/`, `app/`, `cmd/`, `internal/`, `tests/`, `docs/adr/`, manifests like `pyproject.toml`/`pom.xml`/`go.mod`, …) are **not** overwritten. Skeleton files are overwritten — including any local customisation of them.
- Afterwards restore the stable source in the answers file so detection and future updates stay clean: set `_src_path` back to `gh:ika100/claude-platform/templates/<TEMPLATE>` (copier writes the temp clone path).

## Phase 3 — Review and commit

1. `git status --short` and `git diff --stat`. If nothing changed: print "Already up to date with <ref>" and stop (delete the branch if you created it and it is empty).
2. Summarise by group (CI workflow, devbox recipes, Dockerfile/k8s, CLAUDE.md, config, new files). For each **modified** skeleton file, list it explicitly with `git diff --stat` — those are the files where a local customisation could have been overwritten; tell the user to run `git diff <file>` on them and `git checkout -- <file>` to keep their version.
3. Run `devbox run quality` and `devbox run test-fast` if `devbox` is available. Report failures; do not fix them.
4. Commit once: `chore: update skeleton from platform <ref>` (Conventional Commits). Do not push, do not open a PR unless the user asks.

## Final report

```
## Skeleton updated: <repo> (<shape>) from platform <ref>
Branch: chore/platform-update-<date>   Files changed: N   (quality: PASS/FAIL, tests: PASS/FAIL)

Review these locally-customised skeleton files before merging: <list or "none">
New answers that took defaults: <list or "none">
Next: git push -u origin <branch> && open a PR (or `git checkout main && git branch -D <branch>` to discard).
```

## Rules

- Never run on a dirty tree; never commit to `main`.
- Never overwrite project-owned files; never run the template's `_tasks` (`--skip-tasks`).
- Never push or open a PR without being asked.
- Do not "fix" the diff by hand — the template is the source of truth; local customisations that should survive belong in project-owned files or an ADR.
