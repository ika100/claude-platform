# ika100/claude-platform

Reusable Claude Code agents, slash commands, and Copier templates for the **ika100** services fleet.

## What's here

```
.
├── .claude-plugin/marketplace.json    Claude Code marketplace catalog
├── plugins/
│   ├── svc/                           Python service repos (8 agents, 5 commands)
│   ├── gitops/                        GitOps repo (2 agents, 1 command)
│   └── shared/                        Quality, security, /new-service (2 agents, 2 commands)
├── templates/
│   ├── service-python/                Copier template — full Python service skeleton
│   └── library-python/                Copier template — Python library skeleton (no k8s/Docker)
└── docs/
    ├── AGENTS.md                      Orchestration model (read first)
    ├── ADOPTING.md                    How to bring an existing repo onto the platform
    └── ARCHITECTURE.md                Why the platform looks the way it does
```

## Install in a new repo

```
/shared:new-service payments-api --description "Stripe webhooks → Postgres"
```

This runs the `shared` plugin's `/new-service` command which:

1. Asks for project name, description, etc.
2. Runs `copier copy` from `templates/service-python`
3. `git init` + commit
4. `gh repo create --private` under your GitHub account
5. `gh repo edit --add-topic deployable-service` so the GitOps repo's ArgoCD ApplicationSet auto-discovers it

## Install in an existing repo

```
/plugin marketplace add ika100/claude-platform
/plugin install svc@ika100-claude
/plugin install shared@ika100-claude
```

…or pre-wire it by adding to `.claude/settings.json`:

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

See `docs/ADOPTING.md` for the full migration guide.

## Slash commands

| Command | Plugin | Purpose |
|---|---|---|
| `/svc:plan-feature <desc>` | svc | PM + architect only — produce plan & ADR, no code |
| `/svc:build-feature <desc>` | svc | Full pipeline: PM → architect → parallel coders → quality → tester → security → deployment → PR |
| `/svc:quick-task <desc>` | svc | Lightweight: coder → quality → tester → PR |
| `/svc:fix-bug <desc>` | svc | Diagnose → fix → regression test → PR |
| `/svc:release` | svc | Quality gate → test gate → security gate → version bump → tag → close issues |
| `/gitops:promote <svc> <from> <to> [version]` | gitops | Pin a service version in an environment overlay, open PR |
| `/shared:check-quality` | shared | Read-only quality + security audit |
| `/shared:new-service <name>` | shared | Bootstrap a new repo from the service-python or library-python Copier template |

## Updates

- **Agent / command changes:** bump the version in `plugins/<name>/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`, tag, and push. Consumers run `/plugin marketplace update`.
- **Template changes:** edit `templates/service-python/` or `templates/library-python/`, commit, tag. Consumers run `copier update` in their repo to pull the diff.

These two channels are independent — you can ship new agents without forcing all repos to re-run `copier update`, and vice versa.

## License

Apache-2.0
