"""Kyverno guard rails (ADR-022): rendering per environment, and evaluation of rendered manifests with the Kyverno CLI."""
import copy
import shutil
import subprocess

import pytest
import yaml

from test_gitops import gh, gitops_repo, run_compose, render_check, commit  # noqa: F401  (fixtures)

APP = "applications/todo"
needs_kyverno = pytest.mark.skipif(shutil.which("kyverno") is None, reason="the Kyverno CLI is not installed (CI always has it)")


def app_cfg(repo, **extra):
    f = repo / APP / "app.yaml"
    cfg = yaml.safe_load(f.read_text()) or {}
    cfg.update(extra)
    f.write_text(yaml.safe_dump(cfg))
    commit(repo, "cfg")


def render(repo):
    return subprocess.run(["uv", "run", "scripts/render.py"], cwd=repo, capture_output=True, text=True)


def policy(repo, env="dev"):
    return yaml.safe_load((repo / APP / "policies" / env / "policy.yaml").read_text())


def set_envs(repo, envs):
    f = repo / APP / "services.yaml"
    d = yaml.safe_load(f.read_text())
    d["services"][0]["environments"] = envs
    f.write_text(yaml.safe_dump(d))


def test_nothing_without_the_policies_key(gitops_repo, gh):
    run_compose(gitops_repo, "add", "todo-api")
    assert not (gitops_repo / APP / "policies").exists()
    assert "policies" not in (gitops_repo / APP / "applicationset.yaml").read_text().replace("# policies:", "")


def test_enabled_with_defaults_audit_in_dev_enforce_in_prod(gitops_repo, gh):
    app_cfg(gitops_repo, policies={})
    run_compose(gitops_repo, "add", "todo-api")
    set_envs(gitops_repo, ["dev", "staging", "prod"])
    assert render(gitops_repo).returncode == 0
    modes = {e: policy(gitops_repo, e)["spec"]["validationActions"] for e in ("dev", "staging", "prod")}
    assert modes == {"dev": ["Audit"], "staging": ["Audit"], "prod": ["Deny"]}
    p = policy(gitops_repo, "prod")
    assert p["kind"] == "NamespacedValidatingPolicy" and p["metadata"]["namespace"] == "todo-prod"
    sets = [d["metadata"]["name"] for d in yaml.safe_load_all((gitops_repo / APP / "applicationset.yaml").read_text())]
    assert {"todo-policies-dev", "todo-policies-staging", "todo-policies-prod"} <= set(sets)
    assert render_check(gitops_repo).returncode == 0


def test_latest_is_only_forbidden_outside_dev(gitops_repo, gh):
    app_cfg(gitops_repo, policies={})
    run_compose(gitops_repo, "add", "todo-api")
    set_envs(gitops_repo, ["dev", "staging"])
    assert render(gitops_repo).returncode == 0
    msgs = lambda env: [v["message"] for v in policy(gitops_repo, env)["spec"]["validations"]]  # noqa: E731
    assert not any("latest" in m for m in msgs("dev"))
    assert any("latest" in m for m in msgs("staging"))


def test_modes_per_environment_and_off_prunes(gitops_repo, gh):
    app_cfg(gitops_repo, policies={"mode": {"dev": "Enforce", "staging": "Off"}})
    run_compose(gitops_repo, "add", "todo-api")
    set_envs(gitops_repo, ["dev", "staging"])
    assert render(gitops_repo).returncode == 0
    assert policy(gitops_repo, "dev")["spec"]["validationActions"] == ["Deny"]
    assert not (gitops_repo / APP / "policies/staging").exists()


def test_allowed_registries_follow_the_images_and_addons(gitops_repo, gh):
    app_cfg(gitops_repo, policies={"registries": ["registry.example.com/team/"]}, addons={"observability": {}})
    run_compose(gitops_repo, "add", "todo-api")
    regs = yaml.safe_load(policy(gitops_repo)["spec"]["variables"][1]["expression"])
    assert regs == ["ghcr.io/acme/", "otel/", "registry.example.com/team/"]


def test_removing_the_policies_key_prunes_the_files(gitops_repo, gh):
    app_cfg(gitops_repo, policies={})
    run_compose(gitops_repo, "add", "todo-api")
    commit(gitops_repo)
    f = gitops_repo / APP / "app.yaml"
    cfg = yaml.safe_load(f.read_text())
    del cfg["policies"]
    f.write_text(yaml.safe_dump(cfg))
    assert render(gitops_repo).returncode == 0
    assert not (gitops_repo / APP / "policies").exists()


