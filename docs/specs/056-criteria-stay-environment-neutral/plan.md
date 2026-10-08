---
spec_id: 056-criteria-stay-environment-neutral
spec_hash: db9dbb9a22e0
summary: Environment-neutral criteria; automatic local port
tasks:
- id: t1
  title: Spec format guidance
  files: [plugins/svc/skills/spec-format/references/spec.md, plugins/svc/agents/product-manager.md]
  covers: [AC-056.1]
  parallel_safe: true
  depends_on: []
- id: t2
  title: cluster-up defaults to a free port
  files: [templates/gitops-app/scripts/local-cluster.sh, tests/cplat/test_cluster_ports.py]
  covers: [AC-056.2]
  parallel_safe: true
  depends_on: []
---

## t1 — Spec format guidance

**Files:** plugins/svc/skills/spec-format/references/spec.md, plugins/svc/agents/product-manager.md
**Covers:** AC-056.1
**Goal:** Criteria name no host ports, local hostnames or machine paths.

**Implementation notes:**
- —

**Done when:** Text present.

## t2 — cluster-up defaults to a free port

**Files:** templates/gitops-app/scripts/local-cluster.sh, tests/cplat/test_cluster_ports.py
**Covers:** AC-056.2
**Goal:** Default `LOCAL_HTTP_PORT=auto`: 8088 if free, else the next free one; an explicit value still wins and still reports a busy port.

**Implementation notes:**
- —

**Done when:** Tests in test_cluster_ports.py cover default-free, default-busy and explicit-busy.
