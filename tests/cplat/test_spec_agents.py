"""Spec-driven agents (ADR-026, STORY-038): one format reference, tests first, a reviewer, no doc drift."""
import re

import pytest
import yaml

import core

ROOT = core.PLATFORM_ROOT
PLUGINS = ROOT / "plugins"
SKILL = PLUGINS / "svc" / "skills" / "spec-format"
CODE_PLUGINS = ["svc", "web", "svc-java", "svc-go"]


def front(path):
    return yaml.safe_load(path.read_text().split("---", 2)[1])


def test_every_plugin_root_reference_resolves_inside_its_plugin():
    refs = []
    for md in PLUGINS.rglob("*.md"):
        plugin = md.relative_to(PLUGINS).parts[0]
        for rel in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+[\w])", md.read_text()):
            refs.append((md, PLUGINS / plugin / rel))
    assert refs, "expected the agents to reference the spec-format skill"
    missing = [f"{md.relative_to(ROOT)} -> {target.relative_to(ROOT)}" for md, target in refs if not target.is_file()]
    assert not missing


def test_the_format_skill_covers_every_artifact():
    meta = front(SKILL / "SKILL.md")
    assert meta["name"] == "spec-format" and len(meta["description"]) < 400
    for ref in ("spec", "design", "plan", "verification", "testing"):
        assert (SKILL / "references" / f"{ref}.md").is_file()


def test_the_documented_plan_example_matches_what_cplat_checks():
    plan = (SKILL / "references" / "plan.md").read_text()
    meta = yaml.safe_load(plan.split("```yaml\n---\n", 1)[1].split("\n---\n```", 1)[0])
    assert {"spec_id", "shape", "spec_hash", "tasks"} <= set(meta)
    for task in meta["tasks"]:
        assert {"id", "title", "files", "covers", "parallel_safe", "depends_on"} <= set(task)


@pytest.mark.parametrize("agent", ["product-manager", "architect", "reviewer"])
def test_spec_agents_read_the_format_instead_of_restating_it(agent):
    text = (PLUGINS / "svc" / "agents" / f"{agent}.md").read_text()
    assert "${CLAUDE_PLUGIN_ROOT}/skills/spec-format/references/" in text
    assert "STORY-NNN" not in text and "docs/backlog.md" not in text


def test_product_manager_hands_questions_back_and_is_shape_agnostic():
    pm = (PLUGINS / "svc" / "agents" / "product-manager.md").read_text()
    assert "OPEN QUESTIONS:" in pm and "Python project" not in pm
    assert "Bash" not in front(PLUGINS / "svc" / "agents" / "product-manager.md")["tools"]


def test_reviewer_is_routed_and_cannot_edit_code():
    meta = front(PLUGINS / "svc" / "agents" / "reviewer.md")
    assert "Edit" not in meta["tools"] and meta["model"] == "opus"
    assert '"reviewer": "svc:reviewer"' in (ROOT / "scripts" / "cplat" / "shapecmd.py").read_text()


@pytest.mark.parametrize("plugin", CODE_PLUGINS)
def test_testers_write_acceptance_tests_first_in_their_idiom(plugin):
    text = (PLUGINS / plugin / "agents" / "tester.md").read_text()
    section = text.split("## Acceptance mode", 1)[1].split("\n## ", 1)[0]
    assert "AC-007.1" in section and "fail because the behaviour is missing" in section
    assert "docs/backlog.md" not in text


@pytest.mark.parametrize("plugin", CODE_PLUGINS)
def test_coders_never_weaken_acceptance_tests(plugin):
    assert "Never edit, skip or weaken them" in (PLUGINS / plugin / "agents" / "coder.md").read_text()


def test_agents_doc_matches_the_agent_files():
    """docs/AGENTS.md lists each plugin's agents with a model; both must match the files (drift found in the review)."""
    doc = (ROOT / "docs" / "AGENTS.md").read_text()
    blocks = re.split(r"^### `([\w-]+)` plugin.*$", doc, flags=re.M)
    listed = {}
    for plugin, body in zip(blocks[1::2], blocks[2::2]):
        for name, model in re.findall(r"^\| `([\w-]+)` \| (\w+) \|", body.split("\n## ", 1)[0], re.M):
            listed[(plugin, name)] = model
    actual = {(p.parent.parent.name, p.stem): front(p)["model"] for p in PLUGINS.glob("*/agents/*.md")}
    assert listed == actual


