"""Every CI workflow re-checks a pull request when its title is edited (otherwise a fixed title can never turn green)."""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = [ROOT / ".github/workflows/ci.yml", *sorted(ROOT.glob("templates/*/.github/workflows/ci.yml"))]


def render(path: Path) -> dict:
    """Template workflows are Jinja files: undo the escapes for the GitHub expressions, drop other Jinja statements."""
    text = path.read_text()
    text = text.replace("{{ '{{' }}", "${{").replace("{{ '}}' }}", "}}")
    text = re.sub(r"\{%-?.*?-?%\}", "", text)
    text = re.sub(r"(?<!\$)\{\{.*?\}\}", "x", text)   # {{ var }} but not ${{ github expression }}
    return yaml.safe_load(text)


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: str(p.relative_to(ROOT)))
def test_title_edits_trigger_the_title_check_without_cancelling_the_build(path):
    wf = render(path)
    on = wf.get("on", wf.get(True))
    assert "edited" in on["pull_request"]["types"], "pr-title would never re-run after a title fix"
    group = wf["concurrency"]["group"]
    assert "github.event.action == 'edited'" in group, "an edit would cancel the running build"
    assert "pr-title" in wf["jobs"]
