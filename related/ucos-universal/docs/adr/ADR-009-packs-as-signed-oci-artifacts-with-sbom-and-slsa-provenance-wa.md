# ADR-009: Packs as signed OCI artifacts with SBOM and SLSA provenance; WASM for in-process extensions

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §8.3; U57 Capability; U95 Software Delivery |

## Context
UCOS loads capability packs from many authors, including third parties. Supply-chain attacks are a primary risk for a platform that composes software dynamically.

## Decision
Packs are distributed as **OCI artifacts**, signed with Sigstore and accompanied by an SBOM and SLSA level 3 provenance, verified at admission. In-process tenant or partner extensions run as **WASM** modules with capability-based host functions and resource limits. Out-of-process extensions use webhooks or separate services.

## Alternatives considered
- Language-native plugins: fast, but no isolation.
- Containers for every extension: strong isolation, but heavy for small hooks.

## Consequences
**Positive**
- Verifiable provenance of everything that runs.
- Extensions cannot escape their sandbox.

**Negative / costs**
- The WASM host API must be designed and versioned.
- Some libraries are unavailable in WASM.

## Enforcement
`SEC-SUPPLY-01`, `SEC-VULN-01`; admission controller verification.
