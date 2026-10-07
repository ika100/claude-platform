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
