#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///
"""Read and validate the shape registry (shapes.yml, ADR-015).

Usage:
  shapes.py validate          schema + referential checks on shapes.yml
  shapes.py check             validate + templates/plugins exist + PRD §4 table matches
  shapes.py get <id> <field>  print one field (plugin, template, deployable, library, status)
  shapes.py ids               print shape ids, one per line

Run with: uv run scripts/shapes.py <cmd>   (PEP 723 inline deps)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ["id", "plugin", "template", "deployable", "library", "detection", "status"]
STATUSES = {"stable", "planned", "deprecated"}
PRD = ROOT / "docs" / "requirements" / "platform-vision.md"


def load() -> list[dict]:
    return yaml.safe_load((ROOT / "shapes.yml").read_text())["shapes"]


def validate(shapes: list[dict]) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    for s in shapes:
        sid = s.get("id", "<missing id>")
        for f in REQUIRED:
            if f not in s:
                errs.append(f"{sid}: missing field '{f}'")
        if sid in seen:
            errs.append(f"{sid}: duplicate id")
        seen.add(sid)
        if s.get("status") not in STATUSES:
            errs.append(f"{sid}: status must be one of {sorted(STATUSES)}")
        det = s.get("detection", {})
        if det.get("copier_src") != f"templates/{s.get('template')}":
            errs.append(f"{sid}: detection.copier_src must be templates/{s.get('template')}")
        if not det.get("sniff"):
            errs.append(f"{sid}: detection.sniff must list at least one marker")
        if s.get("library") and s.get("deployable"):
            errs.append(f"{sid}: a library cannot be deployable")
    return errs


def check_files(shapes: list[dict]) -> list[str]:
    errs: list[str] = []
    for s in shapes:
        tdir = ROOT / "templates" / s["template"]
        pdir = ROOT / "plugins" / s["plugin"]
        if s["status"] != "planned":
            if not (tdir / "copier.yml").is_file():
                errs.append(f"{s['id']}: templates/{s['template']}/copier.yml missing (status {s['status']})")
            if not pdir.is_dir():
                errs.append(f"{s['id']}: plugins/{s['plugin']}/ missing (status {s['status']})")
    return errs


def prd_rows() -> dict[str, tuple[str, str]]:
    """Parse the §4 table: shape id -> (plugin, template)."""
    text = PRD.read_text()
    section = text.split("## 4. Shape registry", 1)[1].split("\n## 5.", 1)[0]
    rows = {}
    for line in section.splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"[a-z]+(-[a-z]+)+", cells[0]):
            rows[cells[0]] = (cells[1].replace("`", "").split(" ")[0], cells[2])
    return rows


def check_prd(shapes: list[dict]) -> list[str]:
    errs: list[str] = []
    rows = prd_rows()
    by_id = {s["id"]: s for s in shapes}
    for sid in sorted(set(rows) | set(by_id)):
        if sid not in rows:
            errs.append(f"{sid}: in shapes.yml but not in PRD §4 table")
        elif sid not in by_id:
            errs.append(f"{sid}: in PRD §4 table but not in shapes.yml")
        elif rows[sid] != (by_id[sid]["plugin"], by_id[sid]["template"]):
            errs.append(f"{sid}: PRD says {rows[sid]}, shapes.yml says {(by_id[sid]['plugin'], by_id[sid]['template'])}")
    return errs


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, shapes = argv[0], load()
    if cmd == "ids":
        print("\n".join(s["id"] for s in shapes))
        return 0
    if cmd == "get":
        sid, field = argv[1], argv[2]
        s = next((x for x in shapes if x["id"] == sid), None)
        if s is None or field not in s:
            print(f"unknown shape/field: {sid} {field}", file=sys.stderr)
            return 1
        v = s[field]
        print(str(v).lower() if isinstance(v, bool) else v)
        return 0
    errs = validate(shapes)
    if cmd == "check":
        errs += check_files(shapes) + check_prd(shapes)
    elif cmd != "validate":
        print(__doc__)
        return 2
    for e in errs:
        print(f"ERROR: {e}", file=sys.stderr)
    if not errs:
        print(f"OK: {len(shapes)} shapes ({cmd})")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
