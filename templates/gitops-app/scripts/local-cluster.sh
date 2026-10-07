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
#   K3S_IMAGE            default rancher/k3s:v1.32.5-k3s1 — the version the Gateway setup below is verified against
#                        (k3d's own default may be older and ship a Traefik without Gateway API support)
#   GATEWAY_API_VERSION  only used if k3s' Traefik chart did not install the Gateway API CRDs (default v1.2.1)
#   GH_TOKEN             default `gh auth token`; used for both credentials below unless they are set (ArgoCD mode only)
#   REPO_TOKEN           least-privilege token for ArgoCD to read this repo: a fine-grained PAT with only
#                        "Contents: read" on the GitOps repo (default GH_TOKEN)
#   PULL_TOKEN           token for the image pull secret: a classic PAT with only read:packages (default GH_TOKEN)
#   WITH_ARGO=0          Gateway + namespaces only: no ArgoCD, no GitHub credentials, no root Application
#                        (used by the platform's end-to-end test, which applies the rendered manifests directly)
#   ESO_VERSION          External Secrets Operator chart version (default 2.12.0)
#   WITH_ESO=0           skip External Secrets Operator (no `secrets:` support in that cluster)
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
k3s_image="${K3S_IMAGE:-rancher/k3s:v1.32.5-k3s1}"
gateway_api_version="${GATEWAY_API_VERSION:-v1.2.1}"
with_argo="${WITH_ARGO:-1}"
registry_port="${REGISTRY_PORT:-}"
eso_version="${ESO_VERSION:-2.12.0}"
with_eso="${WITH_ESO:-1}"
registry="${name}-registry"
org=$(sed -n 's/^github_org:[[:space:]]*//p' .copier-answers.yml | head -1)
k() { kubectl --context "$ctx" "$@"; }

case "${1:-up}" in
  down)
    k3d cluster delete "$name"
    k3d registry delete "k3d-${registry}" >/dev/null 2>&1 || true
    ;;
  up)
    if [ "$with_argo" = 1 ]; then
      token="${GH_TOKEN:-}"
      if [ -z "$token" ] && { [ -z "${REPO_TOKEN:-}" ] || [ -z "${PULL_TOKEN:-}" ]; }; then token=$(gh auth token); fi
      repo_token="${REPO_TOKEN:-$token}"
      pull_token="${PULL_TOKEN:-$token}"
      if [ -z "${REPO_TOKEN:-}" ] || [ -z "${PULL_TOKEN:-}" ]; then
        echo "Note: using your broad GitHub login token for ArgoCD/GHCR; REPO_TOKEN (Contents: read) and PULL_TOKEN (read:packages) limit what the cluster can do with it"
      fi
    fi
    if k3d cluster list "$name" >/dev/null 2>&1; then
      echo "Cluster $name exists - reusing it"
      k3d cluster start "$name" >/dev/null 2>&1 || true
    else
      create_args=(--image "$k3s_image" -p "${port}:80@loadbalancer" --wait)
      if [ -n "$registry_port" ]; then
        k3d registry list "k3d-${registry}" >/dev/null 2>&1 || k3d registry create "$registry" --port "$registry_port" >/dev/null
        create_args+=(--registry-use "k3d-${registry}:${registry_port}")
      fi
      k3d cluster create "$name" "${create_args[@]}"
    fi

    echo "Enabling the Gateway API (Traefik)"
    # k3s installs Traefik with a Helm job; its CRD chart brings the Gateway API CRDs on current k3s. Wait for that job
    # first so that anything we add cannot race with it (applying the CRDs ourselves breaks the Helm install), and only
    # add the CRDs if the chart did not.
    for _ in $(seq 1 60); do k -n kube-system get job helm-install-traefik-crd >/dev/null 2>&1 && break; sleep 2; done
    k -n kube-system wait --for=condition=complete job/helm-install-traefik-crd --timeout=240s >/dev/null
    if ! k get crd gatewayclasses.gateway.networking.k8s.io >/dev/null 2>&1; then
      k apply --server-side -f "https://github.com/kubernetes-sigs/gateway-api/releases/download/${gateway_api_version}/standard-install.yaml" >/dev/null
    fi
    # The Gateway provider is off by default: turn it on, and let routes attach from every namespace.
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
    ready=0
    for _ in $(seq 1 60); do
      if [ "$(k get gatewayclass traefik -o jsonpath='{.status.conditions[?(@.type=="Accepted")].status}' 2>/dev/null)" = "True" ] &&
        [ "$(k -n kube-system get gateway traefik-gateway -o jsonpath='{.status.conditions[?(@.type=="Programmed")].status}' 2>/dev/null)" = "True" ]; then ready=1; break; fi
      sleep 5
    done
    if [ "$ready" != 1 ]; then
      echo "ERROR: the Traefik Gateway did not become ready within 5 minutes." >&2
      k -n kube-system get pods,job 2>&1 | tail -15 >&2
      echo "  fix: check the k3s version (K3S_IMAGE) and 'kubectl --context $ctx -n kube-system logs deploy/traefik'" >&2
      exit 1
    fi

    if [ "$with_eso" = 1 ]; then
      echo "Installing External Secrets Operator ($eso_version)"
      # k3s' Helm controller installs the chart, so no helm binary is needed. `generate` secrets need only the operator;
      # `remote` secrets read from the platform-secrets store: Secrets in the secrets-store namespace (set with `devbox run secret`).
      k create namespace external-secrets --dry-run=client -o yaml | k apply -f - >/dev/null
      k create namespace secrets-store --dry-run=client -o yaml | k apply -f - >/dev/null
      k apply -f - >/dev/null <<YAML
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: external-secrets
  namespace: kube-system
