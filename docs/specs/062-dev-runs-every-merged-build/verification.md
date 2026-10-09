# Verification — 062-dev-runs-every-merged-build dev runs every merged build

**Result:** pass (live GitHub check pending, see notes)
**Commit:** 7abca37 · **Base:** dadb0f5 · **Trace:** 6/6 criteria named by tests · **Suite:** `tests/cplat` green (493 passed, 3 skipped; `devbox run ci-local` OK)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-062.1 | met | `tests/cplat/test_gitops.py`, `tests/cplat/test_spec_driven.py` | service templates' `pin-dev` job; gitops-app `.github/workflows/pin-dev.yml` | **structure only:** the GitHub side (dispatch → PR → `workflow_dispatch` CI → auto-merge) and the 10-minute bound are checked live in the next end-to-end run |
| AC-062.2 | met | `tests/cplat/test_gitops.py` | gitops-app `scripts/pin.py` (immutable tags only); render.py keeps the pin |  |
| AC-062.3 | met | `tests/cplat/test_gitops.py` | scripts/cplat/status.py `pin_prs` + `pin PR` column; tag and Argo health per row |  |
| AC-062.4 | met | `tests/cplat/test_newsvc.py`, `tests/cplat/test_newapp.py`, `tests/cplat/test_spec_driven.py`, `tests/cplat/test_update_doctor.py` | newsvc `pin_settings_cmds`, `token_step`; newapp one loop for all components; update `pin_dev_steps`; shapes.py requires the job |  |
| AC-062.5 | met | `tests/cplat/test_spec_agents.py` | ADR-027; HOW-IT-WORKS, USER-JOURNEY, gitops-app CLAUDE.md, /app:build, /gitops:promote, deployment agents |  |
| AC-062.6 | met | `tests/cplat/test_gitops.py` | pin lands only through `gh pr merge --auto`; no push to main, no `--admin` | live check in the next end-to-end run |

## Non-goals

Respected (see spec).

## Notes and deviations

- Result is **pass with a live check pending**: whether check runs started by `workflow_dispatch` satisfy branch protection for a PR opened by `GITHUB_TOKEN`, and the time to `dev`, depend on GitHub. ADR-027 and design.md name this; the next end-to-end run on ika100/todo verifies AC-062.1 and AC-062.6.
- Real evidence: `update-service` on a clone of ika100/todo-web brought the job and printed `gh secret set GITOPS_TOKEN -R ika100/todo-web` with the token link for ika100/todo.
- Addition beyond the plan: the gitops-app gets a `devbox run pin` recipe for pinning by hand.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
