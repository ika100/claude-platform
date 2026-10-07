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
  cplat.py addon add|remove|list [postgres]   backing services of the application (app.yaml)
  cplat.py secret set|list ...         remote secrets of the local cluster (values never go to git)
  cplat.py feedback --title T [--what …] [--details-file F] [--submit]   draft (and file) a platform issue, secrets removed
  cplat.py status [--context KUBE_CONTEXT]   one table: pins per env, service CI, Argo sync/health
"""
from __future__ import annotations

import os
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
    "status": "status",
    "secret": "secret",
    "addon": "addon",
    "feedback": "feedback",
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
    except Exception as e:  # noqa: BLE001  (an unexpected crash is a platform defect, not a user error)
        print(f"ERROR: unexpected failure in `cplat {argv[0]}`: {type(e).__name__}: {e}", file=sys.stderr)
        print("  This looks like a platform bug. Run `/shared:report-issue` (or `cplat feedback --title ...`) to file it; "
              "nothing is sent without your OK.", file=sys.stderr)
        if os.environ.get("CPLAT_DEBUG"):
            raise
        return 70


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
