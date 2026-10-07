"""new-service: parsing, shape routing, and a real local render (no GitHub)."""
import subprocess
from pathlib import Path

import pytest

import core
import newsvc


def resolve(*argv, **kw):
    return newsvc.resolve([*argv, "--no-github", "--org", "acme", *kw.get("extra", [])])


def test_defaults_to_service_python_with_python_answers():
    r = resolve("my-api", "A", "thing")
    assert r["shape"] == "service-python"
    assert r["description"] == "A thing"
    assert r["data"]["module_name"] == "my_api" and r["data"]["python_version"] == "3.12"


@pytest.mark.parametrize("flag,shape", [("--web", "web-nextjs"), ("--gitops", "gitops-app"), ("--library", "library-python")])
def test_aliases(flag, shape):
    assert resolve("x1", "desc", flag)["shape"] == shape


def test_flags_may_appear_anywhere():
    r = resolve("--web", "my-web", "Frontend", "app")
    assert (r["name"], r["description"], r["shape"]) == ("my-web", "Frontend app", "web-nextjs")


def test_non_python_shapes_do_not_get_module_name_or_python_version():
    """Regression: module_name=my_saas turned the Go module path into `my_saas`."""
    for shape in ("service-go", "service-java", "web-nextjs", "gitops-app"):
        data = resolve("my-saas", "d", "--type", shape)["data"]
        assert "module_name" not in data and "python_version" not in data, shape


@pytest.mark.parametrize("argv,msg", [
    (["Bad_Name", "d"], "invalid project name"),
    (["ok"], "description is required"),
    ([], "name is required"),
    (["ok", "d", "--web", "--gitops"], "conflicting"),
    (["ok", "d", "--type", "nope"], "unknown shape"),
])
def test_bad_input_has_a_clear_error(argv, msg):
    with pytest.raises(core.PlatformError, match=msg):
        resolve(*argv)


def test_errors_carry_a_hint():
    with pytest.raises(core.PlatformError) as e:
        resolve("Bad_Name", "d")
    assert e.value.hint


def test_app_is_ignored_for_non_deployable_shapes():
    r = resolve("g1", "d", "--gitops", "--app", "acme/g1")
    assert r["app"] is None and r["ignored_app"]
    assert resolve("s1", "d", "--app", "acme/g1")["app"] == "acme/g1"


def test_existing_nonempty_target_is_refused(tmp_path):
    (tmp_path / "taken").mkdir()
    (tmp_path / "taken" / "file").write_text("x")
    with pytest.raises(core.PlatformError, match="not empty"):
        resolve("taken", "d", extra=["--dir", str(tmp_path)])


def test_dry_run_makes_no_changes(tmp_path, capsys):
    assert newsvc.main(["dry-1", "d", "--web", "--no-github", "--dry-run", "--dir", str(tmp_path)]) == 0
    assert not (tmp_path / "dry-1").exists()
    assert "dry run" in capsys.readouterr().out


@pytest.mark.slow
def test_real_local_render_of_each_shape(tmp_path):
    for shape in ("gitops-app", "service-go"):
        name = f"t-{shape}"
        newsvc.main([name, "desc", "--type", shape, "--no-github", "--skip-tasks", "--dir", str(tmp_path), "--org", "acme", "--app", "acme/app-gitops"])
        repo = tmp_path / name
        answers = (repo / ".copier-answers.yml").read_text()
        assert f"_src_path: gh:ika100/sdlc-foundry/templates/{shape}" in answers  # stable, not a temp path
        assert core.read_stamp(repo)["shape"] == shape
        log = subprocess.run(["git", "log", "--format=%s"], cwd=repo, text=True, capture_output=True).stdout.splitlines()
        assert log == [f"chore: bootstrap from {shape} template"]
        assert subprocess.run(["bash", str(core.PLATFORM_ROOT / "scripts/detect-shape.sh"), str(repo)], text=True, capture_output=True).stdout.strip() == shape
    assert "module github.com/acme/t-service-go" in (tmp_path / "t-service-go" / "go.mod").read_text()
    assert not (tmp_path / "t-service-go" / ".platform-app.yml").exists() or "acme/app-gitops" in (tmp_path / "t-service-go" / ".platform-app.yml").read_text()


# ---------------- visibility and template options ----------------

def test_public_flag_is_shown_in_the_preview_and_used_for_the_github_repo(tmp_path, monkeypatch, capsys):
    import subprocess

    calls = []
    real_run = newsvc.run

    def fake_run(cmd, **kw):
        if cmd[0] == "gh":
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return real_run(cmd, **kw)

    monkeypatch.setattr(newsvc, "run", fake_run)
    monkeypatch.setattr(newsvc.core, "has_gh", lambda: True)
    assert newsvc.main(["pubsvc", "d", "--public", "--skip-tasks", "--dir", str(tmp_path), "--org", "acme", "--dry-run"]) == 0
    assert "create PUBLIC GitHub repo acme/pubsvc" in capsys.readouterr().out
    assert newsvc.main(["pubsvc", "d", "--public", "--skip-tasks", "--dir", str(tmp_path), "--org", "acme"]) == 0
    create = next(c for c in calls if c[:3] == ["gh", "repo", "create"])
    assert "--public" in create and "--private" not in create


def test_private_stays_the_default(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(newsvc.core, "has_gh", lambda: True)
    assert newsvc.main(["privsvc", "d", "--skip-tasks", "--dir", str(tmp_path), "--org", "acme", "--dry-run"]) == 0
    assert "create PRIVATE GitHub repo" in capsys.readouterr().out


def test_public_conflicts_are_rejected():
    with pytest.raises(core.PlatformError, match="conflicts"):
        newsvc.resolve(["x-svc", "d", "--public", "--visibility", "private"])
    with pytest.raises(core.PlatformError, match="needs a GitHub repository"):
        newsvc.resolve(["x-svc", "d", "--public", "--no-github"])


def test_data_sets_template_options_and_rejects_unknown_ones(tmp_path):
    req = newsvc.resolve(["opt-svc", "d", "--type", "service-java", "--data", "needs_observability=false", "--dir", str(tmp_path)])
    assert req["data"]["needs_observability"] == "false" and "needs_observability" in req["set_keys"]
    with pytest.raises(core.PlatformError) as e:
        newsvc.resolve(["opt-svc", "d", "--type", "service-java", "--data", "needs_everything=true"])
    assert "no option 'needs_everything'" in str(e.value) and "needs_observability" in (e.value.hint or "")
    with pytest.raises(core.PlatformError, match="KEY=VALUE"):
        newsvc.resolve(["opt-svc", "d", "--data", "oops"])


def test_next_steps_tell_the_agent_to_start_a_feature_without_waiting_for_ci():
    steps = newsvc._next_steps({"name": "svc-a", "shape": "service-python", "description": "Task API"})
    joined = "\n".join(steps)
    assert "/svc:build-feature --plan" in joined and "do not wait" in joined
