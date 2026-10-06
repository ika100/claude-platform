#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///
"""Render ApplicationSets, overlays and Kubernetes manifests from services.yaml (ADR-014, ADR-017).

The GitOps repo owns every manifest. services.yaml is the human-edited registry; this script derives:
  applications/<app>/applicationset.yaml                       one ApplicationSet per env (dev/staging/prod)
  applications/<app>/overlays/<env>/<service>/                 deployment.yaml, service.yaml, [httproute.yaml], kustomization.yaml
  bootstrap/<app>-root.yaml                                    root Argo Application (app-of-apps), applied once by a human

A service is only rendered for the environments listed in its `environments` (default: dev), so a new service never
reaches staging/prod before `/gitops:promote` adds it. Existing image pins (`newTag`) are preserved on re-render.

services.yaml entry (written by `/gitops:compose`, every value explicit and reviewable):
  - name: todo-api
    repo: org/todo-api                 # informational: where the image is built
    shape: service-java
    image: ghcr.io/org/todo-api        # the tag is pinned in the overlay (dev: latest)
    port: 8080
    probes: {liveness: /health, readiness: /ready}
    user: 65532                        # numeric non-root UID the image runs as
    volumes: {tmp: /tmp}               # writable emptyDirs (root filesystem is read-only)
    env: {LOG_LEVEL: INFO}             # non-secret wiring, e.g. API_URL: http://todo-api
    secretRefs: []                     # names of existing Secrets exposed as env vars
    replicas: {dev: 1, staging: 1, prod: 2}   # or a single integer
    resources: {requests: {cpu: 50m, memory: 128Mi}, limits: {cpu: 500m, memory: 512Mi}}
    expose: {host: todo-api}           # optional: publish through the Gateway (needs app.yaml `hosts`)
    environments: [dev]

applications/<app>/app.yaml (optional):
  gateway: {name: traefik-gateway, namespace: kube-system}
  hosts: {dev: "{service}.{app}-dev.localhost"}     # per env; no entry = not exposed in that env

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
MANAGED_FILES = {"deployment.yaml", "service.yaml", "httproute.yaml", "kustomization.yaml"}


class RenderError(Exception):
    pass


def dump(doc: dict) -> str:
    return yaml.safe_dump(doc, sort_keys=False, default_flow_style=False)


def answers() -> dict:
    f = ROOT / ".copier-answers.yml"
    return yaml.safe_load(f.read_text()) if f.is_file() else {}


def existing_tag(kfile: Path) -> str | None:
    """Image tag already pinned in an overlay kustomization, if any."""
    if not kfile.is_file():
        return None
    doc = yaml.safe_load(kfile.read_text()) or {}
    for img in doc.get("images", []):
        if img.get("newTag"):
            return img["newTag"]
    return None


def load_services(app_dir: Path) -> list[dict]:
    services = (yaml.safe_load((app_dir / "services.yaml").read_text()) or {}).get("services") or []
    names = [s.get("name") for s in services]
    if len(names) != len(set(names)):
        raise RenderError(f"duplicate service names in {app_dir.name}/services.yaml")
    for s in services:
        n = s.get("name", "<no name>")
        if "port" not in s or "probes" not in s:
            raise RenderError(
                f"service '{n}' uses the v1 format (remote kustomize base). v2 needs port/probes/...: "
                "run `/gitops:compose import " + n + "` (or see docs/ADOPTING.md → migrating to v2)")
        for k in ("image", "probes"):
            if k not in s:
                raise RenderError(f"service '{n}': missing '{k}'")
        if set(s["probes"]) != {"liveness", "readiness"}:
            raise RenderError(f"service '{n}': probes needs liveness and readiness")
        bad = [e for e in s.get("environments", ["dev"]) if e not in ENVS]
        if bad:
            raise RenderError(f"service '{n}': unknown environments {bad} (valid: {ENVS})")
    return services


def envs_of(svc: dict) -> list[str]:
    return svc.get("environments") or ["dev"]


def labels_for(app: str, svc: dict) -> dict:
    # `app` is also the (immutable) selector: it matches what v1 manifests used, so migrating a running Deployment is an in-place update.
    return {"app": svc["name"], "app.kubernetes.io/name": svc["name"], "app.kubernetes.io/part-of": app, "app.kubernetes.io/managed-by": "gitops-app"}


def replicas_for(svc: dict, env: str) -> int:
    r = svc.get("replicas", 1)
    return int(r.get(env, 1)) if isinstance(r, dict) else int(r)


def deployment(app: str, svc: dict, env: str) -> dict:
    labels = labels_for(app, svc)
    selector = {"app": svc["name"]}
    env_vars = {"PORT": str(svc["port"]), **{k: str(v) for k, v in (svc.get("env") or {}).items()}}
    container: dict = {
        "name": "app",
        "image": svc["image"],
        "ports": [{"name": "http", "containerPort": int(svc["port"])}],
        "env": [{"name": k, "value": v} for k, v in sorted(env_vars.items())],
    }
    if svc.get("secretRefs"):
        container["envFrom"] = [{"secretRef": {"name": n}} for n in svc["secretRefs"]]
    if svc.get("resources"):
        container["resources"] = svc["resources"]
    http = lambda path: {"httpGet": {"path": path, "port": "http"}}  # noqa: E731
    container["startupProbe"] = {**http(svc["probes"]["liveness"]), "periodSeconds": 3, "failureThreshold": 40}  # up to 2 min (JVM)
    container["livenessProbe"] = {**http(svc["probes"]["liveness"]), "periodSeconds": 10}
    container["readinessProbe"] = {**http(svc["probes"]["readiness"]), "periodSeconds": 5}
    sc: dict = {"runAsNonRoot": True, "allowPrivilegeEscalation": False, "readOnlyRootFilesystem": True, "capabilities": {"drop": ["ALL"]}}
    if svc.get("user"):
        sc["runAsUser"] = int(svc["user"])
    container["securityContext"] = sc
    volumes = svc.get("volumes") or {}
    pod: dict = {"securityContext": {"runAsNonRoot": True, "seccompProfile": {"type": "RuntimeDefault"}}, "containers": [container]}
    if volumes:
        container["volumeMounts"] = [{"name": n, "mountPath": p} for n, p in sorted(volumes.items())]
        pod["volumes"] = [{"name": n, "emptyDir": {}} for n in sorted(volumes)]
    return {
        "apiVersion": "apps/v1", "kind": "Deployment",
        "metadata": {"name": svc["name"], "labels": labels},
        "spec": {"replicas": replicas_for(svc, env), "selector": {"matchLabels": selector},
                 "template": {"metadata": {"labels": labels}, "spec": pod}},
    }


def service(app: str, svc: dict) -> dict:
    return {
        "apiVersion": "v1", "kind": "Service",
        "metadata": {"name": svc["name"], "labels": labels_for(app, svc)},
        "spec": {"type": "ClusterIP", "selector": {"app": svc["name"]},
                 "ports": [{"name": "http", "port": 80, "targetPort": "http"}]},
    }


def httproute(app: str, svc: dict, env: str, cfg: dict) -> dict | None:
    expose = svc.get("expose")
    template = (cfg.get("hosts") or {}).get(env)
    if not expose or not template:
        return None
    host = template.format(service=(expose.get("host") if isinstance(expose, dict) else None) or svc["name"], app=app, env=env)
    gw = cfg.get("gateway") or {"name": "traefik-gateway", "namespace": "kube-system"}
    return {
        "apiVersion": "gateway.networking.k8s.io/v1", "kind": "HTTPRoute",
        "metadata": {"name": svc["name"], "labels": labels_for(app, svc)},
        "spec": {"parentRefs": [{"name": gw["name"], "namespace": gw.get("namespace", "kube-system")}], "hostnames": [host],
                 "rules": [{"matches": [{"path": {"type": "PathPrefix", "value": (expose.get("path", "/") if isinstance(expose, dict) else "/")}}],
                            "backendRefs": [{"name": svc["name"], "port": 80}]}]},
    }


def render_app(app_dir: Path, ans: dict) -> dict[Path, str]:
    app = app_dir.name
    services = load_services(app_dir)
    cfg_file = app_dir / "app.yaml"
    cfg = (yaml.safe_load(cfg_file.read_text()) or {}) if cfg_file.is_file() else {}
    org = ans.get("github_org", "ika100")
    server = ans.get("cluster_server", "https://kubernetes.default.svc")
    gitops_repo = f"https://github.com/{org}/{ans.get('project_name', app + '-gitops')}"
    out: dict[Path, str] = {}

    docs = []
    for env in ENVS:
        docs.append({
            "apiVersion": "argoproj.io/v1alpha1", "kind": "ApplicationSet",
            "metadata": {"name": f"{app}-{env}", "namespace": "argocd"},
            "spec": {
                "generators": [{"list": {"elements": [{"name": s["name"]} for s in services if env in envs_of(s)]}}],
                "template": {
                    "metadata": {"name": "{{name}}-" + env},
                    "spec": {
                        "project": "default",
                        "source": {"repoURL": gitops_repo, "targetRevision": "main", "path": f"applications/{app}/overlays/{env}/" + "{{name}}"},
                        "destination": {"server": server, "namespace": f"{app}-{env}"},
                        "syncPolicy": {"automated": {"prune": True, "selfHeal": True}, "syncOptions": ["CreateNamespace=true"]},
                    },
                },
            },
        })
    out[app_dir / "applicationset.yaml"] = "---\n".join(dump(d) for d in docs)

    out[ROOT / "bootstrap" / f"{app}-root.yaml"] = dump({
        "apiVersion": "argoproj.io/v1alpha1", "kind": "Application",
        "metadata": {"name": f"{app}-root", "namespace": "argocd"},
        "spec": {
            "project": "default",
            "source": {"repoURL": gitops_repo, "targetRevision": "main", "path": f"applications/{app}", "directory": {"include": "applicationset.yaml"}},
            "destination": {"server": server, "namespace": "argocd"},
            "syncPolicy": {"automated": {"prune": True, "selfHeal": True}},
        },
    })

    for env in ENVS:
        for s in services:
            if env not in envs_of(s):
                continue
            base = app_dir / "overlays" / env / s["name"]
            files = {"deployment.yaml": deployment(app, s, env), "service.yaml": service(app, s)}
            route = httproute(app, s, env, cfg)
            if route:
                files["httproute.yaml"] = route
            for fname, doc in files.items():
                out[base / fname] = dump(doc)
            tag = existing_tag(base / "kustomization.yaml") or "latest"
            out[base / "kustomization.yaml"] = dump({
                "apiVersion": "kustomize.config.k8s.io/v1beta1", "kind": "Kustomization",
                "resources": sorted(files), "images": [{"name": s["image"], "newTag": tag}],
            })
    return out


def stale_paths(app_dir: Path, wanted: set[Path]) -> list[Path]:
    """Overlay service dirs for services/envs no longer declared, and generated files no longer produced."""
    stale: list[Path] = []
    for env in ENVS:
        base = app_dir / "overlays" / env
        if not base.is_dir():
            continue
        for d in base.iterdir():
            if not d.is_dir():
                continue
            if not any(p.parent == d for p in wanted):
                stale.append(d)
                continue
            stale += [f for f in d.iterdir() if f.name in MANAGED_FILES and f not in wanted]
    return stale


def main() -> int:
    check = "--check" in sys.argv[1:]
    ans = answers()
    apps = sorted(p.parent for p in (ROOT / "applications").glob("*/services.yaml"))
    if not apps:
        print("ERROR: no applications/*/services.yaml found", file=sys.stderr)
        return 1
    drift: list[str] = []
    try:
        for app_dir in apps:
            rendered = render_app(app_dir, ans)
            for path, content in rendered.items():
                if not path.is_file() or path.read_text() != content:
                    drift.append(str(path.relative_to(ROOT)))
                    if not check:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(content)
            for st in stale_paths(app_dir, set(rendered)):
                drift.append(f"{st.relative_to(ROOT)} (stale)")
                if not check:
                    shutil.rmtree(st) if st.is_dir() else st.unlink()
    except RenderError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if check and drift:
        print("ERROR: rendered files are out of date — run `devbox run render`:", file=sys.stderr)
        for d in drift:
            print(f"  {d}", file=sys.stderr)
        return 1
    print("OK: up to date" if check else f"rendered ({len(drift)} file(s) changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
