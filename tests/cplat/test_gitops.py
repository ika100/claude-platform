"""compose + promote against a real rendered gitops-app repo with `gh` faked."""
import base64
import json
import subprocess

import pytest
import yaml

import compose
import core
import newsvc
import promote

JAVA_ANSWERS = "_src_path: gh:ika100/claude-platform/templates/service-java\nport: 8080\n"
WEB_ANSWERS = "_src_path: gh:ika100/claude-platform/templates/web-nextjs\nport: 3000\n"
OLD_K8S = """
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: app
          ports: [{containerPort: 3000}]
          env: [{name: PORT, value: "3000"}, {name: API_URL, value: "http://todo-api"}]
          livenessProbe: {httpGet: {path: /api/health, port: http}}
          readinessProbe: {httpGet: {path: /api/ready, port: http}}
          resources: {requests: {cpu: 10m, memory: 10Mi}}
"""
SHA = "a" * 40


@pytest.fixture()
def gitops_repo(tmp_path):
    newsvc.main(["todo-gitops", "d", "--gitops", "--no-github", "--skip-tasks", "--dir", str(tmp_path), "--org", "acme"])
    return tmp_path / "todo-gitops"


class FakeGh:
    """Canned GitHub: repos with topics/answers/files, GHCR tags, git tags."""

    def __init__(self):
        self.topics = {"acme/todo-api": ["deployable-service"], "acme/todo-web": ["deployable-service"], "acme/nodeploy": []}
        self.files = {("acme/todo-api", ".copier-answers.yml"): JAVA_ANSWERS, ("acme/todo-web", ".copier-answers.yml"): WEB_ANSWERS,
                      ("acme/todo-web", "k8s/base/deployment.yaml"): OLD_K8S}
        self.image_tags = {"todo-api": {"latest", "sha-" + SHA[:7], "1.2.0", "1.3.0"}, "todo-web": {"latest", "sha-" + SHA[:7]}}
        self.git_tags = {"acme/todo-api": ["v1.3.1", "v1.3.0", "v1.2.0", "not-semver"], "acme/todo-web": []}

    def __call__(self, args):
        if args[:2] == ["repo", "view"]:
            slug = args[2]
            if slug not in self.topics:
                raise core.PlatformError("not found")
            return json.dumps({"repositoryTopics": [{"name": t} for t in self.topics[slug]]})
        if args[0] == "api":
            path = args[1].split("?")[0].lstrip("/")
            if path.startswith("repos/") and "/contents/" in path:
                slug, f = path[len("repos/"):].split("/contents/")
                if (slug, f) not in self.files:
                    raise core.PlatformError("404")
                return base64.b64encode(self.files[(slug, f)].encode()).decode()
            if path.endswith("/commits/main"):
                return SHA + "\n"
            if path.endswith("/tags"):
                return json.dumps(self.git_tags[path[len("repos/"):-len("/tags")]])
            if "/packages/container/" in path:
                pkg = path.split("/packages/container/")[1].split("/")[0]
                return json.dumps(sorted(self.image_tags.get(pkg, [])))
        raise AssertionError(f"unexpected gh call {args}")


@pytest.fixture()
def gh(monkeypatch):
    fake = FakeGh()
    monkeypatch.setattr(compose, "gh", fake)
    monkeypatch.setattr(promote, "gh", fake)
    return fake


def services(repo):
    return yaml.safe_load((repo / "applications/todo/services.yaml").read_text())["services"]


def run_compose(repo, *args):
    return compose.main([*args, "--repo-dir", str(repo)])


def render_check(repo):
    return subprocess.run(["uv", "run", "scripts/render.py", "--check"], cwd=repo, capture_output=True, text=True)


def commit(repo, msg="x"):
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", msg], cwd=repo, check=True)


# ---------------- compose ----------------

def test_add_writes_a_complete_explicit_entry_and_renders(gitops_repo, gh):
    run_compose(gitops_repo, "add", "todo-api")
    s = services(gitops_repo)[0]
    assert s["name"] == "todo-api" and s["shape"] == "service-java" and s["image"] == "ghcr.io/acme/todo-api"
    assert s["port"] == 8080 and s["user"] == 65532 and s["environments"] == ["dev"]
    assert s["probes"]["readiness"] == "/actuator/health/readiness"
    dev = gitops_repo / "applications/todo/overlays/dev/todo-api"
    assert {p.name for p in dev.iterdir()} == {"deployment.yaml", "service.yaml", "kustomization.yaml"}
    assert not (gitops_repo / "applications/todo/overlays/staging/todo-api").exists()   # new services start in dev only
    assert render_check(gitops_repo).returncode == 0


def test_services_yaml_comments_survive(gitops_repo, gh):
    run_compose(gitops_repo, "add", "todo-api")
    assert "Registry of the services" in (gitops_repo / "applications/todo/services.yaml").read_text()


def test_env_wiring_and_expose(gitops_repo, gh):
    run_compose(gitops_repo, "add", "todo-web", "--env", "API_URL=http://todo-api", "--expose", "web", "--replicas", "2")
    s = services(gitops_repo)[0]
    assert s["env"]["API_URL"] == "http://todo-api" and s["env"]["NODE_ENV"] == "production" and s["replicas"] == 2
    assert s["expose"] == {"host": "web"} and s["port"] == 3000
    route = yaml.safe_load((gitops_repo / "applications/todo/overlays/dev/todo-web/httproute.yaml").read_text())
    assert route["spec"]["hostnames"] == ["web.todo-dev.localhost"]


