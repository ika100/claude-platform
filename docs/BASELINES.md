# Baselines (v1.1.1) — what v2 is measured against

Measured on the todo end-to-end run (2026-10-06/07, Apple silicon laptop, GitHub-hosted runners). Re-measure after each v2 phase and update the right-hand column.

## Prompt/token footprint (static)

| Item | v1.1.1 | v2 target |
|---|---|---|
| Always-on tokens, all 7 plugins | ~3.4k (svc 1,057; shared 511; web 503; svc-java 518; gitops 457; app 373) | ≤ 3.4k |
| `/shared:new-service` prompt (on invoke) | 11.3 KB (~3k tokens) | < 2 KB |
| `/shared:update-service` prompt | 4.8 KB | < 1.5 KB |
| `/gitops:promote` command + agent | 6.0 KB + 5.2 KB | < 2 KB total |
| `/svc:build-feature` prompt | 14.1 KB (~5.5k tokens) | unchanged in A–F (see Phase G) |
| Prompt files in `plugins/` | 178 KB | tracked |

## Time

| Step | v1.1.1 | v2 target |
|---|---|---|
| Web image build, multi-arch via QEMU | ≈ 9 min | ≈ 3 min (native arm64 runner) |
| Java image build (multi-arch, native builder stage) | ≈ 3 min | ≤ 3 min |
| Generated CI job (quality/test/security) | 2–3 min each | −30 s (leaner devbox) |
| `devbox run cluster-up` from scratch | ≈ 2.5 min | ≈ 2.5 min incl. Gateway API |
| Platform CI (PR) | 3–4 min | ≤ 4 min incl. unit + e2e smoke |

## Defect history

12 defects were found only by running the real chain (see `CHANGELOG.md` [1.1.1]); v2 adds a regression test or contract check for each.
