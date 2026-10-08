"""spec (ADR-026): spec/plan validation, lifecycle, drift, test trace, backlog index, legacy migration."""
import json

import pytest

import core
import spec

SPEC = """---
spec_id: 007-price-alerts
title: Price alerts
status: {status}
priority: P1
shape: service-python
tracks: [42]
---

# 007 — Price alerts

## Problem

Traders miss moves.

## Acceptance criteria

- **AC-007.1** Given a rule, when the price crosses it, then an email is sent.
- **AC-007.2** Given a rule, when a webhook is set, then it is called.
- ~~**AC-007.3**~~ withdrawn: SMS is out of scope.

## Non-goals

- SMS

## Open questions

{questions}

## Changelog

- 2026-10-01 created
"""

PLAN = """---
spec_id: 007-price-alerts
shape: service-python
spec_hash: {hash}
tasks:
  - {{id: t1, title: model, files: [a.py], covers: [AC-007.1], parallel_safe: true, depends_on: []}}
  - {{id: t2, title: hook, files: [b.py], covers: [AC-007.2], parallel_safe: true, depends_on: []}}
  - {{id: t3, title: wire, files: [a.py, c.py], covers: [AC-007.1, AC-007.2], parallel_safe: false, depends_on: [t1, t2]}}
---

## t1 — model
"""


@pytest.fixture(autouse=True)
def no_shape(monkeypatch):
    monkeypatch.setattr(spec, "repo_shape", lambda root: None)


def make(root, status="draft", questions="None.", plan=True, hash_=None):
    d = root / "docs" / "specs" / "007-price-alerts"
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(SPEC.format(status=status, questions=questions))
    if plan:
        (d / "plan.md").write_text(PLAN.format(hash=hash_ or spec.read(d).ac_hash()))
    return spec.read(d)


def edit_plan(root, old, new):
    p = root / "docs" / "specs" / "007-price-alerts" / "plan.md"
    p.write_text(p.read_text().replace(old, new))
    return spec.read(p.parent)


# ---------------- parsing ----------------

def test_criteria_open_questions_and_withdrawn(tmp_path):
    s = make(tmp_path, questions="- Which mail provider?\n- ~~Rate limit?~~ 10/min, see AC-007.1")
    assert [a.id for a in s.acs()] == ["AC-007.1", "AC-007.2", "AC-007.3"]
    assert s.active_acs() == ["AC-007.1", "AC-007.2"]
    assert s.open_questions() == ["Which mail provider?"]


def test_a_valid_spec_and_plan_pass(tmp_path):
    assert spec.check(make(tmp_path, status="approved")) == []


def test_find_by_number_slug_or_id(tmp_path):
    make(tmp_path)
    assert {spec.find(tmp_path, r).id for r in ("7", "007", "price-alerts", "007-price-alerts")} == {"007-price-alerts"}
    with pytest.raises(core.PlatformError):
        spec.find(tmp_path, "8")


# ---------------- spec checks ----------------

def test_approval_is_refused_with_open_questions(tmp_path):
    s = make(tmp_path, questions="- Which mail provider?")
    with pytest.raises(core.PlatformError, match="open question"):
        spec.approve(s, None)
    assert spec.read(s.dir).status == "draft"


def test_approve_sets_status_and_logs_it(tmp_path):
    s = make(tmp_path)
    spec.approve(s, None)
    s = spec.read(s.dir)
    assert s.status == "approved" and "approved" in s.body.split("## Changelog")[1]


def test_approve_needs_a_criterion(tmp_path):
    s = spec.new(tmp_path, "Empty thing", shape=None, priority="P1", tracks=[], parent=None)
    assert s.acs() == [] and s.open_questions() == []  # the skeleton's examples are HTML comments
    with pytest.raises(core.PlatformError, match="at least one acceptance criterion"):
        spec.approve(s, None)


def test_require_status(tmp_path):
    s = make(tmp_path)
    assert any("needs 'approved'" in e for e in spec.check(s, require="approved"))
    assert spec.check(make(tmp_path, status="building"), require="approved") == []
    assert any("needs 'approved'" in e for e in spec.check(make(tmp_path, status="superseded"), require="approved"))


def test_foreign_or_duplicate_criterion_ids(tmp_path):
    s = make(tmp_path, plan=False)
    (s.dir / "spec.md").write_text((s.dir / "spec.md").read_text().replace("AC-007.2", "AC-008.2").replace("AC-007.3", "AC-007.1"))
    errs = spec.check(spec.read(s.dir))
    assert any("AC-008.2 belongs to spec 008" in e for e in errs)
    assert any("duplicate acceptance criterion AC-007.1" in e for e in errs)


