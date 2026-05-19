---
description: Promotes a service version across environments (e.g. staging→prod). Opens a PR pinning the image tag and kustomize ref. Argo reconciles after merge. Usage: /gitops:promote <service> <from> <to> [version]
---

You are the **promotion orchestrator**. Drive an environment promotion through pre-flight checks, manifest dry-run, branch+PR creation. Argo handles reconciliation after merge.

**Arguments:** $ARGUMENTS

Expected format: `<service> <from-env> <to-env> [version]`. Examples:
- `payments-api staging prod` — promote latest staging tag to prod
- `payments-api staging prod v1.4.2` — pin to a specific version

If `$ARGUMENTS` is empty or malformed, print usage and stop.

---

## Phase 1 — Pre-flight

1. Working tree clean:
   ```bash
   git status --porcelain
   ```
   Stop if dirty.

2. On a clean main:
   ```bash
   git checkout main
   git fetch origin
   git merge --ff-only origin/main
   ```

3. Service exists: confirm `overrides/<SERVICE>/` or matching ApplicationSet entry. If neither exists, stop and ask the user to create the initial overlay structure first.

---

## Phase 2 — Resolve source version

Delegate to the **promote** agent (from this plugin) with the parsed arguments. It will:

- Determine the current version in `<FROM_ENV>` (or use the explicit `[version]` argument)
- Verify the GHCR image tag exists
- Compute the target kustomization changes for `<TO_ENV>`

Wait for the promote agent to report the resolved `VERSION`.

If the promote agent cannot resolve a version (e.g. the source env has no overlay yet), stop and report.

---

## Phase 3 — Dry-run

Run:

```bash
devbox run deploy-check
```

This must produce no errors. If it does, stop — the kustomization is broken.

For **prod** promotions, also print an explicit gate message:

```
## ABOUT TO PROMOTE TO PRODUCTION
Service: <SERVICE>
Version: <VERSION>
Source: <FROM_ENV>
Target: <TO_ENV> (PRODUCTION)

Dry-run clean. The next step opens a PR — review before approving.
```

---

## Phase 4 — Branch + commit + PR

The promote agent already prepared the kustomization edits. Now:

```bash
git checkout -b promote/<SERVICE>-<TO_ENV>-<VERSION>
git add overrides/<SERVICE>/<TO_ENV>/kustomization.yaml
git commit -m "chore(promote): <SERVICE> <FROM_ENV>→<TO_ENV> at <VERSION>"
git push -u origin promote/<SERVICE>-<TO_ENV>-<VERSION>
```

The PR (requires user confirmation):

```bash
gh pr create \
  --title "chore(promote): <SERVICE> <FROM_ENV>→<TO_ENV> at <VERSION>" \
  --body "Promotes <SERVICE> from <FROM_ENV> to <TO_ENV>, pinning version <VERSION>.

## Source

- Current <FROM_ENV> version: <VERSION>
- GHCR tag verified: ghcr.io/<ORG>/<SERVICE>:<VERSION>

## Target

- Updates overrides/<SERVICE>/<TO_ENV>/kustomization.yaml
- Argo will reconcile <TO_ENV> within ~3 min after merge

## Checks

- [x] devbox run deploy-check passed
- [x] Source image exists in GHCR
- [ ] Smoke tests on <TO_ENV> after rollout"
```

---

## Phase 5 — Final report

```
## Promotion PR opened

| Field | Value |
|---|---|
| Service | <SERVICE> |
| Source | <FROM_ENV> at <VERSION> |
| Target | <TO_ENV> |
| PR | <URL> |

Next: review and merge. Argo reconciles <TO_ENV> within ~3 min.

To roll back: revert the merged PR and Argo will reconcile back.
```

---

## Rules

- **Never auto-merge.** Promotions are intentional — humans approve.
- **Never `kubectl apply` directly.** Argo owns reconciliation.
- **Prod requires the explicit gate message** (Phase 3) — never skip it.
- **One service, one promotion PR.** Don't batch multiple services into one PR.
- **Stop on dry-run failures.** A broken kustomization shouldn't reach Argo.
