# Design — 045 Multi-repo builds handle the gitops-app entry

## Decisions

- **Operations are data on the gitops-app repo entry.** The planner writes them; `plan-check` validates them; `/app:build` executes them with cplat. No agent edits `services.yaml` by hand.
- **New `cplat compose set`.** `compose add` refuses existing services (`already in services.yaml`), but a feature usually wires services that already run. `set` merges `--env`, `--expose`, `--uses` into the existing entry and re-renders, with the same validation as `add`.

## Contract

```yaml
repos:
  - id: todo                      # the gitops-app repo itself
    shape: gitops-app
    summary: Publish todo-web, wire it to todo-api, add the postgres addon
    acs: [AC-001.1, AC-001.14]
    gitops:
      - {addon: postgres}                                   # cplat addon add postgres
      - {uses: postgres, service: todo-api}                 # cplat compose set todo-api --uses postgres
      - {expose: todo-web, host: todo-web}                  # cplat compose set todo-web --expose todo-web
      - {env: {TODO_API_URL: 'http://todo-api'}, service: todo-web}  # cplat compose set todo-web --env TODO_API_URL=…
    depends_on: []
    done: false
```

Allowed operation keys: `addon`, `uses` + `service`, `expose` (+ optional `host`), `env` + `service`. `service` must be in `services.yaml` or be another repo of the plan; `addon` must be a known addon (`cplat addon list`).

## Execution in /app:build

On branch `compose/<spec_id>` of the gitops-app repo itself (no worktree when the checkout is clean; otherwise a worktree removed afterwards): run the operations in order, `devbox run validate`, commit `feat(compose): <spec_id> — …`, push, PR or command (spec 051). The wave table marks it **merge first**.
