#!/usr/bin/env python3
"""Check that relative links in the repository's Markdown files point at files that exist (CI guard, `ci-local`).

  check-links.py [PATH...]     default: README, CONTRIBUTING, SECURITY, SUPPORT, CODE_OF_CONDUCT, CLAUDE.md, docs/, plugins/
External links (http, mailto) and pure #anchors are ignored; `path#anchor` is checked for the path only. Fenced code
blocks and inline code are skipped, as are templates (their Markdown contains Jinja placeholders).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")
DEFAULTS = ["README.md", "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md", "CODE_OF_CONDUCT.md", "CLAUDE.md", "docs", "plugins"]


def markdown_files(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in map(lambda x: ROOT / x, paths):
        out += [p] if p.is_file() else sorted(p.rglob("*.md")) if p.is_dir() else []
    return out


def links_in(text: str) -> list[str]:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return [a or b for a, b in LINK.findall(text)]


def main(argv: list[str]) -> int:
    broken = []
    for f in markdown_files(argv or DEFAULTS):
        for target in links_in(f.read_text(errors="replace")):
            if target.startswith(("http://", "https://", "mailto:", "#", "<")) or "{{" in target or "$" in target:
                continue
            path = target.split("#", 1)[0].split("?", 1)[0]
            if not path:
                continue
            resolved = (ROOT / path.lstrip("/")) if path.startswith("/") else (f.parent / path)
            if not resolved.exists():
                broken.append(f"{f.relative_to(ROOT)}: broken link '{target}'")
    for b in broken:
        print(b, file=sys.stderr)
    if broken:
        print(f"ERROR: {len(broken)} broken relative link(s)", file=sys.stderr)
        return 1
    print("OK: all relative Markdown links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
