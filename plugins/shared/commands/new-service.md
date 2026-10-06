---
description: "Bootstrap a new repo of any registered shape (see shapes.yml) from a Copier template, init git, create the GitHub repo, and tag it for GitOps. Usage: /shared:new-service <name> [description words...] [--type <shape>] [--library|--web|--gitops] [--python 3.12|3.13] [--app <org>/<gitops-app-repo>] [--org <org>] [--ref <git-ref>]"
---

You are the **bootstrap orchestrator** for new repos of any registered shape (`shapes.yml` in the platform repo is the registry). Goal: scaffold a repo end-to-end with as little user interaction as possible. Default to zero further questions once a project name is supplied.

**Request:** $ARGUMENTS

---

## Parsing rules

Treat `$ARGUMENTS` as one free-form line. Extract in this order:

1. **Flags** (consume wherever they appear, then strip from the stream):
   - `--type <shape>` → `SHAPE=<shape>` (any `id` in `shapes.yml`)
   - Aliases: `--library` → `SHAPE=library-python`, `--web` → `SHAPE=web-nextjs`, `--gitops` → `SHAPE=gitops-app`. If more than one of `--type`/aliases is given, stop and report the conflict.
   - No shape flag → `SHAPE=service-python` (backward-compatible default).
   - `--python <ver>` → `PYTHON_VERSION=<ver>` (only for `service-python` / `library-python`; if the flag is absent for those shapes set `PYTHON_VERSION=3.12`; for all other shapes leave it unset and ignore the flag)
   - `--app <org>/<repo>` → `GITOPS_APP=<org>/<repo>` (service shapes only: writes `.platform-app.yml` so `/gitops:promote` can find the application repo)
   - `--org <org>` → `GITHUB_ORG=<org>`
   - `--description "<text>"` → legacy alias, appended to the description stream
   - `--ref <git-ref>` → `PLATFORM_REF=<ref>` (default `main`)
2. **First remaining token** → `PROJECT_NAME`. Must match `^[a-z][a-z0-9-]{1,39}$`. If invalid, stop and report.
3. **All remaining tokens joined with single spaces** → `DESCRIPTION`.
4. Derived (Python shapes only): `MODULE_NAME = PROJECT_NAME.replace('-', '_')`.

**If `PROJECT_NAME` is missing OR `DESCRIPTION` is empty**, ask the user once via plain text — a single message like: *"Give me a project name (kebab-case) and a one-line description, on one line: `<name> <description>`."* Re-parse the reply and proceed. Do not loop more than once and do not use `AskUserQuestion` for this — free-form text input is faster.

**Never** ask the user to confirm resolved inputs. Print one compact line and proceed:

```
Bootstrapping <SHAPE> "<PROJECT_NAME>" (org: <GITHUB_ORG>[, module: <MODULE_NAME>, python: <PYTHON_VERSION>]) — "<DESCRIPTION>"
```

---

## Phase 1 — Preflight (silent unless something is missing)

| Tool | Required | If missing |
|---|---|---|
| `copier` | yes | `uv tool install copier` automatically (one-shot, one info line). If `uv` is also missing, stop with a clear error. |
| `git` | yes | Stop with error. |
| `gh` | no | Set `SKIP_GITHUB=1`, print one warning line. Phases 4–5 will be skipped and the exact commands will go into the final report. |
| `devbox` | no | Surface a note in the final report — does not block. |

Resolve `GITHUB_ORG` if still unset:
1. Try `gh api user -q .login` (skip if `gh` missing).
2. Fall back to `ika100` (the copier template default). No prompt.

**Target directory check** on `./<PROJECT_NAME>`:
- Doesn't exist → proceed.
- Exists, is empty, or contains only `.claude/` → remove it with one warning line and proceed.
- Anything else → stop and list contents.

---

## Phase 2 — Fetch platform, resolve shape, run Copier

Copier does not accept subdirectory paths in `gh:` URLs. Shallow-clone first, then resolve the shape from the registry in the clone and point Copier at the template subdir. **Run the clone/resolve snippet and the `copier copy` snippet below as one single Bash call** — `PLATFORM_DIR`, the shape variables and the cleanup `trap` live in that one shell.

