# ika100/claude-platform

Reusable Claude Code agents, slash commands, and Copier templates for the **ika100** services fleet.

## What's here

```
.
├── .claude-plugin/marketplace.json    Claude Code marketplace catalog
├── plugins/
│   ├── svc/                           Orchestrators (/svc:*), PM, architect + Python agents
│   ├── web/                           Next.js agents (coder, tester, deployment, observability, release)
│   ├── svc-java/                      Spring Boot agents
│   ├── svc-go/                        Go agents
│   ├── gitops/                        Platform GitOps + gitops-app agents (deployment, promote, compose)
│   ├── app/                           Multi-repo planner (/app:build-feature, /app:plans)
│   └── shared/                        Quality, security, /new-service
├── shapes.yml                         Shape registry (single source of truth)
├── templates/
│   ├── service-python/                Python service
│   ├── library-python/                Python library (no Docker)
│   ├── web-nextjs/                    Next.js App Router web app
│   ├── gitops-app/                    Product-scoped GitOps repo: owns all manifests (ADR-017)
│   ├── service-java/                  Spring Boot 3 / JDK 21 service
│   └── service-go/                    Go (chi) service
├── scripts/                           detect-shape.sh, shapes.py, tests
└── docs/
    ├── USER-JOURNEY.md                End-to-end walk-through (start here to explain the setup)
    ├── AGENTS.md                      Orchestration model
    ├── ADOPTING.md                    How to bring an existing repo onto the platform
    ├── ARCHITECTURE.md                Why the platform looks the way it does
    ├── templates.md                   How to add a new shape
    ├── requirements/                  Platform vision PRD
    └── adr/                           Architecture decision records
```

## Install in a new repo

```
/shared:new-service payments-api Stripe webhooks to Postgres            # service-python (default)
/shared:new-service my-saas-web  Marketing site and app --web           # web-nextjs
/shared:new-service my-saas      GitOps for my-saas --gitops            # gitops-app
/shared:new-service billing      Billing service --type service-java    # or service-go, library-python
```

`/shared:new-service` resolves the shape from `shapes.yml` and:

1. Runs `copier copy` from `templates/<shape>`
2. `git init` + commit
3. `gh repo create --private` under your GitHub account
4. `gh repo edit --add-topic deployable-service` (deployable shapes only) so ArgoCD discovers it

See `docs/requirements/platform-vision.md` §7 for the end-to-end product flow (`--gitops` repo → services → `/gitops:compose` → `/gitops:promote`).

## Install in an existing repo

```
/plugin marketplace add ika100/claude-platform
/plugin install svc@ika100-claude        # + web / svc-java / svc-go / gitops / app as your shapes need
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
| `/svc:build-feature <desc>` | svc | Full pipeline: PM → architect → parallel coders → quality → tester → security → deployment → PR (shape-aware; `--from-plan` for multi-repo plans) |
| `/svc:quick-task <desc>` | svc | Lightweight: coder → quality → tester → PR |
| `/svc:fix-bug <desc>` | svc | Diagnose → fix → regression test → PR |
| `/svc:release` | svc | Quality gate → test gate → security gate → version bump → tag → close issues |
| `/gitops:promote <svc...> <from> <to> [version]` | gitops | Pin service versions in an environment overlay (platform or gitops-app repo), open one PR |
| `/gitops:compose add\|remove <svc...>` | gitops | gitops-app repos: declare which services make up the application |
| `/app:build-feature <desc>` | app | gitops-app repos: plan a feature across repos (plan-only), topo-sorted |
| `/app:plans [list\|show\|start\|done\|abandon]` | app | Multi-repo plan lifecycle |
| `/shared:check-quality` | shared | Read-only quality + security audit |
| `/shared:update-service [--ref <tag>]` | shared | Pull the latest skeleton (CI, devbox, Dockerfile, CLAUDE.md…) into an existing repo on a review branch |
| `/shared:new-service <name>` | shared | Bootstrap a new repo of any registered shape (`shapes.yml`; default `service-python`, `--type <shape>` to choose) |

## Updates

- **Agent / command changes:** bump the version in `plugins/<name>/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`, tag, and push. Consumers run `/plugin marketplace update`.
- **Template changes:** edit `templates/<shape>/`, commit, tag. Consumers run `/shared:update-service` (optionally `--ref <tag>`) in their repo: it re-applies the template on a review branch and leaves project-owned files alone.

These two channels are independent — you can ship new agents without forcing all repos to run `/shared:update-service`, and vice versa.

## License

Apache-2.0
