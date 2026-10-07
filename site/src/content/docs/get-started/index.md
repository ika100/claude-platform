---
title: "Your first product"
description: "Install the plugins, check your setup and create a first product in about fifteen minutes."
---

<p class="lead">You need Claude Code, a GitHub account and a few tools. Everything else is created for you.</p>

## 1. Prerequisites

| Tool | Why | Check |
|---|---|---|
| [Claude Code](https://claude.com/claude-code) | runs the agents and slash commands | `claude --version` |
| `git` and [`gh`](https://cli.github.com), logged in | creates repositories, pull requests, reads image tags | `gh auth status` (scopes `repo`, `workflow`; add `read:packages` for local clusters: `gh auth refresh -s read:packages`) |
| [`uv`](https://docs.astral.sh/uv/) | runs the tested `cplat` CLI | `uv --version` |
| [`devbox`](https://www.jetify.com/devbox) | every recipe (`quality`, `test`, `cluster-up`) runs through it | `devbox version` |
| Docker | image builds and the local cluster | `docker info` |

`k3d`, `kubectl` and the other cluster tools come with the GitOps repository's own `devbox` environment; you do not install them separately.

## 2. Install the plugins

In Claude Code:

```text
/plugin marketplace add ika100/claude-platform
/plugin install shared@ika100-claude
/plugin install svc@ika100-claude
/plugin install gitops@ika100-claude
```

Add `web`, `svc-java`, `svc-go` and `app` for the shapes you use. After installing or updating plugins, **restart Claude Code**: a running session keeps the old prompts.

## 3. Check your setup

```text
/shared:doctor
```

It checks the tools above, `gh` scopes, Docker, your kube context (and warns when it is not local), plugin versions and the platform version of the current repository, and prints a concrete fix for every problem.

## 4. Create the product

```text
/shared:new-service shop Product GitOps repo --gitops
/shared:new-service shop-api Catalog and orders API --type service-java
/shared:new-service shop-web Storefront --web
```

Each command shows what it will do and asks before anything outward-facing (creating the GitHub repository, pushing). The default shape is `service-python`; `--type` picks any registered [shape](/claude-platform/reference/shapes/).

## 5. Build, compose, run

1. In a service repository: `/svc:build-feature <what you want>` (or `/svc:quick-task` for a small change). See [Build a feature](/claude-platform/scenarios/build-a-feature/).
2. When CI has published the first image: `/gitops:compose add shop-api` in the GitOps repository, then merge the pull request.
3. [Run it on your laptop](/claude-platform/get-started/local-cluster/).

## Where to go next

- The whole story with every command: [User journey](/claude-platform/guides/user-journey/).
- Concepts in five minutes: [Concepts](/claude-platform/concepts/).
- Something broke: [Troubleshooting](/claude-platform/guides/adopting/#troubleshooting) or `/shared:report-issue`.