```bash
PLATFORM_REF="${PLATFORM_REF:-main}"
PLATFORM_DIR=$(mktemp -d)
trap 'rm -rf "$PLATFORM_DIR"' EXIT
git clone --depth 1 --branch "$PLATFORM_REF" \
  https://github.com/ika100/claude-platform.git "$PLATFORM_DIR" 2>&1 | tail -2

# Resolve the shape from the registry (single source of truth: shapes.yml)
reg() { uv run "$PLATFORM_DIR/scripts/shapes.py" get "$SHAPE" "$1"; }
TEMPLATE=$(reg template) || { echo "Unknown shape '$SHAPE'. Valid: $(uv run "$PLATFORM_DIR/scripts/shapes.py" ids | tr '\n' ' ')"; exit 1; }
SHAPE_STATUS=$(reg status); DEPLOYABLE=$(reg deployable); SHAPE_PLUGIN=$(reg plugin)
[ -d "$PLATFORM_DIR/templates/$TEMPLATE" ] || { echo "Shape '$SHAPE' is registered (status: $SHAPE_STATUS) but templates/$TEMPLATE does not exist at ref $PLATFORM_REF yet."; exit 1; }
```

If the registry lookup or the template-directory check fails, stop and report the printed message — do not fall back to another shape.

Copier questions are shape-specific. Always pass `project_name`, `description`, `github_org`, `platform_marketplace_ref`; pass `module_name` and `python_version` **only** for `service-python` / `library-python` (in `service-go`, `module_name` is the Go module path and its default `github.com/<org>/<project>` must be kept). Any other question a template defines falls back to its `--defaults` value.

```bash
copier copy "$PLATFORM_DIR/templates/<TEMPLATE>" ./<PROJECT_NAME> \
  --defaults --trust \
  --data project_name=<PROJECT_NAME> \
  ${MODULE_NAME:+--data module_name=$MODULE_NAME} \
  --data description="<DESCRIPTION>" \
  --data github_org=<GITHUB_ORG> \
  ${PYTHON_VERSION:+--data python_version=$PYTHON_VERSION} \
  --data platform_marketplace_ref="$PLATFORM_REF"
```

`--trust` is required because the templates declare `_tasks`. The platform repo is your own trusted source.

If `copier` lives at `~/.local/bin/copier` and isn't on `PATH`, invoke it with the absolute path.

Surface any merge-conflict or skipped-file warnings in the final report.

---

## Phase 3 — Initialize git

Copier's `_tasks` runs `git init -q`, generates lockfiles (`devbox install` + `devbox run -- uv sync --all-extras`), and creates a bootstrap commit with a generic `bootstrap@ika100` identity. Rewrite that commit so the user owns it with a richer message:

```bash
cd <PROJECT_NAME>
# Determine commit identity: prefer existing git config, fall back to session.
GIT_NAME="$(git config user.name 2>/dev/null || true)"
GIT_EMAIL="$(git config user.email 2>/dev/null || true)"
[ -z "$GIT_NAME" ]  && GIT_NAME="claude-bootstrap"
[ -z "$GIT_EMAIL" ] && GIT_EMAIL="${userEmail:-claude-bootstrap@ika100.local}"

git -c user.name="$GIT_NAME" -c user.email="$GIT_EMAIL" \
  commit --amend --reset-author -q -m "chore: bootstrap from <TEMPLATE> template

Generated by /shared:new-service.
Template: ika100/claude-platform/templates/<TEMPLATE>
Description: <DESCRIPTION>"
```

Copier records the temporary clone path as `_src_path` in `.copier-answers.yml`. Replace it with the stable source (detection reads only the `templates/<shape>` tail, and `/shared:update-service` re-applies from the platform repo) and fold it into the same commit:

```bash
sed -i.bak "s#^_src_path:.*#_src_path: gh:ika100/claude-platform/templates/<TEMPLATE>#" .copier-answers.yml && rm -f .copier-answers.yml.bak
git add .copier-answers.yml && git -c user.name="$GIT_NAME" -c user.email="$GIT_EMAIL" commit --amend --no-edit -q
```

If for any reason copier didn't produce a commit (older template, `_tasks` failed silently), fall through to the legacy path:

