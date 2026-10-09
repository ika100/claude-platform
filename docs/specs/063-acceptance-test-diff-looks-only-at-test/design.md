# Design — 063 Acceptance-test diff looks only at test files

## Default file selection

`test_diff(root, base, files)` in `scripts/cplat/spec.py` without explicit files now selects:

1. the files changed since `base` (`git diff --name-only base`);
2. ∩ files matching the repo shape's `test_globs` (`test_globs(repo_shape(root))`, the same globs `cplat spec trace` uses, with the default globs when no shape is recorded);
3. minus anything under `docs/` and any `*.md` file, always (AC-063.3; the default globs are broad, e.g. `tests/**/*`);
4. ∩ files that name a criterion of a `building` spec (as today).

Explicit files are checked as given, without filtering (unchanged).

This is what design 048 already said ("every test file (shape `test_globs`) that names a criterion"); the implementation skipped step 2.

## Agents (AC-063.4)

`/svc:build` already says to stop and show the user on exit 1. A contract test in `tests/cplat/test_spec_agents.py` pins that sentence, so an agent can no longer just "judge it a false alarm" without the command text changing first.
