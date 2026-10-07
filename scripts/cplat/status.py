"""`status`: one table for a product — what each environment pins, how the service's CI is doing, and Argo's view."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

import core
import gitops
from core import PlatformError, Report, run

ENVS = gitops.ENVS


def sh(cmd: list[str]) -> str | None:
    """Run a command; None when the tool is missing or fails (status is best-effort and must never crash)."""
    try:
        p = run(cmd, check=False, timeout=30)
    except PlatformError:
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def pinned_tag(app_dir: Path, env: str, name: str) -> str | None:
    f = app_dir / "overlays" / env / name / "kustomization.yaml"
    if not f.is_file():
        return None
    for img in (yaml.safe_load(f.read_text()) or {}).get("images", []):
        if img.get("newTag"):
            return img["newTag"]
    return None


def ci_state(slug: str) -> str:
    out = sh(["gh", "run", "list", "-R", slug, "--branch", "main", "--workflow", "ci", "--limit", "1", "--json", "status,conclusion", "-q", '.[0]|"\\(.status) \\(.conclusion)"'])
    if not out:
        return "?"
    status, _, concl = out.partition(" ")
    return "running" if status != "completed" else ("ok" if concl == "success" else concl or "?")


def argo_state(context: str | None) -> dict[str, str]:
    if not context:
        return {}
    out = sh(["kubectl", "--context", context, "-n", "argocd", "get", "applications", "-o", "json"])
    if not out:
        return {}
    items = json.loads(out).get("items", [])
    return {i["metadata"]["name"]: f"{i['status'].get('sync', {}).get('status', '?')}/{i['status'].get('health', {}).get('status', '?')}" for i in items}


def collect(repo: Path, app: str | None, context: str | None) -> tuple[str, list[dict]]:
    app_dir = gitops.find_app(repo, app)
    data = yaml.safe_load((app_dir / "services.yaml").read_text()) or {}
    argo = argo_state(context)
    rows = []
    for s in data.get("services") or []:
        envs = s.get("environments") or ["dev"]
        ci = ci_state(s["repo"]) if s.get("repo") else "?"
        for env in ENVS:
            if env not in envs:
                continue
            rows.append({"service": s["name"], "env": env, "tag": pinned_tag(app_dir, env, s["name"]) or "?",
                         "ci": ci, "argo": argo.get(f"{s['name']}-{env}", "-" if not context else "missing"),
                         "exposed": bool(s.get("expose"))})
    cfg_file = app_dir / "app.yaml"
    declared = list(((yaml.safe_load(cfg_file.read_text()) or {}).get("addons") or {})) if cfg_file.is_file() else []
    for name in declared:   # an addon runs in every environment where a service uses it
        for env in ENVS:
            if any(name in (s.get("uses") or []) and env in (s.get("environments") or ["dev"]) for s in data.get("services") or []):
                rows.append({"service": f"{name} (addon)", "env": env, "tag": "-", "ci": "-",
                             "argo": argo.get(f"addon-{name}-{env}", "-" if not context else "missing"), "exposed": False})
    return app_dir.name, rows


def render_table(app: str, rows: list[dict], stamp: dict, context: str | None) -> str:
    head = f"## {app} (gitops-app) — platform {core.platform_version()} available, repo stamped {stamp.get('platform', 'none')}"
    cols = ["service", "env", "tag", "ci", "argo"]
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) if rows else len(c) for c in cols}
    lines = [head, ""] + ["  " + "  ".join(c.ljust(widths[c]) for c in cols), "  " + "  ".join("-" * widths[c] for c in cols)]
    for r in rows:
        lines.append("  " + "  ".join(str(r[c]).ljust(widths[c]) for c in cols))
    if not rows:
        lines.append("  (no services yet — /gitops:compose add <service>)")
    if not context:
        lines += ["", "Argo column empty? pass --context <kube-context> (e.g. k3d-" + app + "-local)."]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="cplat status", description=__doc__)
    ap.add_argument("--repo-dir", default=".")
    ap.add_argument("--app")
    ap.add_argument("--context", help="kube context to read ArgoCD applications from")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    repo = Path(ns.repo_dir).resolve()
    app, rows = collect(repo, ns.app, ns.context)
    if ns.json:
        print(json.dumps({"app": app, "rows": rows}, indent=2))
    else:
        print(render_table(app, rows, core.read_stamp(repo), ns.context))
    return 0
