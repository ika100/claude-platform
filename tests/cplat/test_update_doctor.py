"""update-service on a repo made by new-service, changelog helpers, doctor logic."""
import subprocess
from pathlib import Path

import pytest

import core
import doctor
import newsvc
import update


def git(repo, *a):
    return subprocess.run(["git", *a], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()


@pytest.fixture()
def repo(tmp_path):
    newsvc.main(["upd-go", "desc", "--type", "service-go", "--no-github", "--skip-tasks", "--dir", str(tmp_path), "--org", "acme"])
    return tmp_path / "upd-go"


def test_update_restores_skeleton_keeps_project_files(repo):
    (repo / ".golangci.yml").write_text("# local tweak\n")            # skeleton file → must be overwritten
    (repo / "internal/server/server.go").write_text("// mine\n")      # project-owned → must survive
    (repo / ".platform-version").write_text("platform: 1.0.0\nshape: service-go\nref: main\n")
    git(repo, "add", "-A"); git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "tweak")
    assert update.main(["--repo", str(repo), "--skip-tasks"]) == 0
    assert "tweak" not in (repo / ".golangci.yml").read_text()
    assert (repo / "internal/server/server.go").read_text() == "// mine\n"
    assert git(repo, "branch", "--show-current").startswith("chore/platform-update-")
    assert git(repo, "log", "-1", "--format=%s").startswith("chore: update skeleton from platform")
    assert "_src_path: gh:ika100/claude-platform/templates/service-go" in (repo / ".copier-answers.yml").read_text()
    assert core.read_stamp(repo)["platform"] == core.platform_version()


def test_update_refuses_dirty_tree(repo):
    (repo / "x").write_text("dirty")
    with pytest.raises(core.PlatformError, match="uncommitted"):
        update.resolve(["--repo", str(repo)])


def test_update_requires_answers_file(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    with pytest.raises(core.PlatformError, match="copier-answers"):
        update.resolve(["--repo", str(tmp_path)])


def test_update_data_must_be_key_value(repo):
    with pytest.raises(core.PlatformError, match="KEY=VALUE"):
        update.resolve(["--repo", str(repo), "--data", "oops"])


def test_update_dry_run_changes_nothing(repo, capsys):
    head = git(repo, "rev-parse", "HEAD")
    assert update.main(["--repo", str(repo), "--dry-run"]) == 0
    assert git(repo, "rev-parse", "HEAD") == head and git(repo, "branch", "--show-current") == "main"
    assert "OVERWRITE" in capsys.readouterr().out


def test_changelog_between_selects_the_right_sections():
    text = core.changelog_between("1.0.1", "1.1.1")
    assert "[1.1.1]" in text and "[1.1.0]" in text and "[1.0.1]" not in text
    assert core.changelog_between(None, "1.0.0").count("## [") >= 1


def test_vtuple_orders_numerically():
    assert core.vtuple("1.10.0") > core.vtuple("1.9.9")


def test_doctor_flags_stale_plugins(monkeypatch):
    monkeypatch.setattr(doctor, "installed_plugins", lambda: {"shared": "0.3.1"})
    res = doctor.check_plugins()
    assert res[0]["status"] == doctor.WARN and "RESTART" in res[0]["fix"]


def test_doctor_kube_context_warns_when_not_local(monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda t: "/usr/bin/kubectl")
    monkeypatch.setattr(doctor, "run", lambda *a, **k: type("P", (), {"stdout": "prod-eu-1\n", "returncode": 0})())
    assert doctor.check_kube()[0]["status"] == doctor.WARN
    monkeypatch.setattr(doctor, "run", lambda *a, **k: type("P", (), {"stdout": "k3d-todo-local\n", "returncode": 0})())
    assert doctor.check_kube()[0]["status"] == doctor.OK


def test_doctor_repo_stamp(repo):
    (repo / ".platform-version").write_text("platform: 0.9.0\nshape: service-go\nref: main\n")
    assert any(c["name"] == "repo platform version" and c["status"] == doctor.WARN for c in doctor.check_repo(repo))


def test_update_on_fresh_repo_is_a_noop_and_leaves_no_branch(repo):
    head = git(repo, "rev-parse", "HEAD")
    update.main(["--repo", str(repo), "--skip-tasks"])
    assert git(repo, "branch", "--show-current") == "main"
    assert git(repo, "branch", "--list", "chore/platform-update-*") == ""
    # the stamp is rewritten identically, so nothing differs and no commit is made
    assert git(repo, "rev-parse", "HEAD") == head


def test_shape_routing(repo, tmp_path):
    import shapecmd
    r = shapecmd.route(repo)
    assert r["shape"] == "service-go" and r["agents"]["coder"] == "svc-go:coder" and r["agents"]["architect"] == "svc:architect"
    newsvc.main(["g-app", "d", "--gitops", "--no-github", "--skip-tasks", "--dir", str(tmp_path), "--org", "acme"])
    g = shapecmd.route(tmp_path / "g-app")
    assert g["shape"] == "gitops-app" and "deployment" not in g["agents"] and "unsupported" in g


def test_python_service_routes_to_svc_with_migrations(tmp_path):
    import shapecmd
    newsvc.main(["py-svc", "d", "--no-github", "--skip-tasks", "--dir", str(tmp_path), "--org", "acme"])
    r = shapecmd.route(tmp_path / "py-svc")
    assert r["agents"]["coder"] == "svc:coder" and r["agents"]["migrations"] == "svc:migrations"


def test_migrate_removes_k8s_dir_and_stamp_is_current(repo):
    (repo / "k8s" / "base").mkdir(parents=True)
    (repo / "k8s" / "base" / "deployment.yaml").write_text("kind: Deployment\n")
    git(repo, "add", "-A"); git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v1 k8s")
    update.main(["--repo", str(repo), "--skip-tasks", "--migrate"])
    assert not (repo / "k8s").exists()
    assert git(repo, "log", "-1", "--format=%s").startswith("chore: update skeleton")


def test_without_migrate_k8s_dir_is_left_alone(repo):
    (repo / "k8s").mkdir()
    (repo / "k8s" / "x.yaml").write_text("a: b\n")
    git(repo, "add", "-A"); git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "k8s")
    (repo / ".platform-version").write_text("platform: 1.0.0\nshape: service-go\nref: main\n")
    git(repo, "add", "-A"); git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "old stamp")
    update.main(["--repo", str(repo), "--skip-tasks"])
    assert (repo / "k8s" / "x.yaml").exists()


def test_second_update_the_same_day_gets_a_unique_branch(repo):
    base = update.branch_name()
    git(repo, "branch", base)                      # e.g. yesterday's merged update branch with today's name
    assert update.branch_name(repo) == base + "-2"
    git(repo, "branch", base + "-2")
    assert update.branch_name(repo) == base + "-3"