def test_shape_must_match_the_repo(tmp_path):
    assert any("this repo is 'web-nextjs'" in e for e in spec.check(make(tmp_path), shape="web-nextjs"))


def test_folder_and_spec_id_must_agree(tmp_path):
    s = make(tmp_path, plan=False)
    (s.dir / "spec.md").write_text((s.dir / "spec.md").read_text().replace("spec_id: 007-price-alerts", "spec_id: 007-other"))
    assert any("must equal the folder name" in e for e in spec.check(spec.read(s.dir)))


# ---------------- plan checks ----------------

def test_plan_drift_is_detected(tmp_path):
    s = make(tmp_path, status="approved")
    (s.dir / "spec.md").write_text((s.dir / "spec.md").read_text().replace("an email is sent", "an email is sent within 1 min"))
    assert any("changed after this plan was written" in e for e in spec.check(spec.read(s.dir)))


def test_every_active_criterion_needs_a_task(tmp_path):
    make(tmp_path)
    s = edit_plan(tmp_path, "covers: [AC-007.1, AC-007.2]", "covers: [AC-007.1]")
    s = edit_plan(tmp_path, "covers: [AC-007.2]", "covers: []")
    assert "plan.md: AC-007.2 is not covered by any task" in spec.check(s)


def test_tasks_cannot_cover_withdrawn_or_unknown_criteria(tmp_path):
    make(tmp_path)
    s = edit_plan(tmp_path, "covers: [AC-007.2]", "covers: [AC-007.2, AC-007.3, AC-007.9]")
    errs = spec.check(s)
    assert "plan.md: task t2: covers withdrawn criterion 'AC-007.3'" in errs
    assert "plan.md: task t2: covers unknown criterion 'AC-007.9'" in errs


def test_parallel_tasks_must_not_share_files(tmp_path):
    make(tmp_path)
    s = edit_plan(tmp_path, "files: [b.py]", "files: [a.py]")
    assert any("t1 and t2 are parallel_safe at the same level but share a.py" in e for e in spec.check(s))


def test_dependency_cycle(tmp_path):
    make(tmp_path)
    s = edit_plan(tmp_path, "covers: [AC-007.1], parallel_safe: true, depends_on: []", "covers: [AC-007.1], parallel_safe: true, depends_on: [t3]")
    assert any("dependency cycle" in e for e in spec.check(s))


def test_task_done_marks_progress(tmp_path):
    s = make(tmp_path, status="building")
    spec.task_done(s, "t2")
    s = spec.read(s.dir)
    assert [t.get("done", False) for t in s.plan[0]["tasks"]] == [False, True, False]
    assert spec.check(s) == []  # the rewritten plan is still valid
    with pytest.raises(core.PlatformError):
        spec.task_done(s, "t9")


# ---------------- lifecycle ----------------

def test_transitions(tmp_path):
    s = make(tmp_path)
    with pytest.raises(core.PlatformError, match="not allowed"):
        spec.set_status(s, "approved", None)  # only through approve
    spec.approve(s, None)
    for st in ("building", "done", "draft"):  # done -> draft is an amendment
        spec.set_status(spec.read(s.dir), st, "amend" if st == "draft" else None)
    assert spec.read(s.dir).status == "draft"


@pytest.mark.parametrize("kw, step", [
    ({"questions": "- ?"}, "/svc:spec --amend 007"),
    ({}, "/svc:spec approve 007"),
    ({"status": "approved", "plan": False}, "/svc:plan 007"),
    ({"status": "building"}, "/svc:build 007"),
    ({"status": "done"}, "—"),
])
def test_next_step(tmp_path, kw, step):
    assert spec.next_step(make(tmp_path, **kw)) == step


# ---------------- new ----------------

def test_new_continues_after_legacy_story_ids(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "backlog.md").write_text("#### STORY-012 — old\n")
    s = spec.new(tmp_path, "Price Alerts!", shape="service-python", priority="P0", tracks=[3], parent=None)
    assert s.id == "013-price-alerts"
    assert s.meta == {"spec_id": "013-price-alerts", "title": "Price Alerts!", "status": "draft", "priority": "P0",
                      "shape": "service-python", "tracks": [3]}
    assert spec.check(s) == []
    assert (s.dir / "spec.md").read_text().startswith("---\nspec_id: 013-price-alerts\ntitle: Price Alerts!\n")
    assert "tracks: [3]" in (s.dir / "spec.md").read_text()


def test_slugs_are_cut_at_a_word_boundary():
    assert spec.slugify("Create a repo of any shape with one command") == "create-a-repo-of-any-shape-with-one"
    assert len(spec.slugify("x" * 60)) == 40


