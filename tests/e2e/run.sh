#!/usr/bin/env bash
# Platform end-to-end test (no GitHub, no GHCR, no ArgoCD):
#   render a gitops-app + a Java service + a web app with the real templates → build the images → push to a local
#   registry → start the platform's own local cluster (scripts/local-cluster.sh, WITH_ARGO=0) → apply the manifests the
#   renderer generated → wait for rollout → probe the services through the Gateway.
# It exercises: cplat new-service, the templates' Dockerfiles (non-root numeric user, read-only filesystem), render.py,
# the generated Deployment/Service/HTTPRoute against a real API server, and the Gateway API on k3s' Traefik.
#
# Needs: docker (running), k3d, kubectl, uv, curl, copier (or uv). Env: E2E_KEEP=1 keeps the cluster, E2E_PORT, E2E_WORK.
set -euo pipefail

root=$(cd "$(dirname "$0")/../.." && pwd)
work="${E2E_WORK:-$(mktemp -d)}"
port="${E2E_PORT:-8099}"
regport=5111
cluster=e2e-local
registry="k3d-${cluster}-registry"
cplat="uv run $root/scripts/cplat/cplat.py"
export PATH="$PATH:$HOME/.local/bin"
fail() { echo "E2E FAIL: $*" >&2; exit 1; }
step() { echo; echo "==> $*"; }

cleanup() {
  rc=$?
  if [ "${E2E_KEEP:-0}" != 1 ]; then
    (cd "$work/e2e-gitops" 2>/dev/null && LOCAL_CLUSTER=$cluster WITH_ARGO=0 REGISTRY_PORT=$regport bash scripts/local-cluster.sh down) >/dev/null 2>&1 || true
  fi
  [ $rc -eq 0 ] && echo && echo "E2E OK" || echo "E2E FAILED (work dir: $work)"
  exit $rc
}
trap cleanup EXIT

for t in docker k3d kubectl uv curl; do command -v $t >/dev/null || fail "$t is required"; done
docker info >/dev/null 2>&1 || fail "docker is not running"

step "Render the three repos with the real templates (no GitHub)"
$cplat new-service e2e-gitops "e2e gitops repo" --gitops --no-github --skip-tasks --dir "$work" --org e2e >/dev/null
$cplat new-service e2e-api "e2e api" --type service-java --no-github --skip-tasks --dir "$work" --org e2e >/dev/null
$cplat new-service e2e-web "e2e web" --web --no-github --skip-tasks --dir "$work" --org e2e >/dev/null

step "Start the local cluster with a registry (the template's own script, Gateway only)"
(cd "$work/e2e-gitops" && LOCAL_CLUSTER=$cluster LOCAL_HTTP_PORT=$port WITH_ARGO=0 REGISTRY_PORT=$regport bash scripts/local-cluster.sh up)

step "Build and push the images"
for svc in e2e-api e2e-web; do
  docker build -q -t "localhost:$regport/$svc:latest" "$work/$svc" >/dev/null
  docker push -q "localhost:$regport/$svc:latest" >/dev/null
done

step "Describe the services like /gitops:compose does and render the manifests"
(cd "$work/e2e-gitops" && uv run --with pyyaml --with ruamel.yaml python - "$root" "$registry:$regport" <<'PY'
import argparse, sys
root, registry = sys.argv[1], sys.argv[2]
sys.path.insert(0, f"{root}/scripts/cplat")
import compose, core, gitops
from pathlib import Path
repo = Path(".")
app_dir = gitops.find_app(repo)
y, data = gitops.load(app_dir)
services = gitops.services_of(data)
shapes = {s["id"]: s for s in core.registry.load()}
ns = argparse.Namespace(port=None, replicas=None, env=[], expose=True, generate=[], secret=[])
for name, shape in (("e2e-api", "service-java"), ("e2e-web", "web-nextjs")):
    ns.env = ["API_URL=http://e2e-api"] if name == "e2e-web" else []
    ns.generate = ["e2e-api-auth=DB_PASSWORD,JWT_KEY"] if name == "e2e-api" else []   # random values created by ESO
    ns.secret = ["e2e-api-stripe=STRIPE_KEY"] if name == "e2e-api" else []            # read from the secret store
    services.append(compose.build_entry(name, f"e2e/{name}", shapes[shape], None, registry, ns, {}))
gitops.save(app_dir, y, data)
PY
uv run scripts/render.py)

step "Set the remote secret in the local store (what a developer does with /gitops:secret)"
printf 'sk_test_e2e' | $cplat secret set e2e-api e2e-api-stripe STRIPE_KEY --value-stdin --repo-dir "$work/e2e-gitops" >/dev/null

step "Apply the generated manifests (what ArgoCD would sync)"
ns=e2e-dev
for svc in e2e-api e2e-web; do
  kubectl --context k3d-$cluster apply -n $ns -k "$work/e2e-gitops/applications/e2e/overlays/dev/$svc"
done
for svc in e2e-api e2e-web; do
  kubectl --context k3d-$cluster -n $ns rollout status deploy/$svc --timeout=240s || {
    kubectl --context k3d-$cluster -n $ns describe pod -l app=$svc | tail -30; fail "$svc did not become ready"; }
done

step "Probe through the Gateway"
probe() { # url expected-substring
  for _ in $(seq 1 30); do
    out=$(curl -s -m 5 "$1" || true)
    case "$out" in *"$2"*) echo "ok   $1 -> $2"; return 0;; esac
    sleep 3
  done
  fail "$1 did not return '$2' (got: ${out:-nothing})"
}
probe "http://e2e-web.e2e-dev.localhost:$port/api/health" '"status":"ok"'
probe "http://e2e-api.e2e-dev.localhost:$port/actuator/health/readiness" '"status":"UP"'
probe "http://e2e-api.e2e-dev.localhost:$port/api/info" '"service":"e2e-api"'

step "Pods run as the declared non-root user with a read-only filesystem"
kubectl --context k3d-$cluster -n $ns get pods -o jsonpath='{range .items[*]}{.metadata.name}{" ro="}{.spec.containers[0].securityContext.readOnlyRootFilesystem}{" uid="}{.spec.containers[0].securityContext.runAsUser}{"\n"}{end}'

step "External Secrets: generated values are random and stable, remote values arrive"
kc() { kubectl --context k3d-$cluster -n $ns "$@"; }
secret_val() { kc get secret "$1" -o jsonpath="{.data.$2}" 2>/dev/null | base64 -d; }
for _ in $(seq 1 40); do [ -n "$(secret_val e2e-api-auth DB_PASSWORD)" ] && [ -n "$(secret_val e2e-api-stripe STRIPE_KEY)" ] && break; sleep 3; done
db=$(secret_val e2e-api-auth DB_PASSWORD); jwt=$(secret_val e2e-api-auth JWT_KEY)
[ "${#db}" = 32 ] || fail "generated DB_PASSWORD has length ${#db}, expected 32"
[ "$db" != "$jwt" ] || fail "generated keys must differ"
[ "$(secret_val e2e-api-stripe STRIPE_KEY)" = sk_test_e2e ] || fail "remote secret did not arrive"
kc annotate externalsecret e2e-api-auth force-sync="$(date +%s)" --overwrite >/dev/null; sleep 8
[ "$(secret_val e2e-api-auth DB_PASSWORD)" = "$db" ] || fail "generated secret changed on re-sync (it must be created once)"
kc get pod -l app=e2e-api -o jsonpath='{.items[0].spec.containers[0].envFrom[*].secretRef.name}' | grep -q e2e-api-auth || fail "pod does not consume the generated secret"
echo "ok   generated + remote secrets synced and consumed"
