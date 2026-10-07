"""`compose`: add/remove services in a gitops-app repo (services.yaml → generated manifests)."""
from __future__ import annotations

import argparse
import base64
import re
from pathlib import Path

import yaml

import core
import gitops
from core import PlatformError, Report, run


def gh(args: list[str]) -> str:
    """`gh` wrapper (tests replace this)."""
    return run(["gh", *args]).stdout


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cplat compose", description=__doc__)
    p.add_argument("action", choices=["add", "remove"])
    p.add_argument("services", nargs="+", help="service repo names (org/name, or just name = <github_org>/name)")
    p.add_argument("--app", help="application name when the repo has several")
    p.add_argument("--repo-dir", default=".", help="the gitops-app repo (default: current directory)")
    p.add_argument("--env", action="append", default=[], metavar="KEY=VALUE", help="env var for the service (single service only)")
    p.add_argument("--expose", nargs="?", const=True, default=None, metavar="HOST", help="publish through the Gateway (optional host label)")
    p.add_argument("--generate", action="append", default=[], metavar="SECRET=KEY,KEY", help="Secret whose values ESO generates randomly once per environment (single service only)")
    p.add_argument("--secret", action="append", default=[], metavar="SECRET=KEY,KEY", help="Secret read from the secret store (set the values with `cplat secret set`; single service only)")
    p.add_argument("--secret-ref", action="append", default=[], metavar="NAME", help="existing Secret in the namespace to expose as env vars, e.g. the one generated for another service (single service only)")
    p.add_argument("--uses", action="append", default=[], metavar="ADDON", help="addon the service needs (e.g. postgres → DATABASE_URL); declare it first with `cplat addon add`")
    p.add_argument("--replicas", type=int)
    p.add_argument("--port", type=int, help="override the port (default: the service's template answer, else the shape default)")
    p.add_argument("--from-k8s", action="store_true", help="seed port/probes/env/replicas/resources from the service's existing k8s/base/deployment.yaml (v1 → v2 migration)")
    p.add_argument("--shape", help="shape of the service when it has no .copier-answers.yml")
    p.add_argument("--pr", action="store_true", help="create branch, commit, push and open a pull request")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    return p


def repo_file(slug: str, path: str) -> str | None:
    try:
        raw = gh(["api", f"repos/{slug}/contents/{path}", "-q", ".content"])
    except PlatformError:
        return None
    return base64.b64decode(raw).decode() if raw.strip() else None


def shape_of(answers_text: str | None, explicit: str | None) -> str:
    entries = core.registry.load()
    if explicit:
        if explicit not in {e["id"] for e in entries}:
            raise PlatformError(f"unknown shape '{explicit}'")
        return explicit
    if answers_text:
        src = (yaml.safe_load(answers_text) or {}).get("_src_path", "")
        for e in entries:
            if src.rstrip("/").endswith("templates/" + e["template"]):
                return e["id"]
    raise PlatformError("cannot tell the service's shape", hint="the service repo needs a .copier-answers.yml from the platform template, or pass --shape <shape>")


def seed_from_k8s(slug: str) -> dict:
    text = repo_file(slug, "k8s/base/deployment.yaml")
    if not text:
        raise PlatformError(f"{slug} has no k8s/base/deployment.yaml to import")
    dep = yaml.safe_load(text)
    spec = dep["spec"]["template"]["spec"]
    c = spec["containers"][0]
    out: dict = {}
    if c.get("ports"):
        out["port"] = c["ports"][0]["containerPort"]
    probes = {}
    for k, key in (("liveness", "livenessProbe"), ("readiness", "readinessProbe")):
        path = ((c.get(key) or {}).get("httpGet") or {}).get("path")
        if path:
            probes[k] = path
    if len(probes) == 2:
        out["probes"] = probes
    env = {e["name"]: str(e["value"]) for e in c.get("env", []) if "value" in e and e["name"] != "PORT"}
    if env:
        out["env"] = env
    if "replicas" in dep["spec"]:
        out["replicas"] = dep["spec"]["replicas"]
    if c.get("resources"):
        out["resources"] = c["resources"]
    return out


