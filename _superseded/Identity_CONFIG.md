# Identity Configuration in Global Platform

## Overview

Global Platform supports **6 identity methods** with full configuration:

| Method | Description | Configuration |
|--------|-------------|---------------|
| **Email/Password** | Native authentication with secure password hashing | Password policy, MFA, session settings |
| **SSO** (SAML/OIDC) | Enterprise single sign-on (Okta, Azure AD, Google) | Provider settings, domain mapping |
| **OAuth/Social** | Third-party OAuth (Google, Facebook, Apple) | Client credentials, scopes |
| **OTP** | One-time password via email/SMS | Expiry, delivery method |
| **Magic Link** | Passwordless login via email | Token expiry, redirects |
| **Biometric** | WebAuthn/WebAuth biometrics | Authenticator settings |

---

## Configuration UI

**Path:** `http://localhost:8787/platform.html` → 🔐 Platform Console → Identity

### Password Policy
- Minimum length (default: 8)
- Require uppercase/numbers/special characters
- Password expiry days (0 = never)

### Multi-Factor Authentication
- Enable MFA globally
- Require for admins/staff
- Methods: TOTP, SMS

### Session Settings
- Session timeout (minutes)
- Max concurrent sessions
- Remember me duration

### Login Settings
- Max failed attempts before lockout
- Lockout duration

---

## Identity Providers

### Add Provider via API

```bash
# Add SSO Provider (SAML)
curl -X PUT http://localhost:8787/api/admin/identity-providers \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "sso",
    "name": "Enterprise SSO",
    "enabled": true,
    "config": {
      "provider": "okta",
      "entityId": "urn:okta:example",
      "ssoUrl": "https://okta.example/sso",
      "domains": ["company.com"],
      "mode": "saml"
    }
  }'

# Add OAuth Provider
curl -X PUT http://localhost:8787/api/admin/identity-providers \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "oauth",
    "name": "Google OAuth",
    "enabled": true,
    "config": {
      "clientId": "YOUR_CLIENT_ID",
      "clientSecret": "YOUR_CLIENT_SECRET",
      "scopes": ["email", "profile"],
      "authUrl": "https://accounts.google.com/o/oauth2/auth",
      "tokenUrl": "https://oauth2.googleapis.com/token"
    }
  }'

# Add OTP Provider
curl -X PUT http://localhost:8787/api/admin/identity-providers \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "otp",
    "name": "SMS OTP",
    "enabled": true,
    "config": {
      "provider": "twilio",
      "from": "+1234567890",
      "expiryMinutes": 10
    }
  }'

# Add Magic Link Provider
curl -X PUT http://localhost:8787/api/admin/identity-providers \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "magic_link",
    "name": "Email Magic Link",
    "enabled": true,
    "config": {
      "provider": "sendgrid",
      "from": "noreply@example.com",
      "expiryMinutes": 15
    }
  }'

# Add Biometric Provider
curl -X PUT http://localhost:8787/api/admin/identity-providers \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "biometric",
    "name": "WebAuthn",
    "enabled": true,
    "config": {
      "rpId": "example.com",
      "rpName": "Example Corp",
      "authenticatorAttachment": "platform"
    }
  }'
```

### Get All Providers
```bash
curl http://localhost:8787/api/admin/identity-providers
```

### Delete Provider
```bash
curl -X DELETE http://localhost:8787/api/admin/identity-providers/{provider_id}
```

---

## Authentication API Endpoints

### Initiate Login
```bash
curl -X POST http://localhost:8787/api/auth/login-init \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "method": "password"
  }'

curl -X POST http://localhost:8787/api/auth/login-init \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "method": "otp"
  }'

curl -X POST http://localhost:8787/api/auth/login-init \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "method": "magic_link",
    "config": {
      "baseUrl": "https://app.example.com"
    }
  }'

curl -X POST http://localhost:8787/api/auth/login-init \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "method": "biometric"
  }'
```

### Verify OTP
```bash
curl -X POST http://localhost:8787/api/auth/login/otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456"
  }'
```

### Verify Magic Link
```bash
curl -X POST http://localhost:8787/api/auth/login/magic \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "token": "abc123xyz"
  }'
```

### Verify Biometric
```bash
curl -X POST http://localhost:8787/api/auth/login/biometric \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "challenge": "challenge123",
    "assertion": {
      "clientDataJSON": "...",
      "authenticatorData": "...",
      "signature": "...",
      "userHandle": "..."
    }
  }'
```

