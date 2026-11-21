# ADR-017: Go for the kernel; Go and TypeScript SDKs for packs

| Field | Value |
|---|---|
| Status | Accepted (KERNEL-DESIGN) |
| Deciders | Architecture Board (U01 root authority) |
| References | engineering/KERNEL-DESIGN.md |

## Context
The kernel (gateway, command bus, object service, outbox relay, composer, policy and workflow integration) needs predictable latency, simple deployment and strong concurrency. Pack authors and front-end teams need productive SDKs.

## Decision
The kernel is written in **Go**. The Pack SDK is offered in **Go** and **TypeScript**. UI packs use TypeScript/React with the U64 design system. Performance-critical engines may use Rust behind gRPC if a spike proves the need (for example, the Datalog engine).

## Alternatives considered
- Java/Kotlin: mature, but heavier runtime footprint.
- Rust everywhere: fastest, but slower to hire and develop for.

## Consequences
**Positive**
- Simple static binaries; large talent pool.

**Negative / costs**
- Two SDK languages to maintain.

## Enforcement
SDK conformance suites; `ARCH-CAP-01`.
