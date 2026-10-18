# Multi-Tenant Branding System

## Hierarchy

```
Platform Admin (Global)
├── Global Branding (applies to all stores)
└── Store Permissions (what each store can customize)
    ├── Store 1 → Can change: logo, colors
    ├── Store 2 → Can change: colors only
    └── Store 3 → No customization allowed
```

## Database Schema

```sql
-- Global platform branding
CREATE TABLE platform_branding (
  id INTEGER PRIMARY KEY,
  name TEXT,
  logo TEXT,
  colors TEXT DEFAULT '{}',
  fonts TEXT DEFAULT '{}',
  updated_at TEXT
);

-- Per-store permission overrides
CREATE TABLE store_branding_perms (
  id INTEGER PRIMARY KEY,
  tenant_id INTEGER,
  can_change_name INTEGER DEFAULT 0,
  can_change_logo INTEGER DEFAULT 0,
  can_change_colors INTEGER DEFAULT 0,
  can_change_fonts INTEGER DEFAULT 0,
  can_change_footer INTEGER DEFAULT 0,
  UNIQUE(tenant_id)
);

-- Per-store branding (inherits from platform)
CREATE TABLE store_branding (
  id INTEGER PRIMARY KEY,
  tenant_id INTEGER,
  name TEXT,
  logo TEXT,
  colors TEXT DEFAULT '{}',
  fonts TEXT DEFAULT '{}',
  updated_at TEXT
);
```

## API Flow

```javascript
// Platform sets global branding
POST /api/platform/branding
{
  "global": {
    "name": "QuickShop Network",
    "logo": "🛒",
    "colors": {
      "accent": "#FF9900",
      "header": "#007185"
    }
  }
}

// Platform sets store permissions
PUT /api/platform/branding-permissions/:tenantId
{
  "can_change_name": true,
  "can_change_logo": true,
  "can_change_colors": false,
  "can_change_fonts": false,
  "can_change_footer": true
}

// Store Admin changes permitted fields
PUT /api/store/branding
{
  "name": "QuickShop",
  "logo": "🛒"
}
// ✅ Allowed if permissions permit
```

## Inheritance Logic

```javascript
function getStoreBrand(tenantId) {
  const global = getGlobalBranding();
  const perms = getStorePermissions(tenantId);
  const store = getStoreBranding(tenantId);
  
  return {
    name: store.name || (perms.can_change_name ? null : global.name),
    logo: store.logo || (perms.can_change_logo ? null : global.logo),
    colors: {
      accent: store.colors.accent || (perms.can_change_colors ? null : global.colors.accent),
      header: store.colors.header || (perms.can_change_colors ? null : global.colors.header)
    },
    // ... other fields
  };
}
```

## UI

### Platform Console
- Global branding settings
- Per-store permissions (checkboxes)

### Store Admin
- Only shows permitted customization options
- Grayed out if not permitted

