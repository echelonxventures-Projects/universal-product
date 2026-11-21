# 07 — CERTIFICATION RECONCILIATION

> **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Assumptions flagged explicitly.

---

## 1. Question

For every certification-related blocker: is it **Root**, **Derived**, **False positive**, or **Already satisfied**?

---

## 2. Certification evidence (verified @ `ab78f35`)

| Metric | Value |
|---|---|
| IMPLEMENTED concepts | 314 |
| — of which `certified=true` | 240 |
| — of which `certified=false` | **74** |
| SPECIFIED concepts (not yet certifiable) | 90 |

The 74 IMPLEMENTED-but-uncertified concepts are `in_code=true` — already realized — but have not passed certification. Representative members (from direct read of `closure.json`): `ARCH-GOV-001`, `ARCH-SECURITY-001`, `GOV-002..006`, `PLATFORM-001/008/011`, `DATA-003/004/015/018`, `SERVICE-002/016/018`, `INFRASTRUCTURE-015/017/018`, `RUNTIME-012/013`, the `UCKO-*` set, `EPIC-*` docs, `UCOS-GOV-002/004/006`, `UCOS-EXEC-001/002`, `UKDA-DEC-0001/0002`, `Ω∞-000`.

---

## 3. Certification-blocker classification

| Certification concern | State | Classification |
|---|---|---|
| Certification of 240 already-certified concepts | certified=true | **Already satisfied** |
| Certification of **74 realized-but-uncertified** IMPLEMENTED | in_code=true, certified=false; independent of realization | **ROOT — R2** (in-corpus satisfiable) |
| Certification of the **90 SPECIFIED** span | cannot certify what is not realized | **Derived → R1** (this is **D2**) |
| "Certification architecture / gate missing" | EC3-GATE family present; `verify.sh` present; certified 240 proves the gate operates | **False positive** |
| Absolute constitutional certification (Implementation Authority) | gated by external DR-RAT-11 | **Derived → R3** (finality, see `09`) — distinct from in-corpus certification |

---

## 4. The two-part certification gap

Certification splits cleanly into an independent root and a derivative:

1. **R2 (ROOT, in-corpus):** certify the 74 already-realized concepts. Requires no new realization; runs in parallel with R1. This is a genuine, independent root cause.
2. **D2 (DERIVED → R1):** certify the 90 SPECIFIED concepts — impossible until R1 realizes them.

A third, higher notion — **absolute constitutional certification** (the L8 "Implementation Authority Certified" state) — is gated by **R3 (DR-RAT-11)** and is out-of-corpus. In-corpus certification (R2 + D2) can reach at most **PROVISIONAL** certification (L7).

---

## 5. Completion criteria & success evidence

| Item | Criterion | Evidence |
|---|---|---|
| R2 | all 74 → `certified=true` | regenerated `closure.json`: IMPLEMENTED-certified == IMPLEMENTED total; `verify.sh` green |
| D2 | realized span certified post-R1 | closure shows certified span == realized span |
| L7 gate (provisional) | Certification Complete in-corpus | closure: SPECIFIED=0, all IMPLEMENTED certified, traceability closed (`08`) |
| L8 gate (absolute) | External ratification | out-of-corpus act (R3) — **not achievable in-corpus** |

---

## 6. Verdict

Certification yields **one independent root (R2)** plus **one derivative (D2 → R1)**. The remaining certification concerns are already satisfied, false positives, or fold into R3 (finality). In-corpus certification ceiling is **PROVISIONAL (L7)**.

---
*End of 07-CERTIFICATION-RECONCILIATION.md*
