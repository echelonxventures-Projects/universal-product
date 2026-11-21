# 15 — Security Model

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define the security model for UMA: the trust boundaries, the integrity guarantees that protect measurement from tampering, the read-only guarantee that protects sources (especially UKB), and the confidentiality posture. Security here means **measurement integrity first** — a measurement authority whose outputs can be forged is worthless.

## 1. Threat Model

| Threat | Impact | Primary control |
|---|---|---|
| T-1 Forged measurement result | false closure/completeness claim | Sealed, content-addressed, replayable results (§3) |
| T-2 Source mutation by UMA | corruption of Repository Truth | Read-only-at-L0 invariant (§4) |
| T-3 Silent registry tampering | hidden change to what is measured | Governed, versioned, audited control plane (§5) |
| T-4 Non-deterministic injection (clock/RNG/network) | irreproducible results | Determinism class PURE enforced (§6) |
| T-5 Evidence spoofing | determination without real backing | Evidence = content-hashed pointers (§3) |
| T-6 Unauthorized control-plane change | measurement semantics altered | CEP/CONST authorization + ledger (doc 13) |
| T-7 Secret/PII leakage via measurement | confidentiality breach | Descriptor/pointer-only storage; no content copy (§7) |

## 2. Trust Boundaries

```
[ Sources incl. UKB ]  ── READ-ONLY ──►  [ UMA data plane ]  ── DERIVED ──►  [ Consumers ]
        (truth)                          (measurement)                       (decisions)
                          ▲ control-plane changes ▲
                   [ CEP/CONST Governance ]  (authorization boundary)
```

- Sources are trusted-for-truth but never written by UMA.
- UMA outputs are trusted-as-derived only (`authority = NONE`); consumers must never treat them as truth.
- The control plane is the highest-value boundary: changing it changes measurement meaning, so it sits behind governance authorization.

## 3. Measurement Integrity (anti-forgery)

- Every Result is **sealed**: content-addressed by `(manifest_id, registry_version, source_state_hash, metric_id)` and its own value hash.
- **Replayability = tamper-evidence:** any consumer can `ReplayResult` (doc 09) and detect forgery — a forged result will not reproduce.
- **Evidence is verifiable:** each `EvidenceRef` carries a content hash; a determination can be independently re-verified against the pointed-to source bytes.
- No result is valid without a resolvable manifest, registry snapshot, and evidence chain (fail-closed).

## 4. Source Protection (read-only guarantee)

- L0 access is strictly read-only; UMA has no write path to any source. This is architectural, not merely policy: adapters expose read interfaces only.
- UKB integrity is thereby structurally protected — UMA cannot alter Repository Truth even in principle.
- Idempotence (doc 12) reinforces this: re-runs produce no source-side effects.

## 5. Control-Plane Security

- All control-plane mutations require authorization under the existing governance authority (doc 13) and are recorded in the append-only Governance Ledger.
- Registry snapshots are immutable and versioned; a run pins a snapshot, so post-hoc tampering cannot retroactively change a sealed result.
- Discovery-originated proposals cannot self-promote (no privilege escalation from data plane to control plane).

## 6. Determinism as a Security Property

- Determinism class PURE forbids clock/RNG/network reads inside a measurement, closing non-deterministic injection vectors (T-4).
- Existing determinism CI (`determinism.yml`) is extended (D-12, doc 10) to assert UMA replay equality in the pipeline — making integrity continuously verified, not merely asserted.

## 7. Confidentiality & Data Minimization

- UMA stores **descriptors, metrics, and pointers** — never copies of source content (Knowledge Once, doc 11 §5). This minimizes blast radius: UMA stores cannot leak secrets/PII it never holds.
- Where a source itself contains sensitive material, UMA references it by locator+hash; access control on the underlying source (UKB/repo) remains the enforcing authority.
- Telemetry (doc 12 §7) is derived and must exclude source content.

## 8. Least Authority

- UMA holds the *least* authority necessary: read on sources, write on its own derived stores, none on consumers, none on truth.
- No UMA component may assert `authority = UMA` on a metric; the platform is constitutionally incapable of claiming truth.

## 9. Dependency Determination

- Source access control **RETAINS** with source owners (UKB/repo/OS). UMA adds seal/replay integrity + Governance Ledger (NEW). Determinism CI **EXTENDS** existing `determinism.yml`. No frozen security posture modified.

*END — 15 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