# ---------------- svc 3.0 commands (STORY-039) ----------------

COMMANDS = PLUGINS / "svc" / "commands"


@pytest.mark.parametrize("name", ["spec", "plan", "build", "verify", "specs"])
def test_spec_commands_exist_with_a_usage_line(name):
    meta = front(COMMANDS / f"{name}.md")
    assert f"/svc:{name}" in meta["description"] and len(meta["description"]) < 260


def test_spec_command_asks_the_user_and_never_approves_alone():
    text = (COMMANDS / "spec.md").read_text()
    assert "AskUserQuestion" in text and "cplat spec approve" in text and "OPEN QUESTIONS" in text
    assert "Never answer an open question on the user's behalf" in text


def test_plan_and_build_refuse_unapproved_specs():
    for name in ("plan", "build"):
        assert "spec check <id> --require approved" in (COMMANDS / f"{name}.md").read_text()


def test_build_writes_tests_first_verifies_and_resumes():
    text = (COMMANDS / "build.md").read_text()
    phases = [text.index(h) for h in ("## Phase 1 — Acceptance tests (red)", "## Phase 2 — Implement",
                                      "## Phase 3 — QA", "## Phase 4 — Verify", "## Phase 7 — Pull request")]
    assert phases == sorted(phases)
    assert "**Acceptance mode.**" in text and "agents.reviewer" in text
    assert "skip tasks with `done: true`" in text and "cplat spec task-done" in text and "set-status <id> done" in text


@pytest.mark.parametrize("name", ["quick-task", "fix-bug"])
def test_small_pipelines_stop_at_a_spec_change(name):
    assert "/svc:spec --amend <NNN>" in (COMMANDS / f"{name}.md").read_text()


# ---------------- app 1.0 commands (STORY-040) ----------------

APP = PLUGINS / "app"


@pytest.mark.parametrize("name", ["spec", "plan", "build", "specs"])
def test_app_commands_exist_with_a_usage_line(name):
    meta = front(APP / "commands" / f"{name}.md")
    assert f"/app:{name}" in meta["description"] and len(meta["description"]) < 260


def test_app_plan_and_build_need_an_approved_product_spec():
    for name in ("plan", "build"):
        assert "spec check <id> --require approved" in (APP / "commands" / f"{name}.md").read_text() \
            or "spec check <spec_id> --require approved" in (APP / "commands" / f"{name}.md").read_text()


def test_app_build_runs_each_repo_through_its_own_spec_and_never_answers_questions():
    text = (APP / "commands" / "build.md").read_text()
    assert "/svc:spec --from-plan <abs plan path> <repo-id>" in text and "never answer them" in text
    assert "never merge" in text.lower()


def test_planner_assigns_criteria_instead_of_writing_prompts():
    text = (APP / "agents" / "planner.md").read_text()
    assert "acs: [AC-<NNN>.1" in text and "spec: <PLAN_ID>" in text and "Never restate criteria in `arguments`" in text


def test_repo_specs_come_from_the_deterministic_slice():
    text = (PLUGINS / "svc" / "commands" / "spec.md").read_text()
    assert "cplat spec new --from-plan <abs plan path> <repo-id>" in text
    assert "Product context" in (PLUGINS / "svc" / "agents" / "product-manager.md").read_text()


def test_build_checks_the_worktree_base_before_fanning_out():
    """AC-044.3 AC-044.4: a probe worktree off the feature head means sequential, with the reason."""
    text = (COMMANDS / "build.md").read_text()
    probe = text.split("### 2.2 Worktree probe", 1)[1].split("### 2.3", 1)[0]
    assert "git rev-parse HEAD" in probe and "FEATURE_HEAD" in probe and 'worktree.baseRef: "head"' in probe
    assert "only that task's commits" in text


def test_app_build_runs_the_gitops_entry_itself():
    """AC-045.1 AC-045.3 AC-045.4: cplat operations in the gitops repo, merge first, no leftover worktree."""
    text = (APP / "commands" / "build.md").read_text()
    assert "cplat compose set" in text and "cplat addon add" in text and "merge first" in text and "git worktree remove" in text
    assert "never `/svc:*`" in text


def test_planner_writes_gitops_operations():
    """AC-045.2"""
    text = (APP / "agents" / "planner.md").read_text()
    assert "gitops:" in text and "{uses: postgres, service:" in text
