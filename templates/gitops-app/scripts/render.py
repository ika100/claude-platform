#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///
"""Render the per-environment overlays and ApplicationSets from services.yaml (ADR-014).

services.yaml is the human-edited registry. This script derives:
  applications/<app>/applicationset.yaml                    one ApplicationSet per env (dev/staging/prod)
  applications/<app>/overlays/<env>/<service>/kustomization.yaml

Existing image pins (`newTag`) and kustomize refs in overlays are preserved, so running this after
`/gitops:promote` never un-pins anything. New services start at: dev -> main/latest,
staging/prod -> main/latest (unpromoted; promote them before relying on the env).

Usage:
  render.py            write files
  render.py --check    exit 1 if the tree differs from what would be rendered (CI / quality gate)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENVS = ["dev", "staging", "prod"]


def dump(doc: dict) -> str:
    return yaml.safe_dump(doc, sort_keys=False, default_flow_style=False)


def answers() -> dict:
    f = ROOT / ".copier-answers.yml"
    return yaml.safe_load(f.read_text()) if f.is_file() else {}


def existing_pin(kfile: Path) -> tuple[str | None, str | None]:
    """Return (ref, newTag) already pinned in an overlay kustomization, if any."""
    if not kfile.is_file():
        return None, None
    doc = yaml.safe_load(kfile.read_text()) or {}
    ref = tag = None
    for res in doc.get("resources", []):
        if "?ref=" in res:
            ref = res.split("?ref=", 1)[1]
    for img in doc.get("images", []):
        tag = img.get("newTag", tag)
    return ref, tag


def render_app(app_dir: Path, ans: dict) -> dict[Path, str]:
    services = (yaml.safe_load((app_dir / "services.yaml").read_text()) or {}).get("services") or []
    app = app_dir.name
    org = ans.get("github_org", "ika100")
    registry = ans.get("docker_registry", f"ghcr.io/{org}")
    server = ans.get("cluster_server", "https://kubernetes.default.svc")
    gitops_repo = f"https://github.com/{org}/{ans.get('project_name', app + '-gitops')}"
    out: dict[Path, str] = {}

    docs = []
    for env in ENVS:
        docs.append(
            {
                "apiVersion": "argoproj.io/v1alpha1",
                "kind": "ApplicationSet",
                "metadata": {"name": f"{app}-{env}", "namespace": "argocd"},
                "spec": {
                    "generators": [{"list": {"elements": [{"name": s["name"]} for s in services]}}],
                    "template": {
                        "metadata": {"name": "{{name}}-" + env},
                        "spec": {
                            "project": "default",
                            "source": {
                                "repoURL": gitops_repo,
                                "targetRevision": "main",
                                "path": f"applications/{app}/overlays/{env}/" + "{{name}}",
                            },
                            "destination": {"server": server, "namespace": f"{app}-{env}"},
                            "syncPolicy": {
                                "automated": {"prune": True, "selfHeal": True},
                                "syncOptions": ["CreateNamespace=true"],
                            },
                        },
                    },
                },
            }
        )
    out[app_dir / "applicationset.yaml"] = "---\n".join(dump(d) for d in docs)

    for env in ENVS:
        for s in services:
            kfile = app_dir / "overlays" / env / s["name"] / "kustomization.yaml"
            ref, tag = existing_pin(kfile)
            ref = ref or "main"
            tag = tag or "latest"
            path = s.get("path", "k8s/base")
            doc = {
                "apiVersion": "kustomize.config.k8s.io/v1beta1",
                "kind": "Kustomization",
                "resources": [f"https://github.com/{s['repo']}//{path}?ref={ref}"],
                "images": [{"name": f"{registry}/{s['name']}", "newTag": tag}],
            }
            out[kfile] = dump(doc)
    return out


def stale_dirs(app_dir: Path, services: list[str]) -> list[Path]:
    stale = []
    for env in ENVS:
        base = app_dir / "overlays" / env
        if base.is_dir():
            stale += [d for d in base.iterdir() if d.is_dir() and d.name not in services]
    return stale


def main() -> int:
    check = "--check" in sys.argv[1:]
    ans = answers()
    apps = sorted(p.parent for p in (ROOT / "applications").glob("*/services.yaml"))
    if not apps:
        print("ERROR: no applications/*/services.yaml found", file=sys.stderr)
        return 1
    drift: list[str] = []
    for app_dir in apps:
        services = (yaml.safe_load((app_dir / "services.yaml").read_text()) or {}).get("services") or []
        names = [s["name"] for s in services]
        if len(names) != len(set(names)):
            print(f"ERROR: duplicate service names in {app_dir.name}/services.yaml", file=sys.stderr)
            return 1
        for path, content in render_app(app_dir, ans).items():
            if not path.is_file() or path.read_text() != content:
                drift.append(str(path.relative_to(ROOT)))
                if not check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content)
        for d in stale_dirs(app_dir, names):
            drift.append(f"{d.relative_to(ROOT)} (stale)")
            if not check:
                shutil.rmtree(d)
    if check and drift:
        print("ERROR: rendered files are out of date — run `devbox run render`:", file=sys.stderr)
        for d in drift:
            print(f"  {d}", file=sys.stderr)
        return 1
    print(("OK: up to date" if check else f"rendered ({len(drift)} file(s) changed)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
