# LUXORA Platform - Complete Flow Diagram

## End-to-End User Journey (Customer to Product Receipt)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         LUXORA PLATFORM - FULL USER FLOW                            │
└─────────────────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────────────┐
                        │   CUSTOMER/USER TYPES       │
                        │  ──────────────────────     │
                        │  • End Consumer            │
                        │  • Business/B2B Customer   │
                        │  • Affiliate/Partner       │
                        │  • Enterprise Client       │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: DISCOVERY & ACCESS                                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Web/App    │    │ Affiliate    │    │   Partner    │    │   Enterprise │      │
│  │   Storefront │    │   Link       │    │   Portal     │    │   Dashboard  │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │                   │               │
│         ▼                   ▼                   ▼                   ▼               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                        GLOBAL PRODUCT CATALOG (UCII)                           │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Master Product Registry (global)                                            │  │
│  │  • Store-specific Assignments (per tenant)                                     │  │
│  │  • Real-time Inventory & Pricing                                               │  │
│  │  • AI-Powered Recommendations                                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                         SEARCH & DISCOVERY                                     │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Semantic Search (AI)                                                       │  │
│  │  • Filters & Facets (category, price, brand, ratings)                         │  │
│  │  • Personalized Results (based on history)                                    │  │
│  │  • Product Comparisons                                                        │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: PRODUCT EVALUATION                                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                         PRODUCT DETAIL PAGE                                    │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Product Information (specs, attributes)                                     │  │
│  │  • Pricing (with taxes, discounts)                                             │  │
│  │  • Reviews & Ratings (UGC)                                                     │  │
│  │  • AI Recommendations ("Customers also viewed")                                │  │
│  │  • Availability & Delivery Estimation                                          │  │
│  │  • Affordability Options (BNPL, installments)                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Add to     │    │   Buy Now    │    │   Save for   │    │   Compare    │      │
│  │    Cart      │    │              │    │  Later       │    │              │      │
│  └──────┬───────┘    └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                                                                       │
│         ▼                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: CART & CHECKOUT                                                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                           SHOPPING CART                                        │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Items & Quantities                                                          │  │
│  │  • Subtotals (item pricing)                                                    │  │
│  │  • Applied Offers/Coupons (GOIP)                                               │  │
│  │  • Gift Balance/Wallet                                                        │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                         CHECKOUT PROCESS                                       │  │
│  │                    ─────────────────────────────────                            │  │
│  │  │  1. Shipping Address │ 2. Delivery Method │ 3. Payment │ 4. Review │  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                      PAYMENT PROCESSING                                        │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Payment Gateway Selection (Stripe, UPI, PayPal, etc.)                      │  │
│  │  • Secure Payment (PCI-compliant)                                             │  │
│  │  • Order Authorization                                                        │  │
│  │  • Wallet/Digital Payment Options                                             │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: ORDER PROCESSING                                                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                        ORDER CREATED                                           │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Order Number Generated                                                      │  │
│  │  • Inventory Reserved                                                          │  │
│  │  • Notification Sent (Email/SMS/Push)                                         │  │
│  │  • Payment Confirmation                                                        │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                         STORE ADMIN VIEW                                       │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Orders Dashboard                                                           │  │
│  │  • Fulfillment Assignment                                                    │  │
│  │  • Inventory Allocation                                                       │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: FULFILLMENT & SHIPPING                                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                        WAREHOUSE/STOCK                                         │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Pick & Pack                                                                 │  │
│  │  • Quality Check                                                               │  │
│  │  • Package Creation                                                            │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                      SHIPPING INTEGRATION                                      │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Carrier Selection (FedEx, UPS, DHL, Local)                                 │  │
│  │  • Rate Quote & Label Generation                                               │  │
│  │  • Package Handoff                                                              │  │
│  │  • Tracking Number Assignment                                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: DELIVERY & TRACKING                                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                        IN-TRANSIT TRACKING                                     │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Real-time Location Updates                                                  │  │
│  │  • Estimated Delivery Time                                                    │  │
│  │  • Customer Notifications (milestones)                                         │  │
│  │  • Live Tracking via SMS/Web                                                   │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                         FINAL DELIVERY                                         │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Delivery Agent Assignment                                                   │  │
│  │  • Route Optimization                                                          │  │
│  │  • Delivery Confirmation (OTP/Sig)                                             │  │
│  │  • Proof of Delivery                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 7: POST-PURCHASE                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                     CUSTOMER RECEIVES PRODUCT                                  │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Unboxing Experience                                                         │  │
│  │  • Product Verification                                                        │  │
│  │  • Usage Instructions                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                      POST-DELIVERY OPTIONS                                     │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Leave Review/Rating                                                         │  │
│  │  • Request Returns/Exchange                                                    │  │
│  │  • Customer Support (Chat/SMS/Ticket)                                          │  │
│  │  • Warranty Registration                                                       │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ AFFILIATE/PARTNER JOURNEY (Parallel Path)                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐              │
│  │  JOIN NETWORK    │    │  PROMOTE LINK    │    │  TRACK CLICKS    │              │
│  │  ─────────────   │    │  ──────────────  │    │  ─────────────   │              │
│  │  Sign up → Get   │    │  Share → Customers │  │  → → → → Conversion│              │
│  │  affiliate code  │    │  click → Track   │    │  → Commission    │              │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘              │
│           │                   │                   │                           │
│           └───────────────────┴───────────────────┘                           │
│                                   │                                           │
│                                   ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                  COMMISSION & PAYOUT                                   │  │
│  │                    ─────────────────────────────────                    │  │
│  │  • Commission Calculated (per rule)                                    │  │
│  │  • Pending → Approved → Paid                                           │  │
│  │  • Payout via Bank/PayPal                                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                       │                                       │
│                                       ▼                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ CUSTOMER SUPPORT FLOW (When Issues Arise)                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐              │
│  │  INITIATE        │    │  TICKET CREATE   │    │  AGENT ASSIGN    │              │
│  │  ─────────────   │    │  ──────────────  │    │  ─────────────   │              │
│  │  Chat/SMS/Email/ │    │  → Priority →    │    │  → Resolution →  │              │
│  │  Phone → Contact │    │  Category →      │    │  → → → → Close   │              │
│  │  Center          │    │  Auto-Create     │    │  → CSAT Survey   │              │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘              │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ PLATFORM & ADMIN OVERSIGHT (Management Layer)                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                           PLATFORM CONSOLE                                     │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Tenant Management (create, configure, bill)                                 │  │
│  │  • Global Products (master catalog)                                            │  │
│  │  • AI/ML Configuration (recommendations, search)                               │  │
│  │  • Security & Audit (compliance, logs)                                         │  │
│  │  • Analytics Dashboard (revenue, orders, affiliates)                           │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                           STORE ADMIN                                          │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Product Management (add, edit, prices)                                      │  │
│  │  • Order Fulfillment (process, ship)                                           │  │
│  │  • Customer Service (tickets, chat)                                            │  │
│  │  • Marketing (promotions, affiliate program)                                   │  │
│  │  • Analytics (store-specific)                                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FINANCIAL & SETTLEMENT FLOW                                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                         PAYMENT SETTLEMENT                                     │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Gateway → Merchant Wallet                                                   │  │
│  │  • Platform Fee Deduction                                                      │  │
│  │  • Affiliate Commission Accrual                                                │  │
│  │  • Settlement Batch Processing                                                 │  │
│  │  • Payout to Partners                                                          │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                         BILLING & INVOICING                                    │  │
│  │                    ─────────────────────────────────                            │  │
│  │  • Invoice Generation (monthly/usage)                                         │  │
│  │  • Tax Calculation (GST/VAT/Sales Tax)                                        │  │
│  │  • Payment Processing                                                         │  │
│  │  • Billing Reports                                                            │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                               │
│                                       ▼                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

