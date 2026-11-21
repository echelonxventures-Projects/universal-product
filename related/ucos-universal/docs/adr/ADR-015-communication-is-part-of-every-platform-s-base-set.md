# ADR-015: Communication is part of every platform's base set

| Field | Value |
|---|---|
| Status | Accepted (A-60, A-64, A-65) |
| Deciders | Architecture Board (U01 root authority) |
| References | U40 Communication; U109; spec/rules/facts/defaults.yaml |

## Context
The checker found that a D2C platform composed without any way to message customers (order confirmations, OTP), even though every commerce regulation assumes notices are sent.

## Decision
`communication.core`, `communication.inapp` and `communication.inbound` are in the **base capability set** of every tenant platform. Channel adapters are selected per jurisdiction and method (for example, the TRAI DLT SMS adapter in India). Real-time chat, voice, video and the contact centre (U109) are added by channel requirements from Phase 3.

## Alternatives considered
- Leave communication optional: produces platforms that fail legal notice obligations.

## Consequences
**Positive**
- Every platform can send transactional and legal notices from day one.

**Negative / costs**
- Slightly larger minimum footprint.

## Enforcement
Checker base-set rule; golden platform definitions.
