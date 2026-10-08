"""Static guards for the generated CI workflows (the publish path only runs on main/tags, so PR smoke tests never exercise it)."""
import re
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[2] / "templates"
IMAGE_TEMPLATES = ["service-python", "service-java", "service-go", "web-nextjs"]


def trivy_steps(template: str) -> list[str]:
    text = (TEMPLATES / template / ".github" / "workflows" / "ci.yml").read_text()
    steps = re.split(r"\n(?=      - )", text)
    return [s for s in steps if "aquasecurity/trivy-action" in s]


@pytest.mark.parametrize("template", IMAGE_TEMPLATES)
def test_trivy_resolves_the_digest_for_the_matrix_architecture(template):
    """Each per-arch job scans the digest it just pushed. Without TRIVY_PLATFORM Trivy looks for linux/amd64 and fails on the arm64 job
    ("no child with platform linux/amd64 in index"), so the multi-arch manifest would never be published."""
    steps = trivy_steps(template)
    assert len(steps) == 2, f"{template}: expected the scan and the SBOM step"
    for step in steps:
        assert re.search(r"TRIVY_PLATFORM: linux/\$\{\{ ('\{\{' \}\} )?matrix\.arch", step), f"{template}: a Trivy step has no TRIVY_PLATFORM"


# ---------------- spec 043: the Python templates pass their own quality gate ----------------

import shutil
import subprocess

ROOT = TEMPLATES.parent
CI = ROOT / ".github" / "workflows" / "ci.yml"


def _render(template: str, dest: Path, name: str) -> Path:
    module = name.replace("-", "_")
    subprocess.run(["uv", "tool", "run", "--from", "copier", "copier", "copy", str(TEMPLATES / template), str(dest),
                    "--defaults", "--trust", "--skip-tasks", "--data", f"project_name={name}", "--data", f"module_name={module}",
                    "--data", "description=check"], check=True, capture_output=True)
    return dest


@pytest.mark.slow
@pytest.mark.skipif(not shutil.which("uv"), reason="needs uv")
@pytest.mark.parametrize("template", ["service-python", "library-python"])
def test_rendered_python_templates_pass_ruff_and_mypy(template, tmp_path):
    """AC-043.1 AC-043.2 AC-043.4: a repo named like the run's todo-api starts lint- and type-clean."""
    repo = _render(template, tmp_path / "todo-api", "todo-api")
    for cmd in (["uv", "sync", "--all-extras", "-q"], ["uv", "run", "ruff", "check", "."], ["uv", "run", "ruff", "format", "--check", "."],
                ["uv", "run", "mypy", "src"]):
        out = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
        assert out.returncode == 0, f"{' '.join(cmd)}:\n{out.stdout[-2000:]}{out.stderr[-1000:]}"


def test_platform_ci_lints_types_and_tests_the_python_templates():
    """AC-043.3: the platform PR fails when a rendered Python template does not pass ruff, mypy or pytest."""
    job = CI.read_text().split("  smoke-test-templates:", 1)[1].split("\n  smoke-test-gitops-app:", 1)[0]
    for step in ("uv sync --all-extras", "uv run ruff check .", "uv run ruff format --check .", "uv run mypy src", "uv run pytest -q"):
        assert step in job, f"smoke-test-templates does not run `{step}`"


# ---------------- spec 059: the secrets scan scans ----------------

import json as _json

BASELINE_TEMPLATES = sorted(p.parent.name for p in TEMPLATES.glob("*/.secrets.baseline.json"))


def _baseline(t):
    return _json.loads((TEMPLATES / t / ".secrets.baseline.json").read_text())


@pytest.mark.parametrize("template", BASELINE_TEMPLATES)
def test_every_secrets_baseline_enables_the_default_plugins(template):
    """AC-059.1: an empty plugins_used makes detect-secrets print "No plugins to scan with!" and scan nothing."""
    names = {p["name"] for p in _baseline(template)["plugins_used"]}
    assert names == {p["name"] for p in _baseline("service-python")["plugins_used"]} and len(names) >= 20


@pytest.mark.skipif(not shutil.which("uvx"), reason="needs uvx")
def test_the_web_baseline_finds_a_planted_secret_quietly(tmp_path):
    """AC-059.1: no "No plugins" noise, and a real-looking key is reported."""
    shutil.copy(TEMPLATES / "web-nextjs" / ".secrets.baseline.json", tmp_path / ".secrets.baseline.json")
    (tmp_path / "clean.ts").write_text("export const greeting = 'hello';\n")
    (tmp_path / "leak.ts").write_text("const key = 'AKIAIOSFODNN7EXAMPLE';\n")
    def hook(*files):
        return subprocess.run(["uvx", "--from", "detect-secrets", "detect-secrets-hook", "--baseline", ".secrets.baseline.json", *files],
                              cwd=tmp_path, capture_output=True, text=True)
    clean = hook("clean.ts")
    assert clean.returncode == 0 and "No plugins" not in clean.stdout + clean.stderr
    leak = hook("leak.ts")
    assert leak.returncode == 1 and "AWS" in leak.stdout
