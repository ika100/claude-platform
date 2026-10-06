---
description: Promotes one or more services across environments (e.g. dev→staging→prod). Works in the platform GitOps repo and in gitops-app repos (also from a service repo via .platform-app.yml). Opens one PR pinning image tags and kustomize refs; Argo reconciles after merge. Usage: /gitops:promote <service> [<service>...] <from> <to> [version]
---

You are the **promotion orchestrator**. Drive an environment promotion through pre-flight checks, manifest dry-run, branch+PR creation. Argo handles reconciliation after merge.

**Arguments:** $ARGUMENTS

Expected format: `<service> [<service>...] <from-env> <to-env> [version]` (a trailing semver-looking token is `version`; `--all` instead of services means every service in `services.yaml`; `version` is only valid with a single service). Examples:
- `payments-api staging prod` — promote latest staging tag to prod
- `payments-api staging prod v1.4.2` — pin to a specific version

If `$ARGUMENTS` is empty or malformed, print usage and stop.

---

## Phase 0 — Resolve the target repo and mode

Resolve the shape of the current directory: run this in one Bash call: `P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" shape` and read `shape` from the JSON:

- **`gitops-app`** → **app mode**, operate here.
- **Not `gitops-app` but `.platform-app.yml` exists** (a service repo that belongs to an app, [ADR-014](../../../docs/adr/014-gitops-app-composition-spec.md)) → read `gitops_apps`. If it lists several, ask the user which one (free-form text, once). Clone it next to the work: `gh repo clone <org>/<repo> "$(mktemp -d)/gitops-app"`, `cd` into the clone, and run every later phase there. Tell the user the clone path in the final report.
- **Otherwise** → **platform mode**: the existing platform GitOps repo flow below (`overrides/<service>/<env>/kustomization.yaml`).

In **app mode** the pins live in `applications/<app>/overlays/<env>/<service>/kustomization.yaml` (both the `?ref=` of the remote base and `images[].newTag` change together). Every named service must be in `applications/<app>/services.yaml`. `--all` expands to that list. Version rules in app mode:
- `dev→staging`: the newest commit of the service's `main` that has a built image. Pin the **full commit SHA** as `?ref=` and `sha-<first 7 chars>` as `newTag` (a `sha-…` string is not a git ref).
- `staging→prod`: a release `vX.Y.Z` — the explicit `version`, else the newest `v*` release tag of the service repo whose image exists. `?ref=vX.Y.Z` but `newTag: X.Y.Z` (CI publishes semver images without the `v`).
- Target `dev` is not promotable (it tracks `main`).

After editing, **app mode** runs `devbox run render-check` (the pins survive re-rendering) and `devbox run validate` instead of `deploy-check`. Replace `overrides/<SERVICE>/<TO_ENV>/kustomization.yaml` with the overlay paths above wherever it appears below. One PR per invocation covers all listed services; branch `promote/<services-or-all>-<TO_ENV>-<version-or-shas>`.

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

3. Service exists: in platform mode confirm `overrides/<SERVICE>/` or matching ApplicationSet entry; in app mode confirm each service is in `services.yaml`. If neither exists, stop and ask the user to create the initial overlay structure first.

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
- **One invocation, one promotion PR.** All services named in a single invocation (or `--all`) go into one PR; separate invocations never share a PR.
- **Stop on dry-run failures.** A broken kustomization shouldn't reach Argo.
