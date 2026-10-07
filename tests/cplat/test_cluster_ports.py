"""templates/gitops-app/scripts/ports.sh: busy-port detection used by `devbox run cluster-up`."""
import socket
import subprocess
from pathlib import Path

import pytest

PORTS = Path(__file__).resolve().parents[2] / "templates" / "gitops-app" / "scripts" / "ports.sh"


def sh(snippet: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", "-c", f'. "{PORTS}"; {snippet}'], capture_output=True, text=True)


@pytest.fixture()
def busy_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    s.listen(1)
    yield s.getsockname()[1]
    s.close()


def free_port_number() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_a_listening_port_is_reported_busy(busy_port):
    assert sh(f"port_in_use {busy_port}").returncode == 0


def test_a_free_port_is_not_busy():
    assert sh(f"port_in_use {free_port_number()}").returncode != 0


def test_free_port_skips_busy_ports(busy_port):
    out = sh(f"free_port {busy_port}").stdout.strip()
    assert out.isdigit() and int(out) > busy_port


def test_the_owner_of_a_busy_port_is_named(busy_port):
    out = sh(f"port_owner {busy_port}").stdout
    assert "pid" in out          # e.g. "Python (pid 1234)"; empty only when lsof is missing


def test_cluster_up_refuses_a_busy_port_before_creating_anything(tmp_path, busy_port):
    """Run the real script against a gitops-app skeleton with fake k3d/gh/kubectl: it must stop at the port check."""
    import shutil
    skeleton = tmp_path / "gitops"
    (skeleton / "applications" / "demo").mkdir(parents=True)
    (skeleton / "scripts").mkdir()
    for f in ("local-cluster.sh", "ports.sh"):
        shutil.copy(PORTS.parent / f, skeleton / "scripts" / f)
    (skeleton / ".copier-answers.yml").write_text("github_org: acme\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    for tool in ("k3d", "kubectl", "gh"):
        script = bin_dir / tool
        script.write_text(f'#!/bin/sh\necho "{tool} $*" >> "{log}"\n[ "{tool}" = k3d ] && [ "$1 $2" = "cluster list" ] && exit 1\nexit 0\n')
        script.chmod(0o755)
    import os
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "LOCAL_HTTP_PORT": str(busy_port), "GH_TOKEN": "x"}
    run = subprocess.run(["bash", str(skeleton / "scripts" / "local-cluster.sh"), "up"], capture_output=True, text=True, env=env, cwd=skeleton)
    assert run.returncode == 1
    assert f"host port {busy_port} is already in use" in run.stderr and "LOCAL_HTTP_PORT=" in run.stderr
    assert "k3d cluster create" not in log.read_text()          # nothing was created