spec:
  repo: https://charts.external-secrets.io
  chart: external-secrets
  version: ${eso_version}
  targetNamespace: external-secrets
  valuesContent: |-
    installCRDs: true
YAML
      for _ in $(seq 1 60); do k get crd clustersecretstores.external-secrets.io >/dev/null 2>&1 && break; sleep 3; done
      for d in external-secrets external-secrets-webhook external-secrets-cert-controller; do
        # the CRDs appear before the chart's Deployments do
        for _ in $(seq 1 100); do k -n external-secrets get "deploy/$d" >/dev/null 2>&1 && break; sleep 3; done
        k -n external-secrets rollout status "deploy/$d" --timeout=300s >/dev/null
      done
      k apply -f - >/dev/null <<'YAML'
apiVersion: v1
kind: ServiceAccount
metadata: {name: eso-store, namespace: secrets-store}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: eso-store, namespace: secrets-store}
rules:
  - {apiGroups: [""], resources: [secrets], verbs: [get, list, watch]}
  - {apiGroups: [authorization.k8s.io], resources: [selfsubjectrulesreviews], verbs: [create]}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: {name: eso-store, namespace: secrets-store}
roleRef: {apiGroup: rbac.authorization.k8s.io, kind: Role, name: eso-store}
subjects: [{kind: ServiceAccount, name: eso-store, namespace: secrets-store}]
---
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata: {name: platform-secrets}
spec:
  provider:
    kubernetes:
      remoteNamespace: secrets-store
      server:
        caProvider: {type: ConfigMap, name: kube-root-ca.crt, namespace: secrets-store, key: ca.crt}
      auth:
        serviceAccount: {name: eso-store, namespace: secrets-store}
YAML
    fi

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
        --from-literal=username="${org}" --from-literal=password="$repo_token" --dry-run=client -o yaml | k apply -f - >/dev/null
      k -n argocd label secret github-creds argocd.argoproj.io/secret-type=repo-creds --overwrite >/dev/null
    fi

    # Namespaces are created up front so the GHCR pull secret exists before the first pod; Argo reuses them.
    for env in dev staging prod; do
      ns="${app}-${env}"
      k create namespace "$ns" --dry-run=client -o yaml | k apply -f - >/dev/null
      if [ "$with_argo" = 1 ]; then
        k -n "$ns" create secret docker-registry ghcr-pull --docker-server=ghcr.io --docker-username="${org}" \
          --docker-password="$pull_token" --dry-run=client -o yaml | k apply -f - >/dev/null
        k -n "$ns" patch serviceaccount default -p '{"imagePullSecrets":[{"name":"ghcr-pull"}]}' >/dev/null
      fi
    done

    urls=""
    for host in $(grep -rhA1 'hostnames:' applications/*/overlays/*/*/httproute.yaml 2>/dev/null | grep -- '- ' | sed 's/.*- //' | sort -u); do
      urls="${urls}Exposed:        http://${host}:${port}/   (once the workloads are running)\n"
    done
    urls=$(printf '%b' "$urls")
    if [ -n "$urls" ]; then urls="${urls}"$'\n'; fi   # command substitution strips the trailing newline

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
