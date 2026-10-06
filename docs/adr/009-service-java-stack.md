# ADR-009: `service-java` stack defaults

**Status:** Accepted
**Date:** 2026-05-22

## Context

The `service-java` shape is one of two case studies validating the §4.1 add-a-shape contract from the platform vision PRD. It needs concrete defaults across four axes — build tool, container image, observability, and code style — so the Copier template and the `svc-java` plugin's agents are unambiguous. These decisions cluster into one ADR rather than four because they together define the shape's identity.

## Decision

The `service-java` template ships with:

| Axis | Choice |
|---|---|
| Language / runtime | JDK 21 LTS (pinned per [ADR-005](005-node-version-policy.md)-style policy) |
| Framework | Spring Boot 3.x |
| Build tool | **Maven** |
| Container image base | **`gcr.io/distroless/java21-debian12:nonroot`** |
| Observability | **Spring Boot Actuator + Micrometer (Prometheus registry) + OpenTelemetry Java agent (`-javaagent`)** |
| Code style | **Spotless + google-java-format**, with a minimal Checkstyle config for what the formatter doesn't enforce |

### Build tool — Maven (chosen over Gradle)

- Maven's POM is declarative XML — easier for the `coder` agent to read, parse, and edit safely than a Kotlin/Groovy build script.
- Spring Boot has first-class Maven support; `spring-boot-maven-plugin` covers run, repackage, and image build.
- Lower cognitive load for human contributors who haven't worked with Gradle Kotlin DSL.
- Trade-off accepted: slower full builds than Gradle for large projects, more verbose POMs. For service-shaped repos (one module, modest dependency count) the gap is negligible.

### Container image — Distroless JRE 21

- ~250MB image; no shell; non-root by default.
- Matches the `service-go` `distroless/static-nonroot` choice — uniform security posture across backend shapes.
- GraalVM native image rejected as default: longer build times, reflection requires explicit config (Spring AOT helps but still friction), harder debugging. May become an opt-in mode later for cold-start-sensitive services.

### Observability — Actuator + Micrometer + OTel agent

- Actuator exposes `/actuator/health`, `/actuator/health/readiness`, `/actuator/info`, `/actuator/prometheus`.
- Micrometer's Prometheus registry feeds the `/actuator/prometheus` endpoint.
- OpenTelemetry Java agent (attached via `-javaagent` in the Dockerfile entrypoint) gives distributed tracing with zero code changes.
- Most idiomatic Spring Boot setup; new contributors find documentation instantly.

### Code style — Spotless + google-java-format

- `mvn spotless:apply` runs in `devbox run lint-fix`; `mvn spotless:check` runs in `devbox run lint` and CI.
- google-java-format is the most widely adopted Java style — agents trained on public code produce conformant output.
- Minimal Checkstyle config catches things the formatter doesn't (unused imports, naming, javadoc presence on public APIs).

## Devbox recipes (canonical)

The template ships `devbox.json` with at least:

| Recipe | Wraps |
|---|---|
| `test` | `mvn -B verify` |
| `test-fast` | `mvn -B test` |
| `lint` | `mvn -B spotless:check checkstyle:check` |
| `lint-fix` | `mvn -B spotless:apply` |
| `quality` | `lint` then `verify` |
| `audit` | `mvn -B org.owasp:dependency-check-maven:check` |
| `image-build` | `mvn -B spring-boot:build-image -Dspring-boot.build-image.imageName=<name>:scan` |
| `image-scan` | `trivy image --severity CRITICAL,HIGH <name>:scan` |
| `dev` | `mvn -B spring-boot:run` |
| `deploy` | `kubectl apply -k k8s/overlays/local/` |

## Consequences

- The `svc-java` plugin's `coder` agent generates Spring Boot 3.x code, edits POMs via clearly-bounded XML manipulation (or `maven` plugin commands), and always invokes `devbox run` — never raw `mvn`.
- The `tester` agent writes JUnit 5 + Spring Boot Test, uses Testcontainers when integration tests need real dependencies, and reads coverage from JaCoCo (configured in the POM).
- The `deployment` agent's Dockerfile is a multi-stage build: Maven build stage (`maven:3.9-eclipse-temurin-21`) → distroless runtime stage with the `-javaagent` line.
- Re-evaluate Maven vs Gradle if the platform ever needs multi-module composite builds or build-time AOT (GraalVM native) becomes a default goal.

## References

- [platform-vision.md §4, §11.8](../requirements/platform-vision.md)
- [ADR-008](008-shape-detection.md) — sniffing fallback uses `pom.xml` to detect this shape