### Manage Identity Methods
```bash
# Get user identity methods
curl http://localhost:8787/api/user/identity-methods

# Link identity method
curl -X POST http://localhost:8787/api/user/identity-methods \
  -H "Content-Type: application/json" \
  -d '{
    "method_type": "otp",
    "identifier": "+1234567890",
    "is_primary": false
  }'

# Unlink identity method
curl -X DELETE http://localhost:8787/api/user/identity-methods/{method_id}

# Set primary method
curl -X PUT http://localhost:8787/api/user/identity-methods/{method_id}/primary
```

---

## Settings API

### Get Settings
```bash
curl http://localhost:8787/api/admin/identity-settings
```

### Update Settings
```bash
curl -X PUT http://localhost:8787/api/admin/identity-settings \
  -H "Content-Type: application/json" \
  -d '{
    "password": {
      "minLength": 12,
      "requireUppercase": true,
      "requireNumbers": true,
      "requireSpecialChars": true,
      "expiryDays": 90
    },
    "mfa": {
      "enabled": true,
      "requireForAdmin": true,
      "requireForStaff": true,
      "methods": ["totp", "sms"]
    },
    "session": {
      "timeoutMinutes": 120,
      "maxConcurrent": 3,
      "rememberMeDays": 30
    },
    "login": {
      "maxAttempts": 5,
      "lockoutMinutes": 30,
      "allowGuestCheckout": true
    }
  }'
```

---

## Infinite Extensibility

New identity kinds are added **without code changes**. Every method is a provider TYPE row in
the registry (`identityProviderTypes`), and each type names a **flow** — the one mechanic the
login engine implements for it:

| Flow | Mechanic | Built-in types using it |
|---|---|---|
| `password` | the native email + password (verified by the store's scrypt path) | `password` |
| `challenge` | a short-lived code the user must repeat — `delivery: code` (server issues and sends it) or `delivery: authenticator` (the user's TOTP app derives it from an enrolled secret) | `otp`, `totp` |
| `link` | a single-use passwordless link delivered out of band | `magic_link` |
| `biometric` | a WebAuthn challenge the device signs | `biometric` |
| `external` | an authority (IdP / directory) authenticates the user and returns an assertion; the platform verifies it with its single `verifyIdToken` primitive and provisions on return | `sso`, `oauth`, `openid`, `ldap` |

The engine dispatches on the **flow**, never on the type key, so:

1. Register the type with its config fields and flow — `POST /api/admin/identity-provider-types`
   (or the **Provider Types** card in the console):
   ```bash
   curl -X POST http://localhost:8787/api/admin/identity-provider-types \
     -H "Content-Type: application/json" \
     -d '{ "key": "passkey", "label": "Passkey", "flow": "biometric", "fields": ["rpId", "rpName"] }'
   ```
2. Configure a provider of that type for a store — **Add Provider** in the console now lists
   registry types and renders their fields automatically.
3. That's it: `POST /api/auth/login-init { "method": "passkey" }` routes to the flow the type
   named. No switch to edit, no second place to register it.

A type naming a flow the engine doesn't know is refused at registration, so a typo can't
produce a method that silently never works.

## Roles are per-store

A store's staff roles are their own data. Every store starts on the shared platform default
and inherits it until an operator deliberately forks that store's set; the first edit forks
the whole set (the store keeps every role it had and diverges from there), and a fork can be
dissolved back to the default.

| Endpoint | Purpose |
|---|---|
| `GET /api/admin/roles` | This store's role set + whether it is forked (`ownSet`) |
| `POST /api/admin/roles` | Create / re-scope a role in this store's own set (team:write) |
| `DELETE /api/admin/roles/:key` | Remove a role nobody on this store holds |
| `POST /api/admin/roles/reset` | Dissolve the fork, inherit the platform default again |
| `POST /api/platform/roles/staff` | Platform console: edit a chosen store's set (`tenant_id`) or the shared default |

A grant removed on one store is refused by that store's console and still allowed on every
store that didn't fork — enforcement reads the requesting store's own set.

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `identity_providers` | Configured identity providers per tenant |
| `user_identity_methods` | User's linked authentication methods |
| `identity_otps` | One-time password tracking |
| `identity_magic_links` | Magic link tokens |
| `identity_biometric_challenges` | WebAuthn challenge tracking |
| `identity_user_authenticators` | Stored biometric credentials |

---

## Security Features

- Password hashing with configurable KDF
- Account lockout after failed attempts
- Session management with timeouts
- MFA enforcement options
- Secure OTP/token expiration
- WebAuthn support for biometrics
