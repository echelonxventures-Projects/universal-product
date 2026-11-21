# UCOS Ω∞ — SECURITY INTELLIGENCE LAYER ARCHITECTURE

| Field | Value |
|-------|-------|
| ARTIFACT ID | UKB-ADV-005 |
| ARTIFACT | Security Intelligence Layer Architecture (Workstream UKB-005, Deliverable 6) |
| PROGRAM | UCOS Ω∞ UKB Advancement Program (ADV) |
| STATUS | ACTIVE |
| PARENT | UKB-ADV-004 |
| DEPENDS-ON | UKB-ADV-004 |
| VOLUME | VOL-021 (DIGITAL TWIN) |

*Append-only extension overlay on UCOS-BOOK-000000. Modifies no existing artifact. Embeds no secret (RR-07).*

---

## 1. PURPOSE

Track the full security posture and roll it up automatically: **Threat Models · Security Controls · Vulnerabilities · Findings · Exceptions · Penetration Results · Compliance Evidence · Audit Evidence.**

## 2. ENTITY MODEL

| Entity | Category | Key attributes | Schema |
|--------|----------|----------------|--------|
| Threat Model | `FND` (sub) | STRIDE/LINDDUN elements, assets, mitigations → Control | `finding.schema.json` |
| Security Control | `FND` (sub) | control id (NIST/ISO/CIS), status, evidence | (embedded) |
| Vulnerability / Finding | `FND` | CVE/rule, severity (CVSS), component, state, sla_due | `finding.schema.json` |
| Exception (risk acceptance) | `FND` (sub) | finding ref, approver, expiry, justification | (embedded) |
| Penetration Result | `FND` (sub) | engagement, findings, retest state | (embedded) |
| Compliance Evidence | `FND` (sub) | framework, control, artifact ref | (embedded) |
| Audit Evidence | `FND` (sub) | audit, control, status, link | (embedded) |

## 3. EDGES

- `Finding —References→ Component/Repository/Build` (what is affected)
- `Control —Mitigates→ Threat` ; `Control —References→ Architecture` (UCOS-ARCH security constitution)
- `Exception —References→ Finding` (accepted risk, time-boxed)
- `Finding —Tested-By→ SecurityTest/PenTest` (bridge to UKB-004)

## 4. AUTOMATIC ROLL-UP

Security dimension per artifact = reduce(latest findings):
- any open `CRITICAL`/`HIGH` without a valid Exception → `BLOCKED`
- open `MEDIUM` within SLA → `IN_PROGRESS`/`APPROVED` with caveat
- no open findings + controls satisfied → `APPROVED`

Portfolio security = blocking view over all artifacts. Exceptions auto-expire: when `expiry < now`, the accepted finding reverts to open on next rollup (append-only expiry signal). No security status is entered by hand.

## 5. SIGNALS

| Source | Produces |
|--------|----------|
| OWASP Dependency-Check | dependency CVEs by severity → Finding entities |
| Trivy | image/OS/library vulns, misconfigs → Finding entities |
| SonarQube (security hotspots) | code security findings |
| ZAP / pentest tooling | DAST + manual pentest findings |
| GRC/compliance tracker | control status, audit + compliance evidence |

## 6. SECRET HANDLING

The security layer never stores secret values. Scanner tokens are external secret-manager handles. Any signal or evidence field containing a detected secret pattern is rejected at ingest and raised as a `SECRET-LEAK` finding referencing location only (SRC-08 / RR-07 defense).

*Return: [UKB-ADV-000](UKB-ADV-000-ADVANCEMENT-PROGRAM-MASTER-INDEX.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*
