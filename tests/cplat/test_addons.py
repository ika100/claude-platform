"""Addon contract (ADR-020): app.yaml `addons` + service `uses` → CloudNativePG Cluster and env wiring."""
import subprocess

import pytest
import yaml

import addon
import compose
import core
from test_gitops import gh, gitops_repo, run_compose, render_check, services, commit  # noqa: F401  (fixtures)

APP = "applications/todo"


def app_yaml(repo):
    return yaml.safe_load((repo / APP / "app.yaml").read_text())


def render(repo):
    return subprocess.run(["uv", "run", "scripts/render.py"], cwd=repo, capture_output=True, text=True)


def declare(repo, **kw):
    assert addon.main(["add", "postgres", "--repo-dir", str(repo), *kw.get("extra", [])]) == 0
    commit(repo, "addon")


def dev_deploy(repo, svc="todo-api"):
    return yaml.safe_load((repo / APP / "overlays/dev" / svc / "deployment.yaml").read_text())


def test_addon_add_declares_it_and_keeps_comments(gitops_repo, gh):
    declare(gitops_repo, extra=["--version", "16"])
    cfg = app_yaml(gitops_repo)
    assert cfg["addons"]["postgres"]["version"] == 16 and cfg["addons"]["postgres"]["instances"] == {"dev": 1, "prod": 3}
    assert "Per-application settings" in (gitops_repo / APP / "app.yaml").read_text()


def test_service_uses_postgres_gets_env_from_the_operator_secret_and_a_cluster_is_rendered(gitops_repo, gh):
    declare(gitops_repo)
    run_compose(gitops_repo, "add", "todo-api", "--uses", "postgres")
    env = {e["name"]: e for e in dev_deploy(gitops_repo)["spec"]["template"]["spec"]["containers"][0]["env"]}
    assert env["DATABASE_URL"]["valueFrom"]["secretKeyRef"] == {"name": "todo-postgres-app", "key": "uri"}
    assert env["PGPASSWORD"]["valueFrom"]["secretKeyRef"]["key"] == "password"
    cluster = yaml.safe_load((gitops_repo / APP / "addons/dev/postgres/cluster.yaml").read_text())
    assert cluster["kind"] == "Cluster" and cluster["metadata"]["name"] == "todo-postgres"
    assert cluster["spec"]["instances"] == 1 and cluster["spec"]["storage"]["size"] == "1Gi"
    assert cluster["spec"]["imageName"].endswith("postgresql:17") and cluster["spec"]["enableSuperuserAccess"] is False
    assert cluster["spec"]["bootstrap"]["initdb"] == {"database": "todo", "owner": "todo"}
    sets = yaml.safe_load_all((gitops_repo / APP / "applicationset.yaml").read_text())
    names = [d["metadata"]["name"] for d in sets]
    assert "todo-addons-dev" in names and "todo-addons-prod" not in names
    assert render_check(gitops_repo).returncode == 0


def test_values_can_differ_per_environment(gitops_repo, gh):
    declare(gitops_repo)
    run_compose(gitops_repo, "add", "todo-api", "--uses", "postgres")
    f = gitops_repo / APP / "services.yaml"
    d = yaml.safe_load(f.read_text())
    d["services"][0]["environments"] = ["dev", "prod"]
    f.write_text(yaml.safe_dump(d))
    assert render(gitops_repo).returncode == 0
    prod = yaml.safe_load((gitops_repo / APP / "addons/prod/postgres/cluster.yaml").read_text())
    assert prod["spec"]["instances"] == 3 and prod["spec"]["storage"]["size"] == "20Gi"


def test_nothing_is_rendered_without_users_of_the_addon(gitops_repo, gh):
    declare(gitops_repo)
    run_compose(gitops_repo, "add", "todo-api")
    assert not (gitops_repo / APP / "addons").exists()


def test_removing_the_use_prunes_the_addon_files(gitops_repo, gh):
    declare(gitops_repo)
    run_compose(gitops_repo, "add", "todo-api", "--uses", "postgres")
    commit(gitops_repo)
    f = gitops_repo / APP / "services.yaml"
    d = yaml.safe_load(f.read_text())
    del d["services"][0]["uses"]
    f.write_text(yaml.safe_dump(d))
    assert render(gitops_repo).returncode == 0
    assert not (gitops_repo / APP / "addons/dev/postgres").exists()


@pytest.mark.parametrize("mutate,msg", [
    (lambda d, c: d["services"][0].update(uses=["postgres"]) or c.pop("addons", None), "does not declare"),
    (lambda d, c: d["services"][0].update(uses=["redis"]), "unknown addon 'redis'"),
    (lambda d, c: c.update(addons={"mysql": {}}), "unknown addon 'mysql'"),
    (lambda d, c: (c.update(addons={"postgres": {}}), d["services"][0].update(uses=["postgres"]), d["services"][0]["env"].update(DATABASE_URL="x")), "provided by the 'postgres' addon"),
])
def test_invalid_addon_wiring_is_rejected(gitops_repo, gh, mutate, msg):
    run_compose(gitops_repo, "add", "todo-api")
    sf, cf = gitops_repo / APP / "services.yaml", gitops_repo / APP / "app.yaml"
    d, c = yaml.safe_load(sf.read_text()), yaml.safe_load(cf.read_text()) or {}
    mutate(d, c)
    sf.write_text(yaml.safe_dump(d))
    cf.write_text(yaml.safe_dump(c))
    p = render(gitops_repo)
    assert p.returncode == 1 and msg in p.stderr


def test_addon_remove_refuses_while_in_use_and_never_touches_data(gitops_repo, gh):
    declare(gitops_repo)
    run_compose(gitops_repo, "add", "todo-api", "--uses", "postgres")
    commit(gitops_repo)
    with pytest.raises(core.PlatformError, match="still used by todo-api"):
        addon.main(["remove", "postgres", "--repo-dir", str(gitops_repo)])
    f = gitops_repo / APP / "services.yaml"
    d = yaml.safe_load(f.read_text())
    del d["services"][0]["uses"]
    f.write_text(yaml.safe_dump(d))
    commit(gitops_repo, "no use")
    assert addon.main(["remove", "postgres", "--repo-dir", str(gitops_repo)]) == 0
    assert "addons" not in app_yaml(gitops_repo)


def test_unknown_or_duplicate_addon_is_an_error(gitops_repo, gh):
    with pytest.raises(core.PlatformError, match="unknown addon"):
        addon.main(["add", "redis", "--repo-dir", str(gitops_repo)])
    declare(gitops_repo)
    with pytest.raises(core.PlatformError, match="already declared"):
        addon.main(["add", "postgres", "--repo-dir", str(gitops_repo)])


def test_uses_flag_needs_a_single_service(gitops_repo, gh):
    with pytest.raises(core.PlatformError, match="exactly one service"):
        run_compose(gitops_repo, "add", "todo-api", "todo-web", "--uses", "postgres")
