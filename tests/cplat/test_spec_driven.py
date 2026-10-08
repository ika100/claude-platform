"""Spec-driven bootstrap (ADR-024, ADR-026): every template seeds the spec index and the rule; bootstrap output leads with the spec."""
import re

import pytest
import yaml

import core
import newapp
import newsvc

ROOT = core.PLATFORM_ROOT
SHAPES = [s for s in core.registry.load() if s["status"] != "planned"]
IDS = [s["id"] for s in SHAPES]


def template(shape_id):
    return ROOT / "templates" / next(s["template"] for s in SHAPES if s["id"] == shape_id)


def claude_md(shape_id):
    t = template(shape_id)
    return next(p for p in (t / "CLAUDE.md", t / "CLAUDE.md.jinja") if p.is_file()).read_text()


@pytest.mark.parametrize("shape", IDS)
def test_template_seeds_plan_dir_and_the_spec_first_rule(shape):
    t = template(shape)
    assert (t / "docs" / "plan").is_dir()
    text = claude_md(shape)
    assert "### Spec first" in text
    assert ("/app:spec <description>" if shape == "gitops-app" else "/svc:spec <description>") in text
    assert "plan-feature" not in text and "build-feature --" not in text


@pytest.mark.parametrize("shape", [i for i in IDS if i != "gitops-app"])
def test_service_like_templates_seed_the_generated_spec_index(shape, tmp_path):
    import spec
    backlog = (template(shape) / "docs" / "backlog.md").read_text()
    assert "STORY-" not in backlog and "{{" not in backlog
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "backlog.md").write_text(backlog)
    assert spec.write_index(tmp_path).read_text() == backlog  # the seed is exactly what `cplat spec index` writes


@pytest.mark.parametrize("shape", [i for i in IDS if i != "gitops-app"])
def test_templates_never_overwrite_the_project_spec(shape):
    cfg = yaml.safe_load((template(shape) / "copier.yml").read_text())
    assert "docs/backlog.md" in cfg["_skip_if_exists"] and "docs/plan/**" in cfg["_skip_if_exists"]


def test_gitops_app_keeps_plans_project_owned():
    assert "docs/plan/**" in yaml.safe_load((template("gitops-app") / "copier.yml").read_text())["_skip_if_exists"]


@pytest.mark.parametrize("shape", [i for i in IDS if i != "gitops-app"])
def test_bootstrap_leads_with_the_plan_not_a_bare_build(shape):
    steps = newsvc._next_steps({"name": "x-svc", "shape": shape, "description": "Task API"})
    order = [next(i for i, s in enumerate(steps) if s.startswith(p)) for p in ('/svc:spec "Task API"', "/svc:plan <NNN>", "/svc:build <NNN>")]
    assert order == sorted(order)
    assert not any(re.search(r"build-feature|plan-feature", s) for s in steps)


def test_gitops_bootstrap_points_to_the_product_plan():
    steps = newsvc._next_steps({"name": "shop", "shape": "gitops-app", "description": "Shop"})
    assert any(s.startswith('/app:spec "') for s in steps)