```bash
if ! git rev-parse HEAD >/dev/null 2>&1; then
  git add -A
  git -c user.name="$GIT_NAME" -c user.email="$GIT_EMAIL" \
    commit -q -m "chore: bootstrap from <TEMPLATE> template

Generated by /shared:new-service.
Template: ika100/claude-platform/templates/<TEMPLATE>
Description: <DESCRIPTION>"
fi
```

Never fail the bootstrap on a missing git identity or a no-op amend.

If `GITOPS_APP` is set and `DEPLOYABLE=true`, add `.platform-app.yml` and amend the bootstrap commit ([ADR-014](../../../docs/adr/014-gitops-app-composition-spec.md)):

```bash
printf '# Application repos this service belongs to (read by /gitops:promote)\ngitops_apps:\n  - %s\n' "<GITOPS_APP>" > .platform-app.yml
git add .platform-app.yml && git -c user.name="$GIT_NAME" -c user.email="$GIT_EMAIL" commit --amend --no-edit -q
```

Ignore `--app` (with a one-line note) for shapes that are not deployable.

---

## Phase 4 — Create the GitHub repo (skip if `SKIP_GITHUB=1`)

```bash
gh repo create <GITHUB_ORG>/<PROJECT_NAME> \
  --private \
  --description "<DESCRIPTION>" \
  --source=. \
  --remote=origin \
  --push
```

If creation fails (e.g. repo already exists), surface the `gh` error and continue — do not unwind local state.

---

## Phase 5 — Tag for GitOps discovery (only when the registry says `deployable: true`; skip if `SKIP_GITHUB=1`)

```bash
gh repo edit <GITHUB_ORG>/<PROJECT_NAME> --add-topic deployable-service
```

This tells the ArgoCD ApplicationSet in the gitops repo to pick the service up on the next reconcile. Skip this step when `DEPLOYABLE=false` (libraries, `gitops-app`).

---

## Phase 6 — Final report

```
## <SHAPE> repo bootstrapped: <PROJECT_NAME>

| Item | Value |
|---|---|
| GitHub | https://github.com/<GITHUB_ORG>/<PROJECT_NAME>   (or: "skipped — see commands below") |
| Local path | <abs-path>/<PROJECT_NAME> |
| Topic | deployable-service (only if deployable; otherwise "none") |
| Argo discovery | ~3 min after the topic is applied |

### Next steps
1. `cd <PROJECT_NAME> && devbox shell` — enter the dev environment
2. `devbox run quality && devbox run test` — sanity-check the tree
3. `/svc:plan-feature <your first feature>` — start designing
```

For `gitops-app` repos replace the next steps with: (1) `cd <PROJECT_NAME> && devbox shell`, (2) `devbox run quality`, (3) **once per cluster, by a human:** `devbox run bootstrap` (creates the root Argo Application; Argo needs read access to the repos), (4) `/gitops:compose add <service>` to declare the first services, (5) `/gitops:promote <service> dev staging` once images exist. The `<PROJECT_NAME>` here is the GitOps repo name; the application name defaults to it minus a `-gitops` suffix.

If `SKIP_GITHUB=1`, append a fenced block with the exact `gh repo create` + (for deployable shapes) `gh repo edit --add-topic deployable-service` commands the user should run from inside `devbox shell` (which provisions `gh`).

If `devbox` was missing on the host, note that the user needs to install it (`brew install jetify-com/devbox/devbox`) before step 1 will work.

---

## Rules

- **Default to zero further questions** once a project name is in hand. Ask only when an input is *required* and *missing*. Never ask for confirmation of resolved inputs.
- **Auto-install `copier`; never auto-install `gh`.** `gh` requires interactive login; "skip GitHub steps and print commands" is a better fallback than aborting.
- **Never overwrite a non-empty target directory.** Empty / `.claude`-only stubs may be removed.
- **`deployable-service` topic follows the registry.** Only shapes with `deployable: true` in `shapes.yml` get it; libraries and `gitops-app` repos don't appear in the ApplicationSet.
- **Private by default.** Public release is a separate, explicit action.
- **One progress line per phase.** No verbose narration — the user reads the diff/output, not your prose.
