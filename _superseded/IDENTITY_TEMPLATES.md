# Global Identity Templates

## Overview

Centralized identity configurations that can be applied to new stores during provisioning or to existing stores.

---

## Implementation

### Database (lib/db.js)

Added `platform_identity_templates` table:
```sql
CREATE TABLE IF NOT EXISTS platform_identity_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  name TEXT NOT NULL, 
  description TEXT,
  config TEXT NOT NULL DEFAULT '{}', 
  is_default INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### API Endpoints (lib/api.js)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/platform/identity-templates` | GET | List all templates |
| `/api/platform/identity-templates` | POST | Create template |
| `/api/platform/identity-templates/:id` | GET | Get single template |
| `/api/platform/identity-templates/:id` | PUT | Update template |
| `/api/platform/identity-templates/:id` | DELETE | Delete template |

### Store Provisioning

When creating a store via `POST /api/platform/provisioning/tenants`:

```json
{
  "name": "Acme Corp",
  "slug": "acme",
  "country": "US",
  "identity_template": 1
}
```

The template's configuration is automatically applied to the new store.

### UI (public/js/platform.js)

**Identity Templates** page:
- Create/Edit templates with all identity settings
- Set default template
- View list of saved templates

**Identity** page:
- Dropdown to select and apply templates to current store

---

## Template Configuration

```json
{
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
    "methods": ["totp", "sms"]
  },
  "session": {
    "timeoutMinutes": 120,
    "maxConcurrent": 3
  },
  "login": {
    "maxAttempts": 5,
    "lockoutMinutes": 30
  },
  "providers": [
    {
      "provider_type": "sso",
      "name": "Azure AD",
      "enabled": true,
      "config": {
        "provider": "azure",
        "domains": ["acme.com"]
      }
    },
    {
      "provider_type": "otp",
      "name": "Email OTP",
      "enabled": true,
      "config": { "provider": "email" }
    }
  ]
}
```

---

## Usage Examples

### Create Template
```bash
curl -X POST http://localhost:8787/api/platform/identity-templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Enterprise SSO",
    "description": "SSO + MFA + strong passwords",
    "config": { ... },
    "is_default": true
  }'
```

### Provision Store with Template
```bash
curl -X POST http://localhost:8787/api/platform/provisioning/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "slug": "acme",
    "country": "US",
    "identity_template": 1
  }'
```

### Apply Template to Existing Store
```bash
curl -X POST http://localhost:8787/api/admin/identity-templates/apply \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "tenant_id": 5
  }'
```

---

## Files Modified

| File | Changes |
|------|---------|
| `lib/db.js` | Added `platform_identity_templates` table |
| `lib/api.js` | Added template CRUD endpoints + provision store integration |
| `public/js/platform.js` | Added Identity Templates page + template selector |
| `IDENTITY_TEMPLATES.md` | Documentation |

---

## How It Works

1. **Admin creates template** via UI or API
2. **New store is provisioned** with `identity_template` ID
3. **Store gets configuration**:
   - Password policy
   - MFA settings  
   - Session settings
   - Login settings
   - Identity providers (SSO, OAuth, OTP, etc.)

4. **Apply to existing stores** via UI dropdown

---

## Benefits

- **Consistency** - All stores use same security standards
- **Speed** - Configure identity once, apply everywhere
- **Compliance** - Enforce security policies across stores
- **Scalability** - Easy to update all stores by updating template