def test_new_app_ends_with_the_product_plan(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(newapp.newsvc, "execute", lambda req: (req["target"].mkdir(parents=True), core.Report(title="x"))[1])
    manifest = tmp_path / "app.yml"
    manifest.write_text(yaml.safe_dump({"app": "shop", "components": [{"name": "shop-api", "description": "API", "shape": "service-python"}]}))
    assert newapp.main([str(manifest), "--no-github", "--org", "acme", "--dir", str(tmp_path / "out")]) == 0
    out = capsys.readouterr().out
    assert 'cd shop and run /app:spec "<first feature of the product>"' in out and "/app:build <NNN>" in out


PLUGIN = ROOT / "plugins" / "svc"


def test_the_old_commands_are_gone_and_nothing_points_to_them():
    """svc 3.0 (ADR-026) replaced plan-feature and build-feature; no command, agent, template or script may still name them."""
    assert not (PLUGIN / "commands" / "build-feature.md").exists() and not (PLUGIN / "commands" / "plan-feature.md").exists()
    assert sorted(p.stem for p in (ROOT / "plugins" / "app" / "commands").glob("*.md")) == ["build", "plan", "spec", "specs"]
    stale = [str(p.relative_to(ROOT)) for d in ("plugins", "templates", "scripts") for p in (ROOT / d).rglob("*")
             if p.is_file() and p.suffix in {".md", ".jinja", ".py", ".json"} and "__pycache__" not in p.parts
             and re.search(r"/svc:(plan-feature|build-feature)|/app:(build-feature|run-plan|plans)\b", p.read_text(errors="ignore"))]
    assert stale == []


def test_plans_cover_the_criteria_of_their_spec():
    """ADR-026 replaced ADR-024's `stories:` link: plans cite criteria (`covers`) and record the spec they came from."""
    plan = (PLUGIN / "skills" / "spec-format" / "references" / "plan.md").read_text()
    assert "covers:" in plan and "spec_hash:" in plan
    assert "AC-<NNN>.<n>" in (PLUGIN / "agents" / "product-manager.md").read_text()


# ---------------- spec contract in every template (STORY-041) ----------------

SPEC_FILES = ["docs/specs/README.md", "scripts/spec-check.sh", ".github/workflows/specs.yml"]


@pytest.mark.parametrize("rel", SPEC_FILES)
def test_every_template_ships_the_same_spec_files(rel):
    copies = {(template(s) / rel).read_text() for s in IDS}
    assert len(copies) == 1, f"{rel} differs between templates"
    text = copies.pop()
    assert "{{" not in text and "{%" not in text and "{#" not in text  # rendered verbatim by templates without a suffix


def test_the_spec_workflow_warns_and_uses_pinned_actions():
    wf = yaml.safe_load((template("service-python") / ".github" / "workflows" / "specs.yml").read_text())
    steps = wf["jobs"]["spec-check"]["steps"]
    assert all(re.search(r"@[0-9a-f]{40}$", s["uses"]) for s in steps if "uses" in s)
    assert steps[-1]["run"] == "bash scripts/spec-check.sh" and wf["permissions"] == {"contents": "read"}


def test_spec_check_script_uses_the_repos_platform_version_and_warns_by_default():
    sh = (template("service-go") / "scripts" / "spec-check.sh").read_text()
    assert "sed -n 's/^ref: *//p' .platform-version" in sh and "spec ci" in sh and "SPEC_CHECK_STRICT" in sh
    assert "|| true; } | head -1" in sh  # a repo without .platform-version must not end the script under pipefail


@pytest.mark.parametrize("shape", IDS)
def test_specs_are_project_owned_and_checkable_locally(shape):
    t = template(shape)
    assert "docs/specs/**" in yaml.safe_load((t / "copier.yml").read_text())["_skip_if_exists"]
    devbox = next(p for p in (t / "devbox.json", t / "devbox.json.jinja") if p.is_file()).read_text()
    assert '"spec-check":' in devbox and "bash scripts/spec-check.sh" in devbox


SPEC_MD = """---
spec_id: 001-ping
title: Ping
status: building
priority: P1
---

## Acceptance criteria

- **AC-001.1** Given the service, when GET /ping, then 200.
- **AC-001.2** Given the service, when POST /ping, then 405.
"""


@pytest.mark.skipif(not __import__("shutil").which("uv"), reason="needs uv")
def test_spec_check_script_warns_then_fails_strict_then_passes(tmp_path):
    import subprocess
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "spec-check.sh").write_text((template("service-python") / "scripts" / "spec-check.sh").read_text())
    (tmp_path / "docs" / "specs" / "001-ping").mkdir(parents=True)
    (tmp_path / "docs" / "specs" / "001-ping" / "spec.md").write_text(SPEC_MD)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_ping.py").write_text("def test_get():  # AC-001.1\n    pass\n")

    def check(strict=False):
        env = {**__import__("os").environ, "SPEC_CHECK_PLATFORM": str(ROOT), "SPEC_CHECK_STRICT": "1" if strict else ""}
        return subprocess.run(["bash", "scripts/spec-check.sh"], cwd=tmp_path, env=env, capture_output=True, text=True)

    warn = check()  # no .platform-version: the script must still run (pipefail regression)
    assert warn.returncode == 0 and "::warning" in warn.stdout and "AC-001.2 is not named by any test" in warn.stdout
    assert check(strict=True).returncode == 1
    (tmp_path / "tests" / "test_ping.py").write_text("def test_get():  # AC-001.1\n    pass\ndef test_post():  # AC-001.2\n    pass\n")
    ok = check(strict=True)
    assert ok.returncode == 0 and "0 problem(s)" in ok.stdout
