---
title: "Extend the platform"
description: "Add a new language shape, an addon or an agent through the documented contracts."
---

**Situation.** Your team uses Rust or Kotlin, or needs a Redis addon.

## A new shape

A shape is a registry entry plus a template plus a plugin:

1. Add the entry to `shapes.yml` (id, plugin, template, deployable, runtime defaults: port, probes, numeric user, volumes, resources, metrics path).
2. Create `templates/<shape>/` (a Copier template with the same `devbox` recipes as the other shapes: `quality`, `test`, `security`, image build).
3. Add a plugin with coder, tester, deployment, observability and release agents, or reuse an existing plugin.
4. Add a sniff rule to `scripts/detect-shape.sh`.
5. Run `uv run scripts/shapes.py check` (the contract: registry, templates, plugins and the requirements table agree) and add a smoke job.

Step-by-step with the contract: [Adding a new shape](/claude-platform/guides/add-a-shape/).

## A new addon

Addons are declared in `app.yaml` and implement a **connection contract** (the Secret and environment variables services receive). Add an entry to the `ADDONS` table in `templates/gitops-app/scripts/render.py` plus a manifest function, tests in `tests/cplat`, and an ADR. Services never learn the implementation, so it can later be swapped (a spike evaluated kro this way; see [ADR-020](/claude-platform/reference/adr/020/)).

## An agent or command

Write `plugins/<name>/agents/<agent>.md` or `commands/<command>.md` with front matter (`description` at most 260 characters because it is loaded into every session), bump the plugin version in `plugin.json` and the marketplace, and keep commands thin: they should run a tested script and relay its output.

## Contribute it back

Follow [Contributing](/claude-platform/community/contributing/): conventional commit titles, tests, a changelog line and an ADR for design changes. CI runs the registry contract, every template smoke test and the end-to-end test.