─────────────────────────────────────────────────────────────────────────────────────────

KEY INTEGRATIONS & SERVICES
─────────────────────────────────────────────────────────────────────────────────────────

┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   PAYMENT   │ │   SHIPPING  │ │  TAXATION   │ │    AI/ML    │ │ SECURITY &    │
│   GATEWAYS  │ │    CARRIERS │ │     ENGINES │ │    SERVICES │ │  COMPLIANCE   │
│─────────────│ │─────────────│ │─────────────│ │─────────────│ │─────────────│
│ Stripe      │ │ FedEx       │ │ GST/VAT     │ │ Recommendations│ │ OAuth 2.0   │
│ Razorpay    │ │ UPS         │ │ Sales Tax   │ │ Search      │ │ Rate Limiting │
│ PayPal      │ │ DHL         │ │ International│ │ Personalization│ │ Audit Logs  │
│ UPI/Pix     │ │ Local       │ │ Compliance  │ │ Analytics   │ │ Hash Chain    │
│───┬───────┘ │───┬───────┘ │───┬───────┘ │───┬───────┘ │───┬───────┘
    │             │             │             │             │
    └─────────────┴─────────────┴─────────────┴─────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CENTRAL REGISTRIES                                       │
│                     ─────────────────────────────────                             │
│  • Countries/Currencies  • Tax Modes  • Payment/Shipping Providers               │
│  • GOIP Capabilities  • Affiliate Networks  • Commission Rules                   │
│  • Product Categories  • Search Synonyms  • Marketing Channels                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
Frontend (Storefront/Admin)
├── HTML5/CSS3/JavaScript
├── Responsive Design
├── Real-time Updates (Polling/WebSockets)
└── PWA Ready

Backend Services
├── Node.js + Express
├── SQLite/PostgreSQL (multi-tenant DB)
├── REST API Architecture
└── Background Jobs (Redis/Inline)

Core Modules
├── GOIP (Offer/Incentive Platform)
├── UCII (Universal Commerce ID Infrastructure)
├── Billing & Invoicing
├── Affiliate Network
├── Shipping & Tracking
├── Helpdesk & Support
└── Security & Audit

External Integrations
├── Payment Gateways (Stripe, UPI, PayPal)
├── Shipping (FedEx, UPS, DHL)
├── Tax Services (GST, VAT, Sales Tax)
└── AI/ML (Recommendations, Search)
```

## User Types Summary

| User Type | Access Point | Key Capabilities |
|-----------|--------------|------------------|
| **End Customer** | Storefront (`/`) | Browse, Order, Track, Support |
| **Store Admin** | `/admin.html` | Products, Orders, Support, Analytics |
| **Platform Admin** | `/platform.html` | Tenants, Global Products, Billing |
| **Affiliate** | Partner Portal | Track Links, View Commissions, Payouts |
| **Support Agent** | Helpdesk Dashboard | Tickets, Chat, SMS, Resolution |
| **Enterprise** | Custom Portal | Bulk Orders, Contracts, SLAs |

---

**Platform Status:** 100% Complete with 24 Core Features ✅

**All flows are registry-driven and configurable - no code changes required for expansion.**
