# What only an outside account, person or machine can supply

Everything else runs on this machine: `npm run demo`. Each line says what it is for, what to get, and where it goes.
Credentials are entered in the consoles (stored encrypted), never in code. `npm run preflight` on the server says what is left.

## Needed before the first real customer

| # | What | Get | Where it goes | Until then |
|---|---|---|---|---|
| 1 | Code kept private | GitHub repository set to Private | GitHub → Settings | The repository was public when last checked |
| 2 | A server | A Linux machine with Docker: 2 CPUs, 4 GB memory, 40 GB disk to start | `docker compose up -d` (README, Going live) | `npm run demo` |
| 3 | A domain | A domain, its A record pointing at the server | Platform console → Stores | localhost |
| 4 | TLS certificate | Nothing to buy: Caddy requests it. An email address for the authority | `ACME_EMAIL` in `.env` | http on localhost |
| 5 | Payments (India) | A Razorpay account, KYC done, live key id, key secret and webhook secret | Store console → Payments; webhook address `https://<domain>/api/webhooks/inbound/razorpay?store=<store>` | Local payment page |
| 6 | Email | An SMTP relay, Resend or SendGrid account, with the domain's SPF, DKIM and DMARC records | Master store's console → Payments → Email & SMS senders | Local mailbox |
| 7 | Legal details and review | Business name, address, GSTIN, officers; a lawyer's review of the six legal pages | Store console → Settings → Legal | Demo details |
| 8 | Tax rates confirmed | An accountant's check of GST rates and HSN codes | Tax rules; each item's HSN | Standard 18% |
| 9 | Backups off the machine | An S3-compatible bucket and keys; one restore tried | `LX_BACKUP_S3_*` in `.env` | `data/backups` on this machine |
| 10 | Secrets | Long random passwords, pepper and metrics token | `.env` | Demo passwords |
| 11 | A phone for sign-in | An authenticator app for each admin | Asked for at first sign-in | Not asked in the demo |
| 12 | A real order | One live payment, refund, parcel and return | — | The demo does all four |

## For each extra thing you switch on

| What | Get | Where | Until then |
|---|---|---|---|
| Stripe, PayPal | Accounts and live keys | Store console → Payments | Local payment page |
| SMS | Twilio account (India also needs DLT registration of sender and templates) | Email & SMS senders | Local mailbox |
| Carrier rates and labels | EasyPost account, API key and webhook secret | Platform console → Shipping | Local carrier |
| Instalments without cost | A no-cost EMI offer created with the gateway, and its offer id | The feature's row in the console | Recorded on the order |
| AI assistant | An Anthropic API key and the `@anthropic-ai/sdk` package | Store console → AI | Answers from the store's own knowledge |
| Ads (Meta, Google, TikTok, GA4) | Accounts and tokens | Store console → Marketing | Nothing is sent |
| Single sign-on | An identity provider | Store console → Identity | Email and password |
| Video for live selling | A streaming service | A show's link | A placeholder link |
| Swiss Ephemeris (astrology) | Its licence, if you want it instead of the built-in engine | Astrology settings | Built-in engine |
| Redis, Postgres | Managed services, for more than one machine | `.env` | Built in |

## No stand-in, and not finished: needs the provider first

Adyen, UPI direct, PIX, iDEAL, Klarna, M-Pesa, Tabby and Alipay have no integration; Square and Braintree need rework
(their present specs do not take a shopper's own card). FedEx, UPS, USPS, DHL, Royal Mail, Deutsche Post, Delhivery,
Blue Dart and Correios are listed but reached only through EasyPost where it covers them. Avalara has no integration.
None of these takes an order in production. Each needs the provider's account, test keys and contract before it can be
written and proved. Razorpay already takes UPI, cards, netbanking and wallets.

## Checks by others

A penetration test · a load test on the server you choose · an accessibility review · native speakers' review of the
Hindi, Arabic, Spanish, French and German wording · PCI DSS self-assessment (SAQ A: cards are entered only on the
provider's page) · outside uptime monitoring of `/readyz`.
