# ADR-035: Legal interpretations are owned by in-house counsel with external firms per jurisdiction

| Field | Value |
|---|---|
| Status | Accepted (structure) |
| Deciders | Architecture Board (U01 root authority) |
| References | U67 Compliance; open decision U67 |

## Context
Regulations become facts and controls. Someone accountable must approve each interpretation.

## Decision
Every `Interpretation` in U67 has an **owner (in-house counsel)** and, for jurisdictions without in-house expertise, a **reviewing external firm** recorded on the interpretation. Interpretations are versioned, carry an effective range, and are approved as level-2 decisions.

## Alternatives considered
- Engineers interpret regulations: no accountability or expertise.

## Consequences
**Positive**
- Clear accountability; auditors can trace every control to an approved interpretation.

**Negative / costs**
- External counsel cost per new jurisdiction.

## Enforcement
U67 lint: an Interpretation without an owner and approval cannot be activated.
