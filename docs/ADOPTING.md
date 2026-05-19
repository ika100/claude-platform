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
/shared:new-service shared-models --description "Pydantic models reused across services" --library
```

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

## What you get after adoption

- Slash commands: `/svc:plan-feature`, `/svc:build-feature`, `/svc:quick-task`, `/svc:fix-bug`, `/svc:release`, `/shared:check-quality`, `/shared:new-service`.
- Agents available by name: `product-manager`, `architect`, `coder`, `tester`, `quality`, `security`, `migrations`, `observability`, `release`, `deployment`.
- A SessionStart hook that runs `devbox run -- uv sync --all-extras` whenever you start a Claude Code session.
- One source of truth: agent updates flow via `/plugin marketplace update`, skeleton updates flow via `copier update`. The two channels are independent.