def test_from_k8s_seeds_a_v1_service(gitops_repo, gh):
    run_compose(gitops_repo, "add", "todo-web", "--from-k8s")
    s = services(gitops_repo)[0]
    assert s["env"]["API_URL"] == "http://todo-api" and s["replicas"] == 2 and "PORT" not in s["env"]


@pytest.mark.parametrize("args,msg", [
    (["add", "missing"], "not found"),
    (["add", "nodeploy"], "deployable-service"),
])
def test_add_rejects_bad_repos(gitops_repo, gh, args, msg):
    with pytest.raises(core.PlatformError, match=msg):
        run_compose(gitops_repo, *args)


def test_duplicate_and_unknown_removal(gitops_repo, gh):
    run_compose(gitops_repo, "add", "todo-api")
    commit(gitops_repo)
    with pytest.raises(core.PlatformError, match="already in"):
        run_compose(gitops_repo, "add", "todo-api")
    with pytest.raises(core.PlatformError, match="not in services.yaml"):
        run_compose(gitops_repo, "remove", "ghost")


def test_remove_prunes_generated_files(gitops_repo, gh):
    run_compose(gitops_repo, "add", "todo-api")
    commit(gitops_repo)
    run_compose(gitops_repo, "remove", "todo-api")
    assert not services(gitops_repo)
    assert not (gitops_repo / "applications/todo/overlays/dev/todo-api").exists()


def test_dry_run_changes_nothing(gitops_repo, gh):
    before = (gitops_repo / "applications/todo/services.yaml").read_text()
    run_compose(gitops_repo, "add", "todo-api", "--dry-run")
    assert (gitops_repo / "applications/todo/services.yaml").read_text() == before


# ---------------- promote ----------------

def composed(repo, *args):
    run_compose(repo, "add", *args)
    commit(repo, "compose")


def pin(repo, env, svc):
    k = yaml.safe_load((repo / f"applications/todo/overlays/{env}/{svc}/kustomization.yaml").read_text())
    return k["images"][0]["newTag"]


def test_promote_to_staging_pins_sha_tag_and_adds_the_environment(gitops_repo, gh):
    composed(gitops_repo, "todo-api")
    promote.main(["todo-api", "dev", "staging", "--repo-dir", str(gitops_repo)])
    assert pin(gitops_repo, "staging", "todo-api") == "sha-" + SHA[:7]       # image tag only; no git ref anywhere
    assert services(gitops_repo)[0]["environments"] == ["dev", "staging"]
    assert render_check(gitops_repo).returncode == 0                         # the pin survives a re-render


def test_promote_refuses_an_image_that_does_not_exist(gitops_repo, gh):
    composed(gitops_repo, "todo-web")
    with pytest.raises(core.PlatformError, match="does not exist yet"):
        promote.main(["todo-web", "dev", "staging", "--sha", "b" * 40, "--repo-dir", str(gitops_repo)])


def test_prod_pins_release_without_v_and_picks_newest_with_an_image(gitops_repo, gh):
    composed(gitops_repo, "todo-api")
    promote.main(["todo-api", "dev", "staging", "--repo-dir", str(gitops_repo)])
    commit(gitops_repo, "promote")
    promote.main(["todo-api", "staging", "prod", "--repo-dir", str(gitops_repo)])
    # v1.3.1 has no image yet, so v1.3.0 wins; the pinned tag is 1.3.0 (CI publishes X.Y.Z, not vX.Y.Z)
    assert pin(gitops_repo, "prod", "todo-api") == "1.3.0"


def test_prod_with_explicit_version(gitops_repo, gh):
    composed(gitops_repo, "todo-api")
    promote.main(["todo-api", "dev", "staging", "--repo-dir", str(gitops_repo)])
    commit(gitops_repo, "promote")
    promote.main(["todo-api", "staging", "prod", "--version", "v1.2.0", "--repo-dir", str(gitops_repo)])
    assert pin(gitops_repo, "prod", "todo-api") == "1.2.0"


@pytest.mark.parametrize("argv,msg", [
    (["todo-api", "staging", "dev"], "cannot promote"),
    (["todo-api", "dev", "dev"], "cannot promote"),
    (["todo-api", "dev", "mars"], "unknown environment"),
    (["todo-api", "staging", "prod"], "not in staging yet"),
    (["ghost", "dev", "staging"], "not in services.yaml"),
])
def test_promote_rejects_invalid_moves(gitops_repo, gh, argv, msg):
    composed(gitops_repo, "todo-api")
    with pytest.raises(core.PlatformError, match=msg):
        promote.main([*argv, "--repo-dir", str(gitops_repo)])


def test_promote_all_moves_every_service_in_the_source_env(gitops_repo, gh):
    composed(gitops_repo, "todo-api")
    composed(gitops_repo, "todo-web")
    promote.main(["--all", "dev", "staging", "--repo-dir", str(gitops_repo)])
    assert pin(gitops_repo, "staging", "todo-api").startswith("sha-") and pin(gitops_repo, "staging", "todo-web").startswith("sha-")
