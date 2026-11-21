# 05 — Governance Blockers

| Field | Value |
|-------|-------|
| ARTIFACT ID | EIP-018D-05 (Governance Blockers) |
| MISSION | EIP-018D — Wave-0 Preconditions Reconciliation |
| STATUS | COMPLETE · AUTHORITY = NONE (DERIVED TRUTH) · READ-ONLY |

> **Purpose.** Isolate blockers that are *governance-process* in nature: acts of authority that must be performed and recorded, distinct from constitutional prohibition (03) and engineering work (04). This is where the prior FAIL-CLOSED actually lives.

---

## 1 — The governance gate at Wave 0.1

Wave 0.1 — "ratify USIS-GOV-000 (first-class standing)" — is, by the repository's own words, a **governance authority action** (USIS-012 gate = "ratification"; CRAT-008 §4; CVER-009). This is categorically different from the engineering steps 0.2–0.4. Two governance facts govern it:

1. **A ratification is an authority act.** Under CEP-006 it produces an acceptance determination (ACCEPTED / PROVISIONAL / DEFERRED / REJECTED). It cannot be produced by fiat; it must be a recorded governance determination.
2. **A derived-authority agent may not self-confer authority.** USIS-GOV-000 is AUTHORITY = NONE (DERIVED); every reconciliation/verification session is AUTHORITY = NONE. Fail-closed discipline (S2-08; CEP-006 no-bypass) forbids fabricating an authority the corpus does not hold.

## 2 — Governance blockers

| ID | Blocker | Evidence | Constitutional authority | Required resolution | Repo work? | External? |
|----|---------|----------|--------------------------|---------------------|:----------:|:---------:|
| **GB-1** | **No explicit Wave-0 authorization act exists.** Wave 0 may not commence autonomously; every CRAT/CVER artifact states "commencement requires explicit authorization." | CRAT-008 §6; CRAT-009 §5/§8; CVER-009 §Authorized next sequence; MCP-002 (all EC-3 units "STOP … without explicit authorization") | Repository authority + CEP-006 (governance) | An authorized actor records the Wave-0 authorization; then perform 0.1 as a **provisional** governance ratification (AUTHORITY = NONE), mirroring `SECURITY-GOV-000` founding and the UIMM `CERTIFIED → PROVISIONALLY RATIFIED` precedent (S4-12) | **YES** (an authorized in-corpus governance determination) | No — provisional tier does not require the external act |
| **GB-2** | **Absolute first-class (FINALIZED) standing for USIS-GOV-000 is unattainable in-corpus.** | S2-08 F-04…F-07; CEP-006 Art XII | Constitutional finality (external) | Await/record the External Constituent Act | No (in-corpus) | **YES** — external constituent authority |

## 3 — Distinguishing GB-1 from GB-2 (the crux of the reconciliation)

The prior FAIL-CLOSED at Phase 0.1 is correct **only** to the extent it refused to (a) self-authorize Wave 0, or (b) fabricate FINALIZED standing. It would be **incorrect** if it concluded that 0.1 is *impossible* pending the external act:

- **Provisional ratification of a program root is a routine in-corpus governance act.** Repository precedent is decisive: `SECURITY-GOV-000` (PHASE-008) was founded and Band-13 units U08/U09/U10 + the UIMM were **PROVISIONALLY RATIFIED** at AUTHORITY = NONE, with DR-RAT-11 still BLOCKED. None required the External Constituent Act.
- Therefore GB-1 (missing explicit authorization) is a **governance-process gate**, resolvable by repository work under an authorized actor — **not** an external-authority blocker.
- GB-2 (FINALIZED standing) is the genuine external-authority item — but it is the **finality tier**, which Wave 0 does not require and which is non-blocking to engineering.

## 4 — Governance-gap assessment (GAP-01…08)

The Governance Gap Report items GAP-01…08 (ratification body, quorum, amendment, tie-break, sovereign seat, structural-change definition, ratification audit, immutability) are ALL OPEN (S2-08 F-07). These belong to the **FINALIZED/constituent** tier (they define the missing ratification authority). They do **not** gate provisional program-standing or engineering-scope Wave-0 acts. They are correctly recorded as OPEN and carried forward, not resolvable in-corpus.

## 5 — Determination

- **Governance blocker to *commencing* Wave-0: GB-1 — the absence of an explicit Wave-0 authorization act.** This is an in-corpus governance-process gate (mission-taxonomy **(B)/(F)**), resolvable by repository work under an authorized actor; it is **the true and minimal cause of the correct FAIL-CLOSED posture**.
- **Governance dependency at the finality tier: GB-2 — external constituent authority (mission-taxonomy (G)),** standing and non-blocking to engineering.
- There is **no governance *gap*** (missing machinery) that blocks the engineering-scope Wave-0 acts; the OPEN GAP-01…08 belong exclusively to the FINALIZED tier.

*END — 05 · EIP-018D · GOVERNANCE BLOCKERS · AUTHORITY = NONE (DERIVED TRUTH).*
