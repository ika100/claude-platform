# Adopting the platform

How to bring a repo onto the `ika100/claude-platform` marketplace, whether it's a brand-new repo or an existing one.

---

## New repo (happy path)

From any directory:

```
/shared:new-service payments-api --description "Stripe webhooks → Postgres"
```

That single command runs `copier copy` against the `service-python` template, creates a private GitHub repo, tags it for ArgoCD auto-discovery, and pushes the initial commit. You're done.

For a library (no Docker, no k8s, no GitOps):

```
/shared:new-service shared-models Pydantic models reused across services --library
```

Other shapes (see `shapes.yml`): `--web` (`web-nextjs`), `--gitops` (`gitops-app`), `--type service-java`, `--type service-go`. A service that belongs to a product can record its application repo with `--app <org>/<gitops-app-repo>` (writes `.platform-app.yml`, used by `/gitops:promote`).

---

## Existing repo (migration)

Use this path when you have a working repo and want to swap its in-tree `.claude/agents/` and `.claude/commands/` for the marketplace plugins.

### Step 1 — Add the marketplace reference

Edit `.claude/settings.json` to add the marketplace and enable the plugins:

```json
{
  "extraKnownMarketplaces": {
    "ika100-claude": {
      "source": { "source": "github", "repo": "ika100/claude-platform", "ref": "main" }
    }
  },
  "enabledPlugins": {
    "svc@ika100-claude": true,
    "shared@ika100-claude": true
  }
}
```

Keep your existing `permissions` block as-is.

### Step 2 — Remove the now-duplicate in-tree definitions

```bash
git rm -r .claude/agents/ .claude/commands/ .claude/AGENTS.md
git commit -m "chore(agents): adopt ika100-claude marketplace, drop in-tree definitions"
```

### Step 3 — Drop the SessionStart hook from settings

The `svc` plugin ships its own SessionStart hook (`devbox run -- uv sync --all-extras`). Remove the equivalent hook from your `.claude/settings.json` to avoid duplicate runs.

### Step 4 — Smoke test

```
/svc:check-quality       # should run quality + security against your code
/svc:quick-task          # try a trivial change to confirm the full loop works
```

Both commands should now route through the marketplace plugins.

### Step 5 (optional) — Adopt Copier for skeleton updates

If you also want skeleton updates (CI workflow, devbox recipes) to flow from the template:

1. Create `.copier-answers.yml` at the repo root recording the answers your repo *would* have given to Copier:

   ```yaml
   _commit: <a recent platform tag like v0.1.0>
   _src_path: gh:ika100/claude-platform/templates/service-python
   project_name: <your-repo-name>
   module_name: <your_python_module>
   description: <one-liner>
   github_org: <your-org>
   owner_team: <your-team>
   python_version: "3.12"
   port: 8080
   needs_migrations: <true/false>
   needs_database: <none|postgres|mysql>
   needs_observability: <true/false>
   docker_registry: ghcr.io/<your-org>
   platform_marketplace_ref: main
   ```

2. Run `copier update --skip-answered` — it will reconcile your repo against the template, opening conflicts for files you've customised.

3. Review the diff carefully. For files the template considers "always re-templated" (`devbox.json`, CI workflow, `.claude/settings.json`) the template version wins. For project-owned files (`src/`, `tests/`, `pyproject.toml`) the template won't touch your version.

4. Commit the resulting tree.

---

## Migrating a web repo (Next.js)

1. Enable `web`, `svc` and `shared` in `.claude/settings.json` (marketplace reference as in Step 1).
2. Make the repo conform to the recipe contract: add a `devbox.json` with `install`, `dev`, `test`, `test-fast`, `lint`, `lint-fix`, `typecheck`, `quality`, `audit`, `security`, `image-build`, `image-scan`, `deploy-check` wrapping your `pnpm` scripts (`templates/web-nextjs/devbox.json.jinja` is the reference). Agents never call `pnpm`/`npx` directly.
3. App Router only: if the app still uses `pages/`, migrate or keep it out of agent-driven work (ADR-004). Pin Node and the `packageManager` field (ADR-003/005).
4. Add `k8s/base` (Deployment with `/api/health` + `/api/ready`, Service) and tag the repo `deployable-service`.
5. Write `.copier-answers.yml` (Step 5 below, template `templates/web-nextjs`) so shape detection does not rely on sniffing (`next.config.*` / `"next"` in `package.json`).

## Migrating a gitops-app repo

For an existing product GitOps repo (Kustomize + Argo):

1. Enable `gitops`, `app`, `svc` and `shared`.
2. Restructure to `applications/<app>/{services.yaml,applicationset.yaml,overlays/<env>/<service>/}` (ADR-014): put every component service in `services.yaml`, copy `scripts/render.py` and `scripts/plan.py` plus the `devbox.json` recipes from `templates/gitops-app`, run `devbox run render`, and review that the generated overlays reproduce your current pins (render preserves existing `newTag`/`?ref=` values).
3. Write `.copier-answers.yml` with `_src_path` ending in `templates/gitops-app` (or rely on the `applications/*/applicationset.yaml` sniff).
4. In each service repo add `.platform-app.yml` (`gitops_apps: [<org>/<repo>]`) so `/gitops:promote` works from there.

The same applies to Java (`service-java`) and Go (`service-go`) repos: provide the canonical devbox recipes, enable `svc-java`/`svc-go` + `svc` + `shared`, write `.copier-answers.yml`.

## What you get after adoption

- Slash commands: `/svc:plan-feature`, `/svc:build-feature`, `/svc:quick-task`, `/svc:fix-bug`, `/svc:release`, `/shared:check-quality`, `/shared:new-service`.
- Agents available by name: `product-manager`, `architect`, `coder`, `tester`, `quality`, `security`, `migrations`, `observability`, `release`, `deployment`.
- A SessionStart hook that runs `devbox run -- uv sync --all-extras` whenever you start a Claude Code session.
- One source of truth: agent updates flow via `/plugin marketplace update`, skeleton updates flow via `copier update`. The two channels are independent.
