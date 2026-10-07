"""templates/gitops-app/scripts/plan.py: `ready` computes the next parallel wave of a multi-repo plan (ADR-011/023)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "templates" / "gitops-app" / "scripts" / "plan.py"

PLAN = """---
plan_id: billing
feature: add billing
gitops_app: acme/shop-gitops
status: draft
repos:
  - {id: shop-api, shape: service-java, summary: billing API, arguments: "build the API", depends_on: [], done: false}
  - {id: shop-web, shape: web-nextjs, summary: billing UI, arguments: "build the UI", depends_on: [], done: false}
  - {id: shop-lib, shape: library-python, summary: shared lib, arguments: "bump lib", depends_on: [], done: false}
  - {id: shop-e2e, shape: service-python, summary: e2e checks, arguments: "add checks", depends_on: [shop-api, shop-web], done: false}
---
## body
"""


@pytest.fixture()
def repo(tmp_path):
    (tmp_path / "scripts").mkdir()
    shutil.copy(SCRIPT, tmp_path / "scripts" / "plan.py")
    (tmp_path / "docs" / "plan").mkdir(parents=True)
    (tmp_path / "docs" / "plan" / "billing.md").write_text(PLAN)
    return tmp_path


def plan(repo, *args):
    return subprocess.run([sys.executable, str(repo / "scripts" / "plan.py"), *args], capture_output=True, text=True)


def ready(repo):
    out = plan(repo, "ready", "billing", "--json")
    assert out.returncode == 0, out.stderr
    return [r["id"] for r in json.loads(out.stdout)]


def test_independent_repos_start_together_and_dependents_wait(repo):
    assert ready(repo) == ["shop-api", "shop-lib", "shop-web"]


def test_a_dependent_becomes_ready_only_after_all_its_dependencies_are_done(repo):
    plan(repo, "done", "billing", "shop-api")
    assert ready(repo) == ["shop-lib", "shop-web"]
    plan(repo, "done", "billing", "shop-web")
    assert ready(repo) == ["shop-e2e", "shop-lib"]


def test_done_repos_are_not_offered_again(repo):
    for r in ("shop-api", "shop-web", "shop-lib", "shop-e2e"):
        plan(repo, "done", "billing", r)
    assert plan(repo, "ready", "billing").returncode == 1        # the plan is completed


def test_json_carries_the_paste_ready_prompt(repo):
    out = json.loads(plan(repo, "ready", "billing", "--json").stdout)
    assert {"id": "shop-api", "shape": "service-java", "summary": "billing API", "arguments": "build the API"} in out


def test_text_output_names_the_wave(repo):
    out = plan(repo, "ready", "billing").stdout
    assert "3 repo(s) can start now" in out and "shop-web (web-nextjs)" in out


def test_ready_rejects_abandoned_plans(repo):
    plan(repo, "abandon", "billing")
    assert plan(repo, "ready", "billing").returncode == 1