# ---------------- trace ----------------

def test_trace_finds_ids_in_names_and_comments_but_not_prefixes(tmp_path):
    s = make(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_alerts.py").write_text("def test_email():  # AC-007.1\n    ...\ndef test_x():  # AC-007.20\n    ...\n")
    nm = tmp_path / "tests" / "node_modules"
    nm.mkdir()
    (nm / "x.py").write_text("AC-007.2")
    assert spec.trace(tmp_path, s, ["tests/**/*.py"]) == {"AC-007.1": ["tests/test_alerts.py"], "AC-007.2": []}


def test_trace_cli_fails_on_a_missing_criterion(tmp_path, capsys):
    make(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("# AC-007.1\n")
    assert spec.main(["--repo", str(tmp_path), "trace", "7", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["missing"] == ["AC-007.2"]


def test_every_shape_declares_test_globs():
    assert all(s.get("test_globs") for s in core.registry.load() if s["status"] != "planned")


# ---------------- index / list ----------------

def test_index_keeps_text_outside_the_markers(tmp_path):
    make(tmp_path)
    (tmp_path / "docs" / "backlog.md").write_text(f"# Backlog\n\nintro\n\n{spec.START}\nold\n{spec.END}\n\n## Decisions\n\nkeep\n")
    text = spec.write_index(tmp_path).read_text()
    assert "intro" in text and "keep" in text and "old" not in text
    assert "| [007-price-alerts](specs/007-price-alerts/spec.md) — Price alerts | P1 | draft | 2 | #42 |" in text


def test_index_refuses_legacy_stories(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "backlog.md").write_text("#### STORY-001 — x\n")
    with pytest.raises(core.PlatformError, match="still holds STORY-NNN") as e:
        spec.write_index(tmp_path)
    assert "migrate" in e.value.hint


def test_list_hides_done_unless_all(tmp_path, capsys):
    make(tmp_path, status="done")
    spec.main(["--repo", str(tmp_path), "list", "--json"])
    assert json.loads(capsys.readouterr().out) == []
    spec.main(["--repo", str(tmp_path), "list", "--all", "--json"])
    assert json.loads(capsys.readouterr().out)[0]["tasks"] == 3


# ---------------- migrate ----------------

LEGACY = """# Product backlog

Intro text.

---

## Epic A. Alerts

#### STORY-004: Price alerts
**Status:** done · **Priority:** P0 · **Tracks:** #42, #43 · **Source:** PRD

As a trader, I want alerts, so that I react in time.

**Acceptance criteria:**
- [x] An email is sent.
- [ ] A webhook is called.

## Epic B. Reports

### Notes on reports

Keep me.

#### STORY-005 — Reports
**Status:** open · **Priority:** P2

As a user, I want reports.

## Decisions

1. keep this
"""


def test_migrate_dry_run_writes_nothing(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "backlog.md").write_text(LEGACY)
    out = spec.migrate(tmp_path, None, write=False)
    assert out[0] == "would create docs/specs/004-price-alerts/spec.md  [done, 2 criteria]"
    assert not (tmp_path / "docs" / "specs").exists()


def test_migrate_converts_stories_and_keeps_other_sections(tmp_path):
    (tmp_path / "docs" / "plan").mkdir(parents=True)
    (tmp_path / "docs" / "backlog.md").write_text(LEGACY)
    (tmp_path / "docs" / "plan" / "alerts.md").write_text("---\nplan_id: alerts\nstories: [STORY-004]\n---\n")
    spec.migrate(tmp_path, "service-python", write=True)
    a = spec.find(tmp_path, "4")
    assert a.meta == {"spec_id": "004-price-alerts", "title": "Price alerts", "status": "done", "priority": "P0",
                      "shape": "service-python", "tracks": [42, 43]}
    assert a.active_acs() == ["AC-004.1", "AC-004.2"]
    assert "Legacy plan: `docs/plan/alerts.md`" in a.body and "**Source:** PRD" in a.body
    b = spec.find(tmp_path, "5")
    assert b.status == "draft" and b.acs() == [] and "As a user" in b.body
    assert spec.check(a) == [] and spec.check(b) == []
    backlog = (tmp_path / "docs" / "backlog.md").read_text()
    assert "STORY-00" not in backlog and "Intro text." in backlog and "1. keep this" in backlog
    assert "## Epic A" not in backlog                       # emptied by the move
    assert "## Epic B" in backlog and "Keep me." in backlog  # still has content
    assert backlog.index(spec.START) < backlog.index("## Epic B") and "004-price-alerts" in backlog
    with pytest.raises(core.PlatformError, match="no STORY-NNN"):
        spec.migrate(tmp_path, None, write=True)
