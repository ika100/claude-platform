#!/usr/bin/env python3
"""Keep the dependency pins inside the Copier templates current (issue #56, idea 2).

Dependabot cannot read `pom.xml.jinja`, `package.json.jinja` or `go.mod.jinja`, so new projects would start with old
versions and receive the update pull requests on day one. This script instead:

  1. renders each template with its defaults into a temporary directory,
  2. lets the real ecosystem tool bump the *rendered* manifest (minor/patch only; majors stay a human decision),
  3. copies every changed line back into the template source when that line is unambiguous (the line appears
     literally, exactly once, with no Jinja on it),
  4. re-renders the changed template and checks that it now equals the bumped manifest.

  bump_template_pins.py [TEMPLATE...]   default: every template listed in UPDATERS
  bump_template_pins.py --list          show what would be handled

Lines it cannot map back (Jinja on the line, or ambiguous) are reported, never guessed.
"""
from __future__ import annotations

import argparse
import difflib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "cplat"))

# template -> manifests (relative to the project root) and the commands that bump them there.
UPDATERS: dict[str, dict] = {
    "service-java": {
        "files": ["pom.xml"],
        "commands": [
            ["mvn", "-B", "-q", "versions:update-parent", "-DallowMajorUpdates=false", "-DgenerateBackupPoms=false"],
            ["mvn", "-B", "-q", "versions:update-properties", "-DallowMajorUpdates=false", "-DgenerateBackupPoms=false"],
        ],
    },
    "web-nextjs": {
        "files": ["package.json"],
        "commands": [["npx", "--yes", "npm-check-updates", "-u", "--target", "minor"]],
    },
    "service-go": {
        "files": ["go.mod", "go.sum"],
        "atomic": True,           # go.mod and go.sum belong together: apply both or neither
        "commands": [["go", "get", "-u", "./..."], ["go", "mod", "tidy"]],
    },
}
WHOLE_FILE = {"go.sum"}          # generated, no per-line mapping: copied as a whole when the source has no Jinja
JINJA = ("{{", "{%", "{#")


def source_of(template_dir: Path, rel: str) -> Path | None:
    for candidate in (template_dir / rel, template_dir / f"{rel}.jinja"):
        if candidate.is_file():
            return candidate
    return None


def copy_back(old: str, new: str, source: str) -> tuple[str, list[str]]:
    """Apply the line changes old->new (both rendered) to the template `source`. Returns (new source, skipped notes)."""
    skipped: list[str] = []
    lines = source.split("\n")
    old_lines, new_lines = old.split("\n"), new.split("\n")
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag != "replace" or (i2 - i1) != (j2 - j1):
            skipped.append(f"not a one-to-one line change: {' | '.join(old_lines[i1:i2])[:80]!r}")
            continue
        for before, after in zip(old_lines[i1:i2], new_lines[j1:j2]):
            hits = [n for n, line in enumerate(lines) if line == before]
            if len(hits) != 1 or any(t in before for t in JINJA):
                skipped.append(f"{before.strip()[:70]!r}: {'appears ' + str(len(hits)) + ' times in the template' if not any(t in before for t in JINJA) else 'contains Jinja'}")
                continue
            lines[hits[0]] = after
    return "\n".join(lines), skipped


def render(template_dir: Path, dest: Path, copier: list[str]) -> None:
    subprocess.run([*copier, "copy", str(template_dir), str(dest), "--defaults", "--trust", "--skip-tasks", "--data", "project_name=pin-probe"],
                   check=True, capture_output=True, text=True)


def bump(name: str, template_dir: Path, copier: list[str], run=subprocess.run) -> tuple[list[str], list[str]]:
    """Bump one template in place. Returns (changed template files, skipped notes). `run` is injectable for tests."""
    spec = UPDATERS[name]
    changed: list[str] = []
    skipped: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        render(template_dir, project, copier)
        before = {f: (project / f).read_text() for f in spec["files"] if (project / f).is_file()}
        for cmd in spec["commands"]:
            res = run(cmd, cwd=project, capture_output=True, text=True)
            if res.returncode != 0:
                skipped.append(f"{' '.join(cmd[:3])} failed: {(res.stderr or res.stdout).strip()[-200:]}")
        updated: dict[str, str] = {}
        originals: dict[Path, str] = {}
        for rel, old in before.items():
            new = (project / rel).read_text()
            if new == old:
                continue
            src = source_of(template_dir, rel)
            if src is None:
                skipped.append(f"{rel}: no template source")
                continue
            text = src.read_text()
            if rel in WHOLE_FILE:
                if any(t in text for t in JINJA):
                    skipped.append(f"{rel}: template source has Jinja, not copied")
                    continue
                result, notes = new, []
            else:
                result, notes = copy_back(old, new, text)
            skipped += [f"{rel}: {n}" for n in notes]
            if result != text:
                updated[rel] = result
                originals[src] = text
                src.write_text(result)
                changed.append(str(src.relative_to(template_dir.parent.parent)))
        if spec.get("atomic") and updated and skipped:
            for src, text in originals.items():
                src.write_text(text)
            return [], skipped + [f"rolled back: {name} is all-or-nothing and part of the update could not be applied"]
        if updated:   # the re-render must reproduce the bumped manifests
            verify = Path(tmp) / "verify"
            render(template_dir, verify, copier)
            for rel in updated:
                want = (project / rel).read_text()
                if rel not in WHOLE_FILE and (verify / rel).read_text() != want:
                    skipped.append(f"{rel}: re-render differs from the bumped manifest (review the diff)")
    return changed, skipped


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("templates", nargs="*", help=f"default: {', '.join(UPDATERS)}")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    if args.list:
        for n, s in UPDATERS.items():
            print(f"{n}: {', '.join(s['files'])}")
        return 0
    names = args.templates or list(UPDATERS)
    unknown = [n for n in names if n not in UPDATERS]
    if unknown:
        print(f"ERROR: unknown template(s): {', '.join(unknown)}", file=sys.stderr)
        return 2
    import core
    copier = core.find_copier()
    total = 0
    for n in names:
        tool = UPDATERS[n]["commands"][0][0]
        if shutil.which(tool) is None:
            print(f"{n}: skipped, '{tool}' is not installed")
            continue
        changed, skipped = bump(n, ROOT / "templates" / n, copier)
        total += len(changed)
        print(f"{n}: {len(changed)} file(s) bumped" + (f" ({', '.join(changed)})" if changed else ""))
        for s in skipped:
            print(f"  note: {s}")
    print(f"{total} template file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
