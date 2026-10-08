# Design — 048 Acceptance tests may be reformatted, never weakened

## `cplat spec test-diff <base> [files…]`

- **Files:** by default every test file (shape `test_globs`) that names a criterion of a `building` spec and changed since `<base>` (the Phase 1 commit).
- **Python:** `tokenize` both versions; drop `NL`, `NEWLINE`, `INDENT`, `DEDENT`, `ENCODING` and comments; sort each run of consecutive top-level `import`/`from` statements; compare the remaining `(type, string)` sequences. Equal → formatting only. Comments are ignored except criterion ids: the set of `AC-<NNN>.<n>` mentioned anywhere must be identical.
- **Other languages:** remove all whitespace and compare the strings; the set of criterion ids must be identical.
- **Output:** one line per file, `formatting only` or `changed: <first differing token, line>`; exit 1 when any file changed.

## Why not the formatters

Running each shape's formatter needs its toolchain (pnpm, mvn, go) inside cplat; tokens and whitespace are enough to tell reflow from a changed assertion.
