# TM-WEB — Storefront, tenant admin and public web surfaces

| Field | Value |
|---|---|
| Scope | U64 UI (storefront web, tenant admin, theme/component rendering), U87 SEO (routes, redirects, sitemaps, structured data), U43 Asset (uploads, renditions, public URLs) |
| Data classes | PII on authenticated pages; public catalogue content |
| Owner | `ucos:org:experience` |
| References | U43, U64, U87; OWASP ASVS V5, V12, V14 |

## STRIDE
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| WB-T1 | Stored XSS through tenant content, reviews or product descriptions | 3 | 3 | Rich text is sanitised server-side to an allow-list; contextual output encoding; strict CSP with nonces; no inline event handlers in components | DAST; component tests |
| WB-T2 | Malicious uploads (SVG with script, polyglots, malware) | 2 | 3 | Content-type sniffing, SVG sanitisation or rasterisation, AV scan, serving from a separate cookieless domain | Upload tests |
| WB-S1 | CSRF on admin actions | 2 | 3 | SameSite cookies plus anti-CSRF tokens for cookie sessions; admin APIs use bearer tokens | ASVS tests |
| WB-S2 | Clickjacking of admin or checkout | 2 | 2 | `frame-ancestors` CSP; X-Frame-Options fallback | Header tests |
| WB-T3 | Open redirects via SEO redirects or `returnUrl` | 2 | 2 | Redirect targets restricted to tenant domains; redirect rules governed | Tests |
| WB-I1 | Scraping of prices and catalogue | 3 | 1 | Edge bot management, rate limits; accepted as residual for public data | Monitoring |
| WB-D1 | Cache-busting floods on the storefront | 2 | 2 | CDN with stale-while-revalidate, normalised cache keys, WAF rate rules | Load tests |
| WB-E1 | Theme or custom component code executes with admin privileges | 1 | 3 | Tenant themes are declarative (tokens and layouts); custom components run sandboxed (iframe or WASM) with no access to admin tokens | Review; `SEC-SUPPLY-01` |
| WB-I2 | Admin session left open on shared devices | 2 | 2 | Idle timeout, re-authentication for sensitive actions, session list with remote sign-out | Tests |

## Abuse cases to test
- Store `<img src=x onerror=alert(1)>` in a product description: the storefront must render it inert.
- Upload an SVG containing a script: it must be sanitised or rejected, and served from the asset domain without cookies.
