# Acceptance tests

Acceptance tests turn the criteria into executable checks. They are written **from the approved spec, before the code**, and they are the coders' definition of done.

## Naming the criterion

Every acceptance test names the criterion it proves, in its name or a comment on the test. `cplat spec trace` searches the shape's `test_globs` (from `shapes.yml`) for the id; `AC-007.1` never matches `AC-007.10`.

| Shape | Idiom |
|---|---|
| service-python, library-python | `def test_alert_email_on_cross():  # AC-007.1` |
| web-nextjs | `it("AC-007.1 sends an email when the price crosses", …)` |
| service-java | `@DisplayName("AC-007.1 sends an email when the price crosses")` |
| service-go | `t.Run("AC-007.1 sends an email when the price crosses", …)` or `// AC-007.1` above the test |

One test may name several criteria; one criterion may need several tests (happy path and the error cases it describes).

## Red first

- Write the tests against the **contract** (`design.md`) and the public surface the criteria describe, not against internals that do not exist yet.
- Run `devbox run test-fast`. Every new acceptance test must **fail because the behaviour is missing**: an assertion failure, a 404 for the not-yet-existing route, or an import of the not-yet-existing module. A test that fails for another reason (syntax error, broken fixture) is a broken test; fix it.
- A test that already passes proves nothing about the new feature: tighten it or report that the criterion is already met.
- Commit them as one commit: `test(<slug>): acceptance tests for AC-007.1–AC-007.4`.

## After that

- Coders make these tests pass and never edit, skip or weaken them. Formatting through `devbox run lint-fix` is fine: the build checks every change with `cplat spec test-diff <red commit>` (same parsed code for Python, same text without whitespace for other languages, same criterion ids) and stops on anything else. If a test contradicts the spec or the contract, the coder stops and reports it; the orchestrator decides (and records the change in the spec's Changelog if the spec was wrong).
- Unit and integration tests for internals are added later as usual; they do not need criterion ids.