@pytest.mark.parametrize("conf,msg", [({"mode": {"dev": "Block"}}, "must be Audit, Enforce or Off"), ({"registries": "ghcr.io"}, "list of image prefixes")])
def test_invalid_policy_config_is_rejected(gitops_repo, gh, conf, msg):
    run_compose(gitops_repo, "add", "todo-api")
    commit(gitops_repo)
    app_cfg(gitops_repo, policies=conf)
    p = render(gitops_repo)
    assert p.returncode == 1 and msg in p.stderr


# ---- evaluation with the real Kyverno CLI (offline) ----

def evaluate(tmp_path, repo, resource, env="dev"):
    f = tmp_path / "resource.yaml"
    f.write_text(yaml.safe_dump(resource))
    out = subprocess.run(["kyverno", "apply", str(repo / APP / "policies" / env / "policy.yaml"), "--resource", str(f)], capture_output=True, text=True)
    return out.returncode == 0 and "fail: 0" in out.stdout and "error: 0" in out.stdout, out.stdout + out.stderr


def good_deployment(repo, env="dev"):
    d = yaml.safe_load((repo / APP / "overlays" / env / "todo-api" / "deployment.yaml").read_text())
    d["spec"]["template"]["spec"]["containers"][0]["image"] = "ghcr.io/acme/todo-api:sha-abc1234"
    return d


MUTATIONS = {
    "root user": ("non-root", lambda c, p, d: c["securityContext"].update(runAsUser=0)),
    "writable root fs": ("readOnlyRootFilesystem", lambda c, p, d: c["securityContext"].update(readOnlyRootFilesystem=False)),
    "privilege escalation": ("allowPrivilegeEscalation", lambda c, p, d: c["securityContext"].update(allowPrivilegeEscalation=True)),
    "capabilities kept": ("drop ALL", lambda c, p, d: c["securityContext"].pop("capabilities")),
    "privileged": ("privileged containers", lambda c, p, d: c["securityContext"].update(privileged=True)),
    "host network": ("privileged containers", lambda c, p, d: p.update(hostNetwork=True)),
    "hostPath": ("hostPath", lambda c, p, d: p.update(volumes=[{"name": "h", "hostPath": {"path": "/"}}])),
    "no memory limit": ("requests and a memory limit", lambda c, p, d: c.pop("resources")),
    "no part-of label": ("part-of", lambda c, p, d: d["metadata"]["labels"].pop("app.kubernetes.io/part-of")),
    "foreign registry": ("allowed registry", lambda c, p, d: c.update(image="docker.io/evil/x:1")),
}


@needs_kyverno
def test_a_rendered_deployment_passes_and_each_violation_is_caught(tmp_path, gitops_repo, gh):
    app_cfg(gitops_repo, policies={})
    run_compose(gitops_repo, "add", "todo-api")
    ok, out = evaluate(tmp_path, gitops_repo, good_deployment(gitops_repo))
    assert ok, out
    for name, (expect, mutate) in MUTATIONS.items():
        d = copy.deepcopy(good_deployment(gitops_repo))
        mutate(d["spec"]["template"]["spec"]["containers"][0], d["spec"]["template"]["spec"], d)
        ok, out = evaluate(tmp_path, gitops_repo, d)
        assert not ok and expect in out, f"{name}: expected a violation mentioning '{expect}'\n{out}"


@needs_kyverno
def test_latest_and_untagged_images_fail_outside_dev(tmp_path, gitops_repo, gh):
    app_cfg(gitops_repo, policies={})
    run_compose(gitops_repo, "add", "todo-api")
    set_envs(gitops_repo, ["dev", "staging"])
    assert render(gitops_repo).returncode == 0
    for image in ("ghcr.io/acme/todo-api:latest", "ghcr.io/acme/todo-api"):
        d = good_deployment(gitops_repo, "staging")
        d["spec"]["template"]["spec"]["containers"][0]["image"] = image
        ok, out = evaluate(tmp_path, gitops_repo, d, "staging")
        assert not ok and "latest" in out, image
    ok, out = evaluate(tmp_path, gitops_repo, good_deployment(gitops_repo, "staging"), "staging")
    assert ok, out


@needs_kyverno
def test_the_otel_collector_satisfies_the_guard_rails(tmp_path, gitops_repo, gh):
    app_cfg(gitops_repo, policies={}, addons={"observability": {}})
    run_compose(gitops_repo, "add", "todo-api")
    dep = yaml.safe_load((gitops_repo / APP / "addons/dev/observability/collector.yaml").read_text())
    ok, out = evaluate(tmp_path, gitops_repo, dep)
    assert ok, out
