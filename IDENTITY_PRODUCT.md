# Identity Product Configuration

## Overview

Identity is now a **full-featured product** in the Global Platform Marketplace that can be sold to stores and external platforms.

## Product Tiers

### Identity Basic (Free - Auto-Installed)
- Email/password authentication
- Session management
- CSRF protection

### Identity Pro ($49/store/month)
**Capabilities:**
- SSO (Okta, Azure AD, Google)
- OAuth/Social Login (Google, Facebook, Apple)
- OTP authentication
- Magic Link (passwordless)
- Biometric (WebAuthn)
- MFA enforcement
- Configurable auth flows

**Features:**
| Feature | Description |
|---------|-------------|
| SSO Providers | Configurable SAML/OIDC providers |
| Social Login | OAuth integrations |
| OTP Delivery | Email, SMS, or both |
| Magic Links | Passwordless authentication |
| Biometric | WebAuthn/FIDO2 support |
| MFA | Require for admins/staff |
| Session Management | Timeout, concurrent sessions |
| Password Policy | Length, complexity, expiry |

---

## Configuration

### Via UI (Easiest)

**Step 1:** Install Identity Pro module
1. Go to `http://localhost:8787/platform.html` → 🧩 Module Marketplace
2. Find **Identity Pro** in Identity category
3. Click **Install** and select stores

**Step 2:** Configure Identity Providers
1. Navigate to `http://localhost:8787/platform.html` → 🔐 Identity
2. Scroll to "Identity Providers" section
3. Click **+ Add Provider**

#### Configure SSO (Okta/Azure AD/Google)
| Field | Description | Example |
|-------|-------------|---------|
| Provider | SSO provider type | Okta, Azure AD, Google, SAML Generic |
| SSO URL | SSO endpoint | https://company.okta.com/sso |
| Domains | Email domains (comma-separated) | company.com,acme.com |
| Entity ID | Provider entity ID | urn:okta:example |

#### Configure OAuth/Social (Google/Facebook/Apple)
| Field | Description | Example |
|-------|-------------|---------|
| Provider | OAuth provider | Google, Facebook, Apple |
| Client ID | OAuth client ID | 123456789.apps.googleusercontent.com |
| Client Secret | OAuth client secret | GOCSPX-abcdefg |
| Redirect URI | Callback URL | https://yourapp.com/callback |

#### Configure OTP (Email/SMS)
| Field | Description | Example |
|-------|-------------|---------|
| Delivery | Send method | Email, SMS, Both |
| From | Email address or phone | noreply@example.com |

#### Configure Magic Link
| Field | Description | Example |
|-------|-------------|---------|
| From Email | Sender email | noreply@example.com |
| Base URL | App base URL | https://yourapp.com |

#### Configure Biometric (WebAuthn)
| Field | Description | Example |
|-------|-------------|---------|
| RP ID | Domain for WebAuthn | yourapp.com |
| RP Name | Display name | Your App Name |

**Step 3:** Configure Settings
- Password policy (length, complexity, expiry)
- MFA requirements
- Session timeout
- Lockout settings

### Via API


#### Purchase for Store
```bash
curl -X POST http://localhost:8787/api/platform/modules/identity-pro/install \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": 1,
    "config": {
      "ssoProviders": "okta,azure",
      "socialProviders": "google,facebook",
      "otpMethod": "both",
      "magicLinkEnabled": true,
      "biometricEnabled": true,
      "mfaRequired": true,
      "passwordMinLength": 12,
      "sessionTimeoutMinutes": 120
    }
  }'
```

#### View Installed Modules
```bash
curl http://localhost:8787/api/admin/modules
```

#### Uninstall Module
```bash
curl -X POST http://localhost:8787/api/platform/modules/identity-pro/uninstall \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": 1}'
```

---

## For External Platforms

Identity can be sold as a standalone product:

### 1. Deploy Identity API
Deploy the `lib/identity.js` module with the full API surface.

### 2. Configure Providers
```javascript
// Configure identity providers
const identity = require("./identity.js");

// Add SSO
await identity.upsertIdentityProvider(tenantId, {
  provider_type: "sso",
  name: "Enterprise SSO",
  enabled: true,
  config: {
    provider: "okta",
    ssoUrl: "https://company.okta.com/sso",
    domains: ["company.com"]
  }
});

// Add OAuth
await identity.upsertIdentityProvider(tenantId, {
  provider_type: "oauth",
  name: "Google Login",
  enabled: true,
  config: {
    clientId: "YOUR_CLIENT_ID",
    clientSecret: "YOUR_SECRET"
  }
});
```

### 3. Integration Points
External platforms can integrate via:
- REST API endpoints
- SDK/Webhook callbacks
- SSO federation

---

## Billing & Monitoring

### Revenue Tracking
Identity Pro purchases appear in:
- Store billing dashboard
- Platform revenue reports
- Monthly subscription ledger

### Monitoring
- Authentication events logged
- Provider usage tracked
- Session metrics available

---

## Auto-Installation

When a new store is provisioned:
- ✅ Identity Basic automatically installed (free)
- ✅ Basic email/password enabled
- ✅ MFA ready for Identity Pro upgrade

---

## Provider Configuration Examples

```bash
# Okta SSO
curl -X PUT http://localhost:8787/api/admin/identity-providers \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "sso",
    "name": "Company Okta",
    "enabled": true,
    "config": {
      "provider": "okta",
      "ssoUrl": "https://company.okta.com/sso",
      "domains": ["company.com"]
    }
  }'

# Google OAuth
curl -X PUT http://localhost:8787/api/admin/identity-providers \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "oauth",
    "name": "Google Login",
    "enabled": true,
    "config": {
      "provider": "google",
      "clientId": "YOUR_CLIENT_ID",
      "clientSecret": "YOUR_SECRET"
    }
  }'
```

---

## Security Features

- Password hashing (BCrypt/Argon2)
- Session management
- Account lockout protection
- MFA enforcement
- WebAuthn support
- Provider-level isolation per tenant
