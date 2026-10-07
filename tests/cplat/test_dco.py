"""scripts/check-dco.py: sign-off enforcement for pull requests."""
import importlib.util
import subprocess
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("check_dco", Path(__file__).resolve().parents[2] / "scripts" / "check-dco.py")
dco = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dco)


def git(repo, *args, env=None):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, env=env).stdout.strip()


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    for k, v in {"GIT_AUTHOR_NAME": "Ada", "GIT_AUTHOR_EMAIL": "ada@example.com", "GIT_COMMITTER_NAME": "Ada", "GIT_COMMITTER_EMAIL": "ada@example.com"}.items():
        monkeypatch.setenv(k, v)
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "commit", "-q", "--allow-empty", "-m", "base")
    return tmp_path


def commit(repo, message, **env):
    import os
    git(repo, "commit", "-q", "--allow-empty", "-m", message, env={**os.environ, **env})


def check(repo):
    return dco.problems(f"{git(repo, 'rev-parse', 'main')}..HEAD", cwd=str(repo))


def on_branch(repo):
    git(repo, "checkout", "-q", "-b", "feature")


def test_signed_commits_pass(repo):
    on_branch(repo)
    commit(repo, "feat: x\n\nSigned-off-by: Ada <ada@example.com>")
    assert check(repo) == []


def test_unsigned_commit_is_reported_with_the_fix(repo):
    on_branch(repo)
    commit(repo, "feat: x")
    problems = check(repo)
    assert len(problems) == 1 and "missing" in problems[0] and "commit --amend -s" in problems[0]


def test_trailer_must_match_author_or_committer_email(repo):
    on_branch(repo)
    commit(repo, "feat: x\n\nSigned-off-by: Mallory <mallory@example.com>")
    assert "does not match" in check(repo)[0]


def test_committer_email_is_accepted_when_the_author_differs(repo):
    on_branch(repo)
    commit(repo, "feat: x\n\nSigned-off-by: Ada <ada@example.com>", GIT_AUTHOR_NAME="Bob", GIT_AUTHOR_EMAIL="bob@example.com")
    assert check(repo) == []


def test_bot_commits_are_exempt(repo):
    on_branch(repo)
    commit(repo, "chore(deps): bump x", GIT_AUTHOR_NAME="dependabot[bot]", GIT_AUTHOR_EMAIL="49699333+dependabot[bot]@users.noreply.github.com")
    assert check(repo) == []


def test_merge_commits_are_ignored_but_their_parents_are_checked(repo):
    on_branch(repo)
    commit(repo, "feat: a\n\nSigned-off-by: Ada <ada@example.com>")
    git(repo, "checkout", "-q", "main")
    commit(repo, "main moves on")
    git(repo, "checkout", "-q", "feature")
    git(repo, "merge", "-q", "--no-ff", "main", "-m", "Merge main into feature")
    assert dco.problems(f"{git(repo, 'rev-parse', 'main')}..HEAD", cwd=str(repo)) == []


def test_main_exit_codes(repo, capsys, monkeypatch):
    monkeypatch.chdir(repo)
    on_branch(repo)
    commit(repo, "feat: unsigned")
    assert dco.main(["main..HEAD"]) == 1
    assert "CONTRIBUTING.md" in capsys.readouterr().err
