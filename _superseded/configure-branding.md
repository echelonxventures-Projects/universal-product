# Configure Store Branding

## Quick - Dynamic

```bash
# Set QuickShop branding
curl -X PUT http://localhost:8787/api/admin/settings \
  -H "Content-Type: application/json" \
  -d '{
  "brand": {
    "name": "QuickShop",
    "wordmark": "QuickShop",
    "tagline": "Everything You Need",
    "logo": "🛒",
    "poweredBy": "Powered by QuickShop"
  },
  "theme": {
    "accent": "#FF9900",
    "header": "#007185",
    "primary": "#FFD700"
  }
}'

# Verify
curl http://localhost:8787/api/config
```

---

## All Configurable Settings

| Category | Settings | Example |
|----------|----------|---------|
| **Brand** | name, wordmark, tagline, logo, footerNote | "QuickShop" |
| **Theme** | accent, header, primary colors | #FF9900, #007185 |
| **UI/UX** | layout, font, navigation style | Modern, Minimal |
| **Logo** | emoji, text, SVG, image URL | 🛒 |
| **Fonts** | heading, body, font family | Roboto, Arial |

---

## Full Configuration

```javascript
// Full branding configuration
curl -X PUT http://localhost:8787/api/admin/settings \
  -H "Content-Type: application/json" \
  -d '{
  "brand": {
    "name": "QuickShop",
    "wordmark": "QuickShop",
    "tagline": "Everything You Need, Delivered Fast",
    "logo": "🛒",
    "logoUrl": "https://quickshop.com/logo.svg",
    "favicon": "https://quickshop.com/favicon.ico",
    "poweredBy": "QuickShop Platform",
    "footerNote": "© {year} QuickShop. All rights reserved."
  },
  "theme": {
    "accent": "#FF9900",
    "header": "#007185",
    "primary": "#FFD700",
    "secondary": "#232F3E",
    "linkColor": "#007185",
    "buttonStyle": "rounded"
  },
  "commerce": {
    "currency": "USD",
    "currencySymbol": "$",
    "freeShippingThreshold": 35,
    "taxIncluded": false
  },
  "features": {
    "affiliate": true,
    "reviews": true,
    "wishlist": true,
    "compare": true,
    "liveChat": true,
    "smsSupport": true
  }
}'
```

---

## Access Config

After configuration, access at:

```
http://localhost:8787/admin.html?view=settings
```

All settings are immediately applied without restart.

---

## Dynamic Updates

Settings update in real-time across all pages:

- ✅ Store header logo/name
- ✅ Color scheme
- ✅ Footer text
- ✅ Support email
- ✅ UI/UX preferences

All stored in `config_store` table - no code changes needed.
