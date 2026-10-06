#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml", "ruamel.yaml"]
# ///
"""cplat — deterministic implementation of the claude-platform commands.

The slash commands (plugins/*/commands/*.md) are thin: they run this script with --dry-run, show the plan to the user,
and run it for real. Everything that can be code is code (and has tests in tests/cplat).

  cplat.py new-service <name> <description…> [--web|--gitops|--library|--type SHAPE] [--app ORG/REPO] [--dry-run]
  cplat.py update-service [--data KEY=VALUE] [--dry-run]
  cplat.py doctor [--json]
  cplat.py shape [--repo DIR]          shape + agent routing for the /svc:* orchestrators
  cplat.py compose add|remove <service…> [--expose] [--env K=V] [--from-k8s] [--pr]   (run inside a gitops-app repo)
  cplat.py promote <service…|--all> <from> <to> [--version V] [--sha S] [--pr]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import core  # noqa: E402

COMMANDS = {
    "new-service": "newsvc",
    "update-service": "update",
    "doctor": "doctor",
    "shape": "shapecmd",
    "compose": "compose",
    "promote": "promote",
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help") or argv[0] not in COMMANDS:
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 2
    module = __import__(COMMANDS[argv[0]])
    try:
        return module.main(argv[1:])
    except core.PlatformError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if e.hint:
            print(f"  fix: {e.hint}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
