---
spec_id: 011-java-spring-boot-template
title: Java (Spring Boot) template
status: done
priority: P1
---

# 011 — Java (Spring Boot) template

## Stories

As a founder, I want a Spring Boot 3.x / JDK 21 / Maven service.

## Acceptance criteria

- **AC-011.1** Spotless + Checkstyle, JUnit 5, and a JaCoCo coverage gate; Actuator probes; optional Micrometer Prometheus and OpenTelemetry Java agent; distroless image running as a numeric user.
- **AC-011.2** `needs_database=true` adds JPA, Bean Validation, Flyway and the PostgreSQL driver; config reads the platform's `PG*` variables; Hibernate only validates; readiness includes the database; the service waits for its database at startup.
- **AC-011.3** CI has a smoke variant with a real PostgreSQL next to the image.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** ADR-009, CHANGELOG 3.1.0

## Changelog

- 2026-10-08 migrated from STORY-011 in docs/backlog.md
