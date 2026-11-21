# TM-INTEGRATION — Connectors and webhooks

| Field | Value |
|---|---|
| Scope | U62 Integration: connector runtime, provider credentials, inbound webhooks (`/hooks/*`), tenant outbound webhooks, sync jobs, file imports |
| Data classes | Credentials and secrets (via U65), any payload class |
| Owner | `ucos:org:platform-integration` |
| References | U62, U65; OWASP SSRF guidance |

## STRIDE
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| IN-S1 | Forged inbound webhook | 3 | 3 | Per-provider signature verification, timestamp tolerance, source allow-lists where the provider publishes them, re-fetch before terminal state changes | Connector conformance |
| IN-T1 | SSRF through tenant-configured outbound webhook URLs | 3 | 3 | Egress proxy with deny-lists for private, link-local and metadata ranges; DNS-rebinding protection; HTTPS only | SSRF tests |
| IN-I1 | Provider credentials leaked | 2 | 3 | SecretRef only; secrets manager with rotation; connector processes cannot read other tenants' secrets | `SEC-SECRETS-01` |
| IN-I2 | Outbound webhook payloads over-share | 2 | 2 | Subscribers choose event types; payloads are filtered by data class and purpose; signed with a per-subscription secret | Contract tests |
| IN-D1 | Slow or failing tenant endpoints back up delivery | 3 | 2 | Per-subscription queues, exponential backoff, automatic disable after a failure threshold with notification | Load tests |
| IN-T2 | Malicious import files (CSV injection, zip bombs) | 2 | 2 | Size and decompression limits, formula-prefix escaping on export, schema validation on import | Fuzz tests |
| IN-R1 | Disputed delivery of a webhook | 2 | 1 | Delivery log with response codes and hashes (TenantWebhookDelivery) | Logs |
