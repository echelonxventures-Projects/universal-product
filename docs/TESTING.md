# UCII Platform Testing Guide

## Quick Start

### Running the Platform

```bash
# Option 1: Direct development
npm run dev

# Option 2: Docker Compose
docker-compose up
```

### Test Suites

```bash
# Unit tests
npm test

# E2E tests (requires platform running)
npx playwright test

# Integration tests
npm run test:integration
```

## Available UI Portals

### Admin Portal (http://localhost:3000/admin)
- Dashboard with statistics
- Product management (CRUD)
- Order management
- Offer/Promotion management
- Analytics (future)

### Merchant Portal (http://localhost:3000/merchant)
- Earnings dashboard
- Order tracking
- Product listing
- Payout history

### Seller Portal (http://localhost:3000/seller)
- Inventory management
- Sales tracking
- Low stock alerts

## E2E Test Scenarios

1. **Product Lifecycle**
   - Create product
   - View product list
   - Update product

2. **Order Flow**
   - Create order
   - Update order status
   - View order details

3. **Promotion Flow**
   - Create offer
   - Activate offer
   - Validate coupon

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/products | GET | List products |
| /api/products | POST | Create product |
| /api/orders | GET | List orders |
| /api/orders | POST | Create order |
| /api/offers | GET | List offers |
| /api/offers | POST | Create offer |
| /api/coupons/validate | POST | Validate coupon |

## Coverage

- Unit Tests: Core services, event bus, policy engine
- Integration Tests: API endpoints
- E2E Tests: Complete user flows across all portals
