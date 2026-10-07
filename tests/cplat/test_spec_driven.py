"""Spec-driven bootstrap (ADR-024): every template seeds backlog/plan and the rule; bootstrap output leads with the plan."""
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
    assert ("/app:build-feature" if shape == "gitops-app" else "/svc:plan-feature") in text


@pytest.mark.parametrize("shape", [i for i in IDS if i != "gitops-app"])
def test_service_like_templates_seed_a_backlog_with_the_story_format(shape):
    backlog = (template(shape) / "docs" / "backlog.md").read_text()
    assert "STORY-001" in backlog and "No stories yet." in backlog and "{{" not in backlog


@pytest.mark.parametrize("shape", [i for i in IDS if i != "gitops-app"])
def test_templates_never_overwrite_the_project_spec(shape):
    cfg = yaml.safe_load((template(shape) / "copier.yml").read_text())
    assert "docs/backlog.md" in cfg["_skip_if_exists"] and "docs/plan/**" in cfg["_skip_if_exists"]


def test_gitops_app_keeps_plans_project_owned():
    assert "docs/plan/**" in yaml.safe_load((template("gitops-app") / "copier.yml").read_text())["_skip_if_exists"]


@pytest.mark.parametrize("shape", [i for i in IDS if i != "gitops-app"])
def test_bootstrap_leads_with_the_plan_not_a_bare_build(shape):
    steps = newsvc._next_steps({"name": "x-svc", "shape": shape, "description": "Task API"})
    plan = next(i for i, s in enumerate(steps) if s.startswith('/svc:plan-feature "Task API"'))
    build = next(i for i, s in enumerate(steps) if s.startswith("/svc:build-feature --plan docs/plan/<slug>.md"))
    assert plan < build
    assert not any(re.match(r"/svc:build-feature (?!--plan)", s) for s in steps)


def test_gitops_bootstrap_points_to_the_product_plan():
    steps = newsvc._next_steps({"name": "shop", "shape": "gitops-app", "description": "Shop"})
    assert any(s.startswith('/app:build-feature "') for s in steps)


def test_new_app_ends_with_the_product_plan(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(newapp.newsvc, "execute", lambda req: (req["target"].mkdir(parents=True), core.Report(title="x"))[1])
    manifest = tmp_path / "app.yml"
    manifest.write_text(yaml.safe_dump({"app": "shop", "components": [{"name": "shop-api", "description": "API", "shape": "service-python"}]}))
    assert newapp.main([str(manifest), "--no-github", "--org", "acme", "--dir", str(tmp_path / "out")]) == 0
    out = capsys.readouterr().out
    assert 'cd shop and run /app:build-feature "<first feature of the product>"' in out and "/app:run-plan" in out


PLUGIN = ROOT / "plugins" / "svc"


def test_build_feature_documents_plan_and_plan_feature_points_to_it():
    build = (PLUGIN / "commands" / "build-feature.md").read_text()
    assert "[--plan <path>]" in build.splitlines()[1] and "Phase 1 skipped — --plan" in build and "Phase 2 skipped — --plan" in build
    assert "mutually exclusive with `--from-plan`" in build.lower()
    assert "--plan docs/plan/<slug>.md" in (PLUGIN / "commands" / "plan-feature.md").read_text()


def test_plans_and_stories_reference_each_other():
    assert "stories:" in (PLUGIN / "agents" / "architect.md").read_text()
    assert "STORY-NNN" in (PLUGIN / "agents" / "product-manager.md").read_text()
