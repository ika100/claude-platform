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


CORE_RECIPES = ["lint", "lint-fix", "quality", "test", "test-fast", "security"]
DEPLOY_RECIPES = ["image-build", "image-scan", "deploy-check"]
CONTRACT_AGENTS = ["coder", "tester"]
DEPLOY_AGENTS = ["deployment", "observability", "release"]


def _template_file(tdir: Path, name: str) -> Path | None:
    for cand in (tdir / name, tdir / f"{name}.jinja"):
        if cand.is_file():
            return cand
    return None


def check_contract(shapes: list[dict]) -> list[str]:
    """PRD §4.1 contract: every non-planned shape ships the template, plugin and detection artifacts."""
    errs: list[str] = []
    detect = (ROOT / "scripts" / "detect-shape.sh").read_text()
    fixtures = (ROOT / "scripts" / "test-detect-shape.sh").read_text()
    for s in shapes:
        if s["status"] == "planned":
            continue
        sid, tdir, pdir = s["id"], ROOT / "templates" / s["template"], ROOT / "plugins" / s["plugin"]
        # 1. template: devbox recipes, CLAUDE.md, plugin enablement
        devbox = _template_file(tdir, "devbox.json")
        if devbox is None:
            errs.append(f"{sid}: template has no devbox.json")
        else:
            text = devbox.read_text()
            need = CORE_RECIPES + (DEPLOY_RECIPES if s["deployable"] else [])
            for r in need:
                if f'"{r}"' not in text:
                    errs.append(f"{sid}: devbox.json missing canonical recipe '{r}'")
        if _template_file(tdir, "CLAUDE.md") is None:
            errs.append(f"{sid}: template has no CLAUDE.md")
        settings = _template_file(tdir / ".claude", "settings.json")
        if settings is None:
            errs.append(f"{sid}: template has no .claude/settings.json")
        else:
            st = settings.read_text()
            for plugin in (s["plugin"], "shared"):
                if f'"{plugin}@ika100-claude": true' not in st:
                    errs.append(f"{sid}: .claude/settings.json does not enable '{plugin}'")
        # 2. plugin: agents
        if s["plugin"] != "gitops":
            agents = CONTRACT_AGENTS + (DEPLOY_AGENTS if s["deployable"] else [])
            for a in agents:
                if s["plugin"] == "svc":
                    break  # svc owns the python shapes and is checked by its own manifest
                if not (pdir / "agents" / f"{a}.md").is_file():
                    errs.append(f"{sid}: plugins/{s['plugin']}/agents/{a}.md missing")
        # 3. detection registration
        if f"templates/{s['template']}" not in detect:
            errs.append(f"{sid}: scripts/detect-shape.sh has no copier_src case for templates/{s['template']}")
        if "for s in" not in fixtures:  # fixtures iterate over every id in shapes.yml
            errs.append(f"{sid}: detection fixtures do not iterate the registry")
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
        errs += check_files(shapes) + check_contract(shapes) + check_prd(shapes)
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
