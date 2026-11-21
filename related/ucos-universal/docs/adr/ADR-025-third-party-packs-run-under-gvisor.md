# ADR-025: Third-party packs run under gVisor

| Field | Value |
|---|---|
| Status | Accepted |
| Deciders | Architecture Board (U01 root authority) |
| References | U57 Capability; open decision U57; ADR-009 |

## Context
Packs from third parties execute code inside UCOS cells. Container isolation alone shares the host kernel.

## Decision
Out-of-process packs from **third parties run under gVisor** (runsc) with network egress allow-lists and resource limits. First-party, certified packs run on the default runtime. In-process extensions remain WASM (ADR-009). The P2 cost spike measures the gVisor overhead; it changes node sizing, not the policy.

## Alternatives considered
- gVisor for every pack: simpler policy, but pays the overhead for code UCOS writes and certifies itself.
- No extra sandbox: unacceptable for code UCOS does not control.

## Consequences
**Positive**
- Kernel-level isolation for untrusted code.

**Negative / costs**
- 10–30% overhead for syscall-heavy third-party packs; dedicated node pools.

## Enforcement
Admission policy: third-party packs without the gVisor runtime class are rejected; `SEC-SUPPLY-01`.
