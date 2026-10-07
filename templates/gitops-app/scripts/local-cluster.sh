#!/usr/bin/env bash
# Local k3d cluster for this product: Gateway API (Traefik) and, by default, ArgoCD with access to the private GitHub
# repo and GHCR images, then the root Application. For trying the application on your machine; real clusters are
# bootstrapped by a human with `KUBE_CONTEXT=<ctx> devbox run bootstrap`.
#
#   local-cluster.sh up      create (or reuse) the cluster, install the Gateway API (+ ArgoCD, credentials, root app)
#   local-cluster.sh down    delete the cluster (and its registry)
#
# Environment:
#   LOCAL_CLUSTER        cluster name (default <app>-local)
#   LOCAL_HTTP_PORT      host port of the Gateway (default 8088)
#   ARGOCD_VERSION       default stable
#   GH_TOKEN             default `gh auth token`; needs repo + read:packages/write:packages (ArgoCD mode only)
#   WITH_ARGO=0          Gateway + namespaces only: no ArgoCD, no GitHub credentials, no root Application
#                        (used by the platform's end-to-end test, which applies the rendered manifests directly)
#   REGISTRY_PORT        also create a local image registry reachable as localhost:<port> from the host and as
#                        k3d-<cluster>-registry:<port> from the cluster
# Re-running `up` is safe; it re-applies credentials and the root Application.
set -euo pipefail

cd "$(dirname "$0")/.."
app=$(basename "$(find applications -mindepth 1 -maxdepth 1 -type d | sort | head -1)")
name="${LOCAL_CLUSTER:-$app-local}"
ctx="k3d-$name"
port="${LOCAL_HTTP_PORT:-8088}"
argocd_version="${ARGOCD_VERSION:-stable}"
with_argo="${WITH_ARGO:-1}"
registry_port="${REGISTRY_PORT:-}"
registry="${name}-registry"
org=$(sed -n 's/^github_org:[[:space:]]*//p' .copier-answers.yml | head -1)
k() { kubectl --context "$ctx" "$@"; }

case "${1:-up}" in
  down)
    k3d cluster delete "$name"
    k3d registry delete "k3d-${registry}" >/dev/null 2>&1 || true
    ;;
  up)
    if [ "$with_argo" = 1 ]; then token="${GH_TOKEN:-$(gh auth token)}"; fi
    if k3d cluster list "$name" >/dev/null 2>&1; then
      echo "Cluster $name exists - reusing it"
      k3d cluster start "$name" >/dev/null 2>&1 || true
    else
      create_args=(-p "${port}:80@loadbalancer" --wait)
      if [ -n "$registry_port" ]; then
        k3d registry list "k3d-${registry}" >/dev/null 2>&1 || k3d registry create "$registry" --port "$registry_port" >/dev/null
        create_args+=(--registry-use "k3d-${registry}:${registry_port}")
      fi
      k3d cluster create "$name" "${create_args[@]}"
    fi

    echo "Enabling the Gateway API (Traefik)"
    # k3s ships Traefik and its CRD chart, which already installs the Gateway API CRDs (applying them ourselves races with
    # the Helm install and breaks it on a fresh cluster). Only the Gateway *provider* is off by default: turn it on, and let
    # routes attach from every namespace.
    k apply -f - >/dev/null <<'YAML'
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    providers:
      kubernetesGateway:
        enabled: true
    gateway:
      listeners:
        web:
          namespacePolicy: All
YAML
    for _ in $(seq 1 60); do
      [ "$(k get gatewayclass traefik -o jsonpath='{.status.conditions[?(@.type=="Accepted")].status}' 2>/dev/null)" = "True" ] &&
        [ "$(k -n kube-system get gateway traefik-gateway -o jsonpath='{.status.conditions[?(@.type=="Programmed")].status}' 2>/dev/null)" = "True" ] && break
      sleep 5
    done

    if [ "$with_argo" = 1 ]; then
      echo "Installing ArgoCD ($argocd_version)"
      k create namespace argocd --dry-run=client -o yaml | k apply -f - >/dev/null
      k apply -n argocd --server-side -f "https://raw.githubusercontent.com/argoproj/argo-cd/${argocd_version}/manifests/install.yaml" >/dev/null
      for d in argocd-repo-server argocd-applicationset-controller argocd-server; do
        k -n argocd rollout status "deploy/$d" --timeout=300s
      done

      echo "Wiring credentials (GitHub org ${org})"
      # Argo reads this (private) GitOps repo with the token; services no longer need any repo access (ADR-017).
      k -n argocd create secret generic github-creds --from-literal=url="https://github.com/${org}" \
        --from-literal=username="${org}" --from-literal=password="$token" --dry-run=client -o yaml | k apply -f - >/dev/null
      k -n argocd label secret github-creds argocd.argoproj.io/secret-type=repo-creds --overwrite >/dev/null
    fi

    # Namespaces are created up front so the GHCR pull secret exists before the first pod; Argo reuses them.
    for env in dev staging prod; do
      ns="${app}-${env}"
      k create namespace "$ns" --dry-run=client -o yaml | k apply -f - >/dev/null
      if [ "$with_argo" = 1 ]; then
        k -n "$ns" create secret docker-registry ghcr-pull --docker-server=ghcr.io --docker-username="${org}" \
          --docker-password="$token" --dry-run=client -o yaml | k apply -f - >/dev/null
        k -n "$ns" patch serviceaccount default -p '{"imagePullSecrets":[{"name":"ghcr-pull"}]}' >/dev/null
      fi
    done

    urls=""
    for host in $(grep -rhA1 'hostnames:' applications/*/overlays/*/*/httproute.yaml 2>/dev/null | grep -- '- ' | sed 's/.*- //' | sort -u); do
      urls="${urls}Exposed:        http://${host}:${port}/   (once the workloads are running)\n"
    done
    urls=$(printf '%b' "$urls")

    if [ "$with_argo" = 1 ]; then
      echo "Applying the root Application"
      k apply -n argocd -f bootstrap/
      cat <<MSG

Cluster ${ctx} is ready. Watch it converge:
  kubectl --context ${ctx} -n argocd get applications
  kubectl --context ${ctx} -n ${app}-dev get pods
${urls}Or port-forward: kubectl --context ${ctx} -n ${app}-dev port-forward svc/<service> 8080:80
Remove it:      devbox run cluster-down
MSG
    else
      echo "Cluster ${ctx} is ready (Gateway API only, no ArgoCD)."
      if [ -n "$registry_port" ]; then echo "Registry: push to localhost:${registry_port}/<image>; pods pull k3d-${registry}:${registry_port}/<image>"; fi
    fi
    ;;
  *)
    echo "usage: $0 up|down" >&2
    exit 2
    ;;
esac
