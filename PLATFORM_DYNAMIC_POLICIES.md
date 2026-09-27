# LUXORA Platform - Dynamic Policies (No Code Changes)

All platform behaviors are runtime-configurable through the Platform Console.

## API Endpoints

```
GET    /api/platform/policies           # List all policies
GET    /api/platform/policies/:category # Get single policy
PUT    /api/platform/policies/:category # Update policy (live)
```

---

## 1. Identity & Access Policy

```json
{
  "policy": {
    "minPasswordLength": 8,
    "requireUppercase": true,
    "requireNumbers": true,
    "requireSpecialChars": false,
    "passwordExpiryDays": 90,
    "maxLoginAttempts": 5,
    "lockoutDurationMinutes": 30,
    "sessionTimeoutMinutes": 120,
    "allowGuestCheckout": true,
    "requireEmailVerification": true,
    "allowSocialLogin": false
  }
}
```

---

## 2. SEO Policy

```json
{
  "policy": {
    "titleTemplate": "{{title}} | {{store}}",
    "descriptionTemplate": "{{description}} - {{store}}",
    "robots": "index, follow",
    "sitemapEnabled": true,
    "sitemapMaxEntries": 50000,
    "canonicalUrls": true,
    "ogTags": true,
    "schemaOrg": true,
    "autoGenerateMetaTags": true
  }
}
```

---

## 3. Reviews Policy

```json
{
  "policy": {
    "enabled": true,
    "moderation": "auto",
    "minRating": 1,
    "maxRating": 5,
    "allowPhotoReviews": true,
    "allowVideoReviews": false,
    "requireVerifiedPurchase": true,
    "allowOwnerResponse": true,
    "sortDefault": "newest",
    "maxReviewsPerProduct": 1000
  }
}
```

---

## 4. Search & Discovery Policy

```json
{
  "policy": {
    "minSearchLength": 2,
    "maxSearchResults": 100,
    "facetsEnabled": true,
    "facets": ["dept", "brand", "price", "rating"],
    "autoComplete": true,
    "autocompleteSuggestions": 5,
    "personalizedResults": true,
    "boostBestSellers": true
  }
}
```

---

## 5. Checkout Policy

```json
{
  "policy": {
    "guestCheckout": true,
    "requirePhone": false,
    "allowedCountries": ["US", "CA", "GB"],
    "taxIncludedInPrice": false,
    "freeShippingThreshold": 35,
    "allowGiftMessage": true,
    "allowGiftWrap": true,
    "allowScheduledDelivery": true
  }
}
```

---

## 6. Features Policy

```json
{
  "policy": {
    "reviews": true,
    "wishlist": true,
    "compare": true,
    "deals": true,
    "giftCards": true,
    "coupons": true,
    "affiliate": true,
    "liveChat": true,
    "smsSupport": true,
    "aiRecommendations": true
  }
}
```

---

## 7. Provisioning Policy

```json
{
  "policy": {
    "seedCatalogByDefault": true,
    "defaultPlanId": 1,
    "couponsAllowed": true,
    "fiscalContextsAllowed": true,
    "autoApproveTenants": true,
    "maxTenantsPerOrg": 10
  }
}
```

---

## Usage Examples

```bash
# View all policies
curl http://localhost:8787/api/platform/policies

# Update SEO policy
curl -X PUT http://localhost:8787/api/platform/policies/seo \
  -H "Content-Type: application/json" \
  -d '{"sitemapEnabled":true,"sitemapMaxEntries":100000}'

# Update identity policy
curl -X PUT http://localhost:8787/api/platform/policies/identity \
  -H "Content-Type: application/json" \
  -d '{"minPasswordLength":10,"requireSpecialChars":true}'

# Update review policy
curl -X PUT http://localhost:8787/api/platform/policies/reviews \
  -H "Content-Type: application/json" \
  -d '{"allowPhotoReviews":true,"maxReviewsPerProduct":5000}'
```

---

## UI Location

All policies are configurable from Platform Console:
```
http://localhost:8787/platform.html → Runtime → Policies
```

**All policies take effect immediately - no restart required!** 🚀
