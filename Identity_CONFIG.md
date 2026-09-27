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

New identity types can be added **without code changes**:

1. **Define provider** via `/admin/identity-providers`
2. **Create handler** in `lib/identity.js` (add to `initiateLogin` switch)
3. **Register UI component** in `public/js/platform.js`

Example for custom provider:
```javascript
// In lib/identity.js, add to initiateLogin:
case 'custom_provider':
  return {
    ok: true,
    action: "custom_redirect",
    url: config.authUrl + "?email=" + encodeURIComponent(email)
  };
```

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
