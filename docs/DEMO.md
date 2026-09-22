# UCII Ω∞ Demo

## Local Demo URL

```
http://localhost:3001
```

## Access Points

| Portal | URL | Description |
|--------|-----|-------------|
| **Admin** | http://localhost:3001/admin | Platform management |
| **Merchant** | http://localhost:3001/merchant | Seller dashboard |
| **Seller** | http://localhost:3001/seller | Inventory management |

## Demo Credentials (Simulated)

### Admin User
- **Email:** admin@echelonx.com
- **Role:** Super Admin
- **Permissions:** Full access to all features

### Merchant User
- **Email:** merchant@example.com
- **Role:** Merchant
- **Permissions:** Products, Orders, Earnings

### Seller User
- **Email:** seller@example.com
- **Role:** Seller
- **Permissions:** Inventory, Sales tracking

## Sample Data

### Products
| SKU | Name | Status |
|-----|------|--------|
| PROD-001 | Premium Widget | Active |
| PROD-002 | Basic Widget | Active |
| PROD-003 | Deluxe Widget | Active |

### Offers
| Code | Type | Value | Status |
|------|------|-------|--------|
| SUMMER25 | Discount | 25% | Active |
| WELCOME10 | Cashback | $10 | Active |

### Orders
| Order # | Status | Total |
|---------|--------|-------|
| ORD-100001 | Delivered | $234.50 |
| ORD-100002 | Shipped | $156.75 |
| ORD-100003 | Processing | $89.00 |

## Getting Started

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the platform:**
   ```bash
   npm run dev
   ```

3. **Open browser:**
   ```
   http://localhost:3001
   ```

4. **Navigate to portals:**
   - Admin: `/admin`
   - Merchant: `/merchant`
   - Seller: `/seller`

## API Access (Backend)

- **Base URL:** http://localhost:3000/api
- **Tenant ID:** tenant-123
- **Auth:** Bearer Token (simulated)

## Docker Setup

```bash
docker-compose up
```

This starts:
- Backend API (port 3000)
- Web UI (port 3001)
- PostgreSQL (port 5432)
- Redis (port 6379)

