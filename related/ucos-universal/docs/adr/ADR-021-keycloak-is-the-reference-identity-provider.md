# ADR-021: Keycloak is the reference identity provider

| Field | Value |
|---|---|
| Status | Accepted (provisional; confirmed by spike S-02 by 2027-01-15) |
| Deciders | Architecture Board (U01 root authority) |
| References | U09 Identity; PHASE1-READINESS S-02; open decision U09 |

## Context
U09 needs a standards-based identity provider for multi-tenant OIDC issuers, passkeys (WebAuthn), step-up ACR, token exchange for agents (RFC 8693), SAML federation for enterprise tenants and social login. The two candidates were Keycloak and Ory.

## Decision
Use **Keycloak** (Apache 2.0) as the reference IdP behind the U09 port, with one realm per tenant group and per-tenant issuers. UCOS code depends only on the U09 port (OIDC/OAuth2 and the admin API wrapper), never on Keycloak internals, so the IdP stays replaceable. Spike S-02 must show 5k logins/s per cell, per-tenant issuer isolation and passkey plus step-up flows. If it fails, the decision reverts to Ory through the same port.

## Alternatives considered
- Ory (Kratos, Hydra, Keto): lighter, API-first, but needs several components to match Keycloak's built-in SAML, admin console and federation.
- Commercial IdP (Auth0/Okta-class): fast to start, but cost per MAU and residency limits do not fit a multi-tenant platform.

## Consequences
**Positive**
- Mature OIDC/SAML, WebAuthn, token exchange, admin console, large operator community.
- Self-hosted in each cell, so residency is satisfied.

**Negative / costs**
- The JVM footprint and realm scaling need tuning; realm-per-tenant limits are tested in S-02.

## Enforcement
S-02 acceptance criteria; `SEC-ID-01`; U09 port conformance tests.