def parse_secret_args(items: list[str]) -> list[tuple[str, list[str]]]:
    out = []
    for item in items:
        name, _, keys = item.partition("=")
        ks = [k for k in keys.split(",") if k]
        if not name or not ks:
            raise PlatformError(f"expected SECRET=KEY[,KEY...], got '{item}'", hint="e.g. --generate todo-api-auth=DB_PASSWORD,JWT_KEY")
        out.append((name, ks))
    return out


def build_entry(name: str, slug: str, shape_entry: dict, port: int | None, registry_ns: str, ns: argparse.Namespace, seed: dict) -> dict:
    rt = shape_entry["runtime"]
    entry = {
        "name": name, "repo": slug, "shape": shape_entry["id"], "image": f"{registry_ns}/{name}",
        "port": ns.port or seed.get("port") or port or rt["port"],
        "probes": seed.get("probes") or dict(rt["probes"]),
        "user": rt["user"],
        "metrics": rt["metrics"],
        "volumes": dict(rt.get("volumes") or {}),
        "env": {**(rt.get("env") or {}), **(seed.get("env") or {})},
        "secretRefs": [],
        "replicas": ns.replicas or seed.get("replicas") or 1,
        "resources": seed.get("resources") or rt["resources"],
        "environments": ["dev"],
    }
    for kv in ns.env:
        k, _, v = kv.partition("=")
        if not k or not _:
            raise PlatformError(f"--env expects KEY=VALUE, got '{kv}'")
        entry["env"][k] = v
    secrets = [{"name": n, "generate": keys} for n, keys in parse_secret_args(ns.generate)] + \
              [{"name": n, "remote": {"keys": keys}} for n, keys in parse_secret_args(ns.secret)]
    if secrets:
        entry["secrets"] = secrets
    if ns.uses:
        entry["uses"] = list(dict.fromkeys(ns.uses))
    for ref in ns.secret_ref:
        if not re.match(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", ref) or len(ref) > 63:
            raise PlatformError(f"--secret-ref '{ref}' is not a valid Secret name", hint="lowercase letters, digits and '-', e.g. pm-backend-auth")
    entry["secretRefs"] = list(dict.fromkeys(ns.secret_ref))
    if ns.expose:
        entry["expose"] = {"host": name if ns.expose is True else ns.expose}
    return entry


def resolve_slug(arg: str, org: str) -> tuple[str, str]:
    slug = arg if "/" in arg else f"{org}/{arg}"
    return slug.split("/", 1)[1], slug


def check_remote(slug: str) -> str | None:
    """Verify repo + topic via gh; returns the service's answers file text."""
    try:
        info = yaml.safe_load(gh(["repo", "view", slug, "--json", "repositoryTopics"]) or "{}")  # JSON is valid YAML
    except PlatformError:
        raise PlatformError(f"repository {slug} not found or not readable", hint=f"check the name; create it with /shared:new-service {slug.split('/')[1]} …") from None
    topics = [t["name"] for t in (info.get("repositoryTopics") or [])]
    if "deployable-service" not in topics:
        raise PlatformError(f"{slug} does not have the topic deployable-service", hint=f"gh repo edit {slug} --add-topic deployable-service")
    return repo_file(slug, ".copier-answers.yml")


def main(argv: list[str]) -> int:
    ns = build_parser().parse_args(argv)
    repo = Path(ns.repo_dir).resolve()
    app_dir = gitops.find_app(repo, ns.app)
    ans = gitops.answers(repo)
    org = ans.get("github_org", "ika100")
    registry_ns = ans.get("docker_registry", f"ghcr.io/{org}")
    if (ns.env or ns.generate or ns.secret or ns.uses or ns.secret_ref) and len(ns.services) != 1:
        raise PlatformError("--env, --generate, --secret, --secret-ref and --uses apply to exactly one service")
    if not ns.dry_run:
        gitops.require_clean(repo)
    shapes = {e["id"]: e for e in core.registry.load()}

    y, data = gitops.load(app_dir)
    services = gitops.services_of(data)
    existing = {s["name"]: s for s in services}
    # a half-migrated services.yaml cannot be rendered: refuse before touching anything, and say how to finish in one go
    v1_left = [n for n, e in existing.items() if "port" not in e and "probes" not in e and resolve_slug(n, org)[0] not in [resolve_slug(x, org)[0] for x in ns.services]]
    if v1_left and ns.action == "add":
        raise PlatformError(f"other services still use the v1 format: {', '.join(v1_left)}",
                            hint=f"migrate them together in one command: compose add {' '.join(list(ns.services) + v1_left)} --from-k8s")
    r = Report(title=f"compose {ns.action}: {', '.join(ns.services)} ({app_dir.name})")
    names: list[str] = []
    replaced: list[str] = []

    if ns.action == "add":
        new = []
        for arg in ns.services:
            name, slug = resolve_slug(arg, org)
            old = existing.get(name)
            v1 = old is not None and "port" not in old and "probes" not in old     # platform-v1 entry (remote base, `path:`)
            if old is not None and not v1:
                raise PlatformError(f"{name} is already in services.yaml", hint="edit its entry by hand, or remove it first")
            answers_text = check_remote(slug)
            shape = shape_of(answers_text, ns.shape)
            port = (yaml.safe_load(answers_text) or {}).get("port") if answers_text else None
            seed = seed_from_k8s(slug) if ns.from_k8s else {}
            entry = build_entry(name, slug, shapes[shape], port, registry_ns, ns, seed)
            if v1:  # migrate in place: keep the environments that already run (their overlays exist) and, via render, their image pins
                entry["environments"] = [e for e in gitops.ENVS if (app_dir / "overlays" / e / name).is_dir()] or ["dev"]
                replaced.append(name)
            new.append(entry)
            names.append(name)
            r.will_do.append(("migrate v1 entry of " if v1 else "add ") + f"{name} ({shape}): port {entry['port']}, image {entry['image']}, environments {entry['environments']}" + (", exposed" if "expose" in entry else "")
                             + (" — existing image pins are kept" if v1 else ""))
        if not ns.dry_run:
            for e in new:
                if e["name"] in replaced:
                    del services[[x["name"] for x in services].index(e["name"])]
                services.append(e)
            gitops.save(app_dir, y, data)
    else:
        for arg in ns.services:
            name, _ = resolve_slug(arg, org)
            if name not in existing:
                raise PlatformError(f"{name} is not in services.yaml", hint="current: " + ", ".join(existing) if existing else "services.yaml is empty")
            names.append(name)
            r.will_do.append(f"remove {name}; Argo prunes its Applications and workloads after the PR merges (prune is on)")
        if not ns.dry_run:
            for name in names:
                del services[[s["name"] for s in services].index(name)]
            gitops.save(app_dir, y, data)

    r.will_do.append("regenerate ApplicationSets and manifests (render.py)")
    if ns.pr:
        r.will_do.append("[outward] open a pull request (branch compose/…)")
    if ns.dry_run:
        r.emit(True, ns.json)
        return 0

    gitops.render(repo)
    changed = gitops.rendered_changes(repo)
    r.did.append(f"updated services.yaml and regenerated {len(changed)} file(s)")
    if ns.pr:
        title = f"feat(compose): {ns.action} {' '.join(names)}"
        url = gitops.open_pr(repo, f"compose/{ns.action}-{gitops.slug('-'.join(names))}", title, f"`/gitops:compose {ns.action} {' '.join(names)}`. Generated files regenerated by `devbox run render`.")
        r.did.append(f"opened {url}")
        r.next_steps.append("review and merge the PR; Argo syncs after the merge")
    else:
        r.next_steps.append("review `git diff`, run `devbox run validate`, then commit (or re-run with --pr)")
    if ns.action == "add":
        r.next_steps.append("adapt the entry if needed (env wiring such as API_URL, replicas, --expose); services start in dev only — `/gitops:promote` adds staging/prod")
    r.undo.append("git checkout -- . && git clean -fd applications bootstrap")
    r.data = {"services": names, "changed": changed}
    r.emit(False, ns.json)
    return 0
