#!/usr/bin/env python3
"""Developer Certificate of Origin check: every commit of a pull request must carry a matching Signed-off-by trailer.

  check-dco.py <base>..<head>        e.g. the PR's base SHA .. head SHA (CI passes them through BASE_SHA / HEAD_SHA)

`git commit -s` adds the trailer. It certifies https://developercertificate.org/ : you wrote the change or have the right to
submit it under the project's license. The trailer's e-mail must be the commit's author or committer e-mail. Merge commits
and commits made by bots (author name or e-mail contains "[bot]", e.g. Dependabot) are exempt.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

TRAILER = re.compile(r"^signed-off-by:\s*(?P<name>.+?)\s*<(?P<email>[^>\s]+@[^>\s]+)>\s*$", re.I | re.M)
SEP_COMMIT, SEP_FIELD = "\x1e", "\x1f"


def commits(rev_range: str, cwd: str | None = None) -> list[dict]:
    fmt = SEP_FIELD.join(["%H", "%an", "%ae", "%ce", "%B"]) + SEP_COMMIT
    out = subprocess.run(["git", "log", "--no-merges", f"--format={fmt}", rev_range], capture_output=True, text=True, check=True, cwd=cwd).stdout
    result = []
    for chunk in filter(str.strip, out.split(SEP_COMMIT)):
        sha, name, a_mail, c_mail, body = chunk.strip("\n").split(SEP_FIELD, 4)
        result.append({"sha": sha.strip(), "author": name, "emails": {a_mail.lower(), c_mail.lower()}, "body": body})
    return result


def problems(rev_range: str, cwd: str | None = None) -> list[str]:
    bad = []
    for c in commits(rev_range, cwd):
        if "[bot]" in c["author"].lower() or any("[bot]" in e for e in c["emails"]):
            continue
        signed = [m.group("email").lower() for m in TRAILER.finditer(c["body"])]
        if not signed:
            bad.append(f"{c['sha'][:10]}: missing 'Signed-off-by: Name <email>' (fix: git commit --amend -s, or git rebase --signoff <base>)")
        elif not set(signed) & c["emails"]:
            bad.append(f"{c['sha'][:10]}: the sign-off e-mail does not match the commit's author or committer e-mail")
    return bad


def main(argv: list[str]) -> int:
    rev_range = argv[0] if argv else f"{os.environ.get('BASE_SHA', 'origin/main')}..{os.environ.get('HEAD_SHA', 'HEAD')}"
    bad = problems(rev_range)
    if bad:
        print("ERROR: commits without a valid DCO sign-off (see CONTRIBUTING.md, 'Sign your commits'):", file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        return 1
    print(f"OK: every commit in {rev_range} is signed off")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
