# UCII Platform Quick Start Guide

## Prerequisites

- Node.js 20+
- npm or yarn
- PostgreSQL (for production)
- Docker (for development)

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

## Running Tests

```bash
npm test
npm run test:watch
```

## Building

```bash
npm run build
```

## API Usage

### Create a Product

```javascript
const { UCIIPlatform } = require('ucii-platform');

const platform = new UCIIPlatform({
  tenantId: 'tenant-123',
  region: 'us-east-1',
  features: { aiCommerce: true }
});

await platform.initialize();

const response = await fetch('http://localhost:3000/products', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sku: 'PROD-001',
    name: 'Premium Widget',
    description: 'High-quality widget',
    categoryIds: ['electronics'],
    status: 'active',
    tenantId: 'tenant-123'
  })
});

const product = await response.json();
console.log(product);
```

### Create and Redeem a Coupon

```javascript
// Create offer
const offerResponse = await fetch('http://localhost:3000/offers', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: 'SAVE20',
    name: '20% Off',
    type: 'discount',
    value: 20,
    currency: 'USD',
    tenantId: 'tenant-123'
  })
});

// Redeem coupon
const redemption = await fetch('http://localhost:3000/coupons/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ code: 'SAVE20' })
});

console.log(await redemption.json());
```

## Configuration

Edit `config/platform.yaml`:

```yaml
version: "1.0.0"
tenant:
  isolation: "separate"
security:
  auth: "oauth2"
  mfa: "optional"
features:
  aiCommerce: true
  marketplaceFederation: true
```

## Production Deployment

See `docs/production-deployment.md` for Kubernetes and Terraform deployment guides.
