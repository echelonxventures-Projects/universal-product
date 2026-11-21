# TM-IDENTITY — Identity and access

| Field | Value |
|---|---|
| Scope | U09: registration, login (password, OTP, passkey/FIDO2, TOTP), sessions, social login/federation, role grants and delegation, verification records (KYC/KYB), account recovery |
| Data classes | PII, CREDENTIAL |
| Owner | `ucos:org:identity` |
| References | U09 constitution (ID-L1…); ADR-005; NIST SP 800-63B; OWASP ASVS V2/V3 |

## Entry points
`/auth/*` (OIDC authorize/token, login, OTP send/verify, passkey register/assert), social callback URLs, recovery links, admin role-grant APIs, IdP admin console.

## STRIDE
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| ID-S1 | Credential stuffing and password spraying | 3 | 3 | Breached-password check, rate limits per account/IP/device, risk-based step-up (U69 from P2; `unknown` band until then), passkeys preferred | Login abuse tests |
| ID-S2 | OTP interception (SIM swap, SMS pumping) | 2 | 3 | OTP bound to the session and purpose, 5-minute validity, 3 attempts, SMS pumping guard (per-country caps and anomaly alerts), WhatsApp/email alternatives, passkeys for business users | OTP tests; spend alerts |
| ID-S3 | Social-login account takeover via an unverified email at the provider | 2 | 3 | Link accounts only on a verified email claim plus a re-authentication challenge; never auto-merge on the email string alone | Federation tests |
| ID-S4 | Phishing of business users | 2 | 3 | Phishing-resistant MFA required for every non-customer role (ID-L3) | `SEC-ID-01` |
| ID-T1 | Session fixation or token theft | 2 | 3 | Rotate the session on login and privilege change, HttpOnly/Secure/SameSite cookies, refresh-token rotation with reuse detection, device binding | ASVS V3 tests |
| ID-R1 | Disputed role grants | 2 | 2 | Grants are DecisionRecord-backed for admin roles and audited, with validity ranges | Audit review |
| ID-I1 | User enumeration through login, recovery or registration responses | 3 | 1 | Uniform responses and timing; rate limits | Tests |
| ID-I2 | KYC document exposure | 1 | 3 | Documents stored in U43 with `restricted` class, encryption with tenant keys, access purpose-bound, retention per regulation | Access logs; `SEC-META-01` |
| ID-D1 | OTP or email flooding a victim | 2 | 2 | Per-recipient caps and cooldowns | Tests |
| ID-E1 | Delegation widens authority | 1 | 3 | Delegation is the intersection of the delegator's grants (`AUTH_DELEGATION_WIDENS`), time-boxed | Unit and property tests |
| ID-E2 | Account recovery bypasses MFA | 2 | 3 | Recovery requires possession of a second factor or a verified support process with a cooldown and notification to all contact points | Recovery tests |

## Abuse cases to test
- Verify an OTP issued for `login` against `payment-confirmation` and expect a rejection.
- Register a passkey from a session older than the re-authentication window and expect a step-up.
- Grant a role to yourself through the API without an authority and expect `AUTH_LEVEL_INSUFFICIENT`.
