#!/usr/bin/env bash
# Local k3d cluster for this product: ArgoCD + access to private GitHub repos and GHCR images, then the root
# Application. For trying the application on your machine; real clusters are bootstrapped by a human with
# `KUBE_CONTEXT=<ctx> devbox run bootstrap`.
#
#   local-cluster.sh up      create (or reuse) the cluster, install ArgoCD, wire credentials, apply bootstrap/
#   local-cluster.sh down    delete the cluster
#
# Environment: LOCAL_CLUSTER (default <app>-local), LOCAL_HTTP_PORT (default 8088), ARGOCD_VERSION (default stable),
#              GH_TOKEN (default: `gh auth token`; needs repo + read:packages/write:packages).
# Re-running `up` is safe; it re-applies credentials and the root Application.
set -euo pipefail

cd "$(dirname "$0")/.."
app=$(basename "$(find applications -mindepth 1 -maxdepth 1 -type d | sort | head -1)")
name="${LOCAL_CLUSTER:-$app-local}"
ctx="k3d-$name"
port="${LOCAL_HTTP_PORT:-8088}"
argocd_version="${ARGOCD_VERSION:-stable}"
org=$(sed -n 's/^github_org:[[:space:]]*//p' .copier-answers.yml | head -1)
k() { kubectl --context "$ctx" "$@"; }

case "${1:-up}" in
  down)
    k3d cluster delete "$name"
    ;;
  up)
    token="${GH_TOKEN:-$(gh auth token)}"
    if k3d cluster list "$name" >/dev/null 2>&1; then
      echo "Cluster $name exists - reusing it"
      k3d cluster start "$name" >/dev/null 2>&1 || true
    else
      k3d cluster create "$name" -p "${port}:80@loadbalancer" --wait
    fi

    echo "Installing ArgoCD ($argocd_version)"
    k create namespace argocd --dry-run=client -o yaml | k apply -f - >/dev/null
    k apply -n argocd --server-side -f "https://raw.githubusercontent.com/argoproj/argo-cd/${argocd_version}/manifests/install.yaml" >/dev/null
    for d in argocd-repo-server argocd-applicationset-controller argocd-server; do
      k -n argocd rollout status "deploy/$d" --timeout=300s
    done

    echo "Wiring credentials (GitHub org ${org})"
    # Argo reads the service repos (remote Kustomize bases) and this repo with the same token.
    k -n argocd create secret generic github-creds --from-literal=url="https://github.com/${org}" \
      --from-literal=username="${org}" --from-literal=password="$token" --dry-run=client -o yaml | k apply -f - >/dev/null
    k -n argocd label secret github-creds argocd.argoproj.io/secret-type=repo-creds --overwrite >/dev/null
    # Namespaces are created up front so the GHCR pull secret exists before the first pod; Argo reuses them.
    for env in dev staging prod; do
      ns="${app}-${env}"
      k create namespace "$ns" --dry-run=client -o yaml | k apply -f - >/dev/null
      k -n "$ns" create secret docker-registry ghcr-pull --docker-server=ghcr.io --docker-username="${org}" \
        --docker-password="$token" --dry-run=client -o yaml | k apply -f - >/dev/null
      k -n "$ns" patch serviceaccount default -p '{"imagePullSecrets":[{"name":"ghcr-pull"}]}' >/dev/null
    done

    echo "Applying the root Application"
    k apply -n argocd -f bootstrap/
    cat <<MSG

Cluster ${ctx} is ready. Watch it converge:
  kubectl --context ${ctx} -n argocd get applications
  kubectl --context ${ctx} -n ${app}-dev get pods
Try a service:  kubectl --context ${ctx} -n ${app}-dev port-forward svc/<service> 8080:80
Remove it:      devbox run cluster-down
MSG
    ;;
  *)
    echo "usage: $0 up|down" >&2
    exit 2
    ;;
esac
