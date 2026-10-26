# LUXORA Branding System

## Dynamic Configuration (No Code Changes)

All branding elements are stored in `config_store` table:

```sql
SELECT key, value FROM config_store WHERE key = 'settings';
```

### Configuration Structure

```json
{
  "brand": {
    "name": "QuickShop",
    "wordmark": "QuickShop",
    "tagline": "Everything You Need",
    "logo": "🛒",
    "logoUrl": "https://...",
    "poweredBy": "Powered by QuickShop",
    "footerNote": "© {year} QuickShop"
  },
  "theme": {
    "accent": "#FF9900",
    "header": "#007185",
    "fontDisplay": "Didot",
    "fontBody": "Inter"
  }
}
```

---

## Logo Placement

### Header Logo (Top-left)
```javascript
// In public/js/admin.js line 246
<div class="p-logo">
  <b>{TT.brand?.name || TT.brand?.wordmark}</b>
  <small>Store Console · {TT.tenant.slug}</small>
</div>
```

### Storefront Logo (CSS)
```css
.logo {
  width: 150px;
  height: 40px;
  object-fit: contain;
}
```

---

## Fonts (Typography)

### Configured via theme.fontDisplay & theme.fontBody
```css
/* From theme settings */
font-display: "Didot", "Bodoni MT", serif;
font-body: "Inter", "Helvetica Neue", sans-serif;
```

### Applied Automatically
```css
body {
  font-family: var(--font-body);
}
h1, h2, h3 {
  font-family: var(--font-display);
}
```

---

## Tagline & Copyright

### Tagline
```javascript
// Used in header/subheader
<div>{TT.brand.tagline}</div>
```

### Footer
```javascript
// Footer rendering
<p>{TT.brand.footerNote.replace('{year}', new Date().getFullYear())}</p>
```

---

## Terms & Conditions (T&C)

### Stored in Config
```json
{
  "copy": {
    "terms": "https://...",
    "privacy": "https://...",
    "returnPolicy": "https://..."
  }
}
```

### Footer Links
```javascript
<div class="footer-links">
  <a href="{TT.copy.terms}">Terms & Conditions</a>
  <a href="{TT.copy.privacy}">Privacy Policy</a>
  <a href="{TT.copy.returnPolicy}">Returns</a>
</div>
```

---

## Quick Branding

```bash
# Full branding update
curl -X PUT http://localhost:8787/api/admin/settings \
  -H "Content-Type: application/json" \
  -d '{
  "brand": {
    "name": "QuickShop",
    "wordmark": "QuickShop",
    "tagline": "Everything You Need",
    "logo": "🛒",
    "footerNote": "© 2026 QuickShop"
  },
  "theme": {
    "accent": "#FF9900",
    "header": "#007185",
    "fontDisplay": "Arial",
    "fontBody": "Helvetica"
  },
  "copy": {
    "terms": "https://quickshop.com/terms",
    "privacy": "https://quickshop.com/privacy",
    "returnPolicy": "https://quickshop.com/returns"
  }
}'
```

---

## Runtime Updates

All branding changes apply immediately without restart because:

1. Settings stored in `config_store` table
2. JS files fetch `GET /api/config` on page load
3. All UI components use `TT.brand.*` variables

```
No server restart needed!
```

---

## All Configurable Elements

| Element | Config Path | Example |
|---------|-------------|---------|
| Store Name | `brand.name` | "QuickShop" |
| Wordmark | `brand.wordmark` | "QuickShop" |
| Tagline | `brand.tagline` | "Everything You Need" |
| Logo (Emoji) | `brand.logo` | "🛒" |
| Logo (Image) | `brand.logoUrl` | "https://..." |
| Footer Note | `brand.footerNote` | "© {year} QuickShop" |
| Accent Color | `theme.accent` | "#FF9900" |
| Header Color | `theme.header` | "#007185" |
| Display Font | `theme.fontDisplay` | "Didot" |
| Body Font | `theme.fontBody` | "Inter" |
| Terms URL | `copy.terms` | "https://..." |
| Privacy URL | `copy.privacy` | "https://..." |

