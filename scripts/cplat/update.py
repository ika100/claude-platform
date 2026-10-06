"""`update-service`: re-apply the platform template to an existing repo on a review branch."""
from __future__ import annotations

import argparse
import datetime
import re
from pathlib import Path

import core
from core import PLATFORM_ROOT, PlatformError, Report, run


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cplat update-service", description=__doc__)
    p.add_argument("--ref", default=None, help="platform ref being applied (informational; the running checkout is the source)")
    p.add_argument("--data", action="append", default=[], metavar="KEY=VALUE", help="change a template answer (repeatable)")
    p.add_argument("--repo", default=".", help="repo to update (default: current directory)")
    p.add_argument("--migrate", action="store_true", help="v1 → v2: also delete the service's k8s/ directory (the gitops-app repo owns manifests now; import them first with `compose add <service> --from-k8s`)")
    p.add_argument("--skip-tasks", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    return p


def detect_shape(repo: Path) -> str:
    out = run(["bash", str(PLATFORM_ROOT / "scripts" / "detect-shape.sh"), str(repo)], check=False)
    if out.returncode != 0 or not out.stdout.strip():
        raise PlatformError("cannot determine the repo's shape", hint="a .copier-answers.yml with _src_path ending in templates/<shape> is required (see docs/ADOPTING.md, Step 5)")
    return out.stdout.strip()


def resolve(argv: list[str]) -> dict:
    ns = build_parser().parse_args(argv)
    repo = Path(ns.repo).resolve()
    if not (repo / ".git").is_dir():
        raise PlatformError(f"{repo} is not a git repository")
    if not (repo / ".copier-answers.yml").is_file():
        raise PlatformError("no .copier-answers.yml in the repo", hint="see docs/ADOPTING.md → 'Adopt the template for skeleton updates'")
    if run(["git", "status", "--porcelain"], cwd=repo).stdout.strip():
        raise PlatformError("the working tree has uncommitted changes", hint="commit or stash first; the update must be one reviewable commit")
    for kv in ns.data:
        if "=" not in kv:
            raise PlatformError(f"--data expects KEY=VALUE, got '{kv}'")
    shape = detect_shape(repo)
    entry = next(s for s in core.registry.load() if s["id"] == shape)
    stamp = core.read_stamp(repo)
    return {"repo": repo, "shape": shape, "template": entry["template"], "data": ns.data, "old": stamp.get("platform"),
            "new": core.platform_version(), "ref": ns.ref or stamp.get("ref") or "main", "skip_tasks": ns.skip_tasks, "migrate": ns.migrate,
            "dry_run": ns.dry_run, "json": ns.json}


def branch_name() -> str:
    return "chore/platform-update-" + datetime.date.today().strftime("%Y%m%d")


def plan(req: dict) -> Report:
    r = Report(title=f"Update {req['repo'].name} ({req['shape']}) from platform {req['old'] or 'unknown'} → {req['new']}")
    cur = run(["git", "symbolic-ref", "--short", "HEAD"], cwd=req["repo"], check=False).stdout.strip()
    if cur in ("main", "master"):
        r.will_do.append(f"create review branch {branch_name()}")
    r.will_do.append(f"re-apply templates/{req['template']} with the repo's recorded answers" + (f" plus {', '.join(req['data'])}" if req["data"] else ""))
    r.will_do.append("OVERWRITE skeleton files (CI, Dockerfile, devbox.json, CLAUDE.md, …); project-owned files are never touched")
    if req["migrate"]:
        r.will_do.append("DELETE k8s/ (v1 → v2 migration: manifests are generated in the product's gitops-app repo; recoverable from git history)")
    r.will_do.append("restore the stable template source in .copier-answers.yml and stamp .platform-version")
    r.will_do.append("commit once (nothing is pushed)")
    return r


def execute(req: dict) -> Report:
    repo: Path = req["repo"]
    r = plan(req)
    cur = run(["git", "symbolic-ref", "--short", "HEAD"], cwd=repo).stdout.strip()
    if cur in ("main", "master"):
        run(["git", "checkout", "-q", "-b", branch_name()], cwd=repo)
        r.did.append(f"created branch {branch_name()}")
    before = (repo / ".copier-answers.yml").read_text()

    cmd = [*core.find_copier(), "copy", str(PLATFORM_ROOT / "templates" / req["template"]), ".", "--data-file", ".copier-answers.yml",
           "--overwrite", "--defaults", "--trust", "--skip-tasks"]
    for kv in req["data"]:
        cmd += ["--data", kv]
    run(cmd, cwd=repo)
    answers = repo / ".copier-answers.yml"
    answers.write_text(re.sub(r"^_src_path:.*$", f"_src_path: gh:ika100/claude-platform/templates/{req['template']}", answers.read_text(), flags=re.M))
    core.write_stamp(repo, req["shape"], req["ref"])
    if req["migrate"] and (repo / "k8s").is_dir():
        import shutil
        shutil.rmtree(repo / "k8s")
        r.did.append("removed k8s/ (v1 manifests; import them with `compose add <service> --from-k8s` if you have not yet)")

    new_keys = sorted(set(re.findall(r"^([a-z_]+):", answers.read_text(), re.M)) - set(re.findall(r"^([a-z_]+):", before, re.M)))
    changed = [ln[3:] for ln in run(["git", "status", "--porcelain"], cwd=repo).stdout.splitlines()]
    modified = [ln[3:] for ln in run(["git", "status", "--porcelain"], cwd=repo).stdout.splitlines() if ln[:2].strip() == "M"]
    if not changed:
        if cur in ("main", "master"):  # do not leave an empty review branch behind
            run(["git", "checkout", "-q", cur], cwd=repo)
            run(["git", "branch", "-D", branch_name()], cwd=repo)
        r.did.append(f"already up to date with platform {req['new']} — nothing changed")
        return r
    run(["git", "add", "-A"], cwd=repo)
    run(["git", *core.git_identity(repo), "commit", "-q", "-m", f"chore: update skeleton from platform {req['new']}"], cwd=repo)
    r.did.append(f"re-applied the template; {len(changed)} file(s) changed, committed on {branch_name() if cur in ('main','master') else cur}")
    notes = core.changelog_between(req["old"], req["new"])
    r.data = {"changed": changed, "modified": modified, "new_answers": new_keys, "changelog": notes}
    if modified:
        r.next_steps.append("review MODIFIED skeleton files for lost local customisations: " + ", ".join(modified[:12]) + " — keep yours with `git checkout HEAD~1 -- <file>`")
    if new_keys:
        r.next_steps.append("new template answers took their defaults: " + ", ".join(new_keys))
    if notes:
        r.next_steps.append("platform changes since your version are in docs/CHANGELOG.md of claude-platform (see changelog in --json output)")
    r.next_steps.append("run the repo's checks: devbox run quality && devbox run test-fast, then push the branch and open a PR")
    r.undo.append(f"git checkout {cur} && git branch -D {branch_name()}" if cur in ("main", "master") else "git reset --hard HEAD~1")
    return r


def main(argv: list[str]) -> int:
    req = resolve(argv)
    if req["dry_run"]:
        plan(req).emit(True, req["json"])
        return 0
    execute(req).emit(False, req["json"])
    return 0
