/* LUXORA Platform — what a page says about itself before any script runs: its title, description,
   canonical address, sharing card and structured data, written into the page for search engines
   and link previews, in the store's own name. And the store's legal details, filled into the legal
   pages (settings.legal); a part nobody has filled in shows as a gap, never as an invented value. */
"use strict";

const db = () => require("./db.js");
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const settingsOf = t => require("./settings.js").load(t.id);
/* text inside a JSON-LD block can never close it */
const ld = o => '<script type="application/ld+json">' + JSON.stringify(o).replace(/</g, "\\u003c") + "</script>";
const PAGE_TITLES = { "/": "", "/index.html": "", "/results.html": "Search", "/deals.html": "Deals", "/cart.html": "Your bag", "/checkout.html": "Checkout", "/orders.html": "Your orders", "/gift-cards.html": "Gift cards",
  "/customer-service.html": "Customer service", "/privacy.html": "Privacy notice", "/terms.html": "Terms of use", "/returns.html": "Returns and refunds", "/shipping.html": "Shipping", "/cookies.html": "Cookies", "/contact.html": "Contact us", "/sell.html": "Sell", "/messages.html": "Messages", "/reset.html": "Reset your password", "/astro.html": "Astrology" };
const PRIVATE = new Set(["/invoice.html", "/proposal.html", "/trip.html", "/ride.html", "/drive.html", "/cart.html", "/checkout.html", "/orders.html", "/messages.html", "/reset.html", "/session.html", "/console.html", "/registry.html"]);

/* the parts of the head a page gets: { title, html } */
function head(t, pathname, query, origin) {
  const s = settingsOf(t), brand = (s.brand && s.brand.name) || t.name;
  const site = origin || "";
  let title = [PAGE_TITLES[pathname], brand].filter(Boolean).join(" — ") || brand;
  let desc = (s.brand && (s.brand.tagline || s.brand.description)) || "";
  let canonical = site + (pathname === "/index.html" ? "/" : pathname), extra = "", image = "";
  if (pathname === "/product.html") {
    const id = String(query.get("id") || "");
    const p = id ? db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", t.id, id) : null;
    if (p) {
      title = p.title.slice(0, 80) + " — " + brand; canonical = site + "/product.html?id=" + encodeURIComponent(p.id);
      const b = db().all("SELECT text FROM product_bullets WHERE tenant_id=? AND product_id=? ORDER BY pos LIMIT 3", t.id, p.id).map(x => x.text);
      desc = b.join(". ") || p.title;
      const m = money(t), price = +(Number(p.price) * m.fx).toFixed(m.decimals);
      const data = { "@context": "https://schema.org", "@type": "Product", name: p.title, sku: p.id, brand: { "@type": "Brand", name: p.brand }, description: desc,
        offers: { "@type": "Offer", url: canonical, price, priceCurrency: m.currency, availability: "https://schema.org/" + (Number(p.stock) > 0 ? "InStock" : "OutOfStock") } };
      /* only ratings customers of this store left */
      const r = db().get("SELECT COUNT(*) n, AVG(rating) a FROM reviews WHERE tenant_id=? AND product_id=? AND user_id IS NOT NULL", t.id, p.id);
      if (r && r.n > 0) data.aggregateRating = { "@type": "AggregateRating", ratingValue: +Number(r.a).toFixed(1), reviewCount: r.n };
      extra = ld(data) + ld({ "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: brand, item: site + "/" }, { "@type": "ListItem", position: 2, name: p.title, item: canonical }] });
      image = require("./registry.js") && firstImage(p);
    }
  } else if (pathname === "/" || pathname === "/index.html") {
    extra = ld({ "@context": "https://schema.org", "@type": "Organization", name: brand, url: site + "/" })
      + ld({ "@context": "https://schema.org", "@type": "WebSite", name: brand, url: site + "/", potentialAction: { "@type": "SearchAction", target: site + "/results.html?q={search_term_string}", "query-input": "required name=search_term_string" } });
  }
  desc = String(desc || brand).slice(0, 200);
  const html = `<meta name="description" content="${esc(desc)}">` + (PRIVATE.has(pathname) ? '<meta name="robots" content="noindex">' : (site ? `<link rel="canonical" href="${esc(canonical)}">` : ""))
    + `<meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(desc)}"><meta property="og:type" content="website"><meta property="og:site_name" content="${esc(brand)}">`
    + (site ? `<meta property="og:url" content="${esc(canonical)}">` : "") + (image ? `<meta property="og:image" content="${esc(image)}">` : "") + `<meta name="twitter:card" content="${image ? "summary_large_image" : "summary"}">`
    + '<link rel="manifest" href="/manifest.webmanifest">' + extra;
  return { title, html };
}
function firstImage(p) { try { const m = JSON.parse(p.media || "[]"); const i = (Array.isArray(m) ? m : []).find(x => x && /^https:\/\//.test(x.url || x)); return i ? i.url || i : ""; } catch (e) { return ""; } }
/* the currency the store shows, and the rate from the one its prices are kept in */
function money(t) {
  const c = settingsOf(t).commerce, reg = require("./registry.js");
  const co = reg.country(c.country) || {}, base = reg.currency(co.currency) || { code: co.currency, decimals: 2 };
  const cur = (c.currency && reg.currency(c.currency)) || base;
  return { currency: cur.code, decimals: cur.decimals != null ? cur.decimals : 2, fx: cur.code === base.code ? 1 : reg.fxTo(base.code, cur.code) };
}
/* ---------- legal details ---------- */
const LEGAL = require("./seed/settings.json").LEGAL_FIELDS;
function legal(t) { const l = settingsOf(t).legal || {}; return Object.fromEntries(LEGAL.map(f => [f.key, String(l[f.key] || "").trim()])); }
/* what still has to be filled in before the legal pages may be relied on */
function legalGaps(t) { const l = legal(t); return LEGAL.filter(f => f.required && !l[f.key]).map(f => f.label); }
function fill(html, t) {
  if (!html.includes("{{")) return html;
  const l = legal(t), s = settingsOf(t), m = money(t);
  const vars = { ...l, store: (s.brand && s.brand.name) || t.name, currency: m.currency, returnDays: Number(s.commerce.returnDays) > 0 ? String(s.commerce.returnDays) : "" };
  const gaps = legalGaps(t);
  return html.replace(/<!--if-gaps-->([\s\S]*?)<!--end-->/g, (_, x) => gaps.length || !l.reviewedOn ? x : "")
    .replace(/<!--if (\w+)-->([\s\S]*?)<!--end-->/g, (_, k, x) => vars[k] ? x : "")
    .replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] ? esc(vars[k]) : '<mark>[to be completed]</mark>');
}
/* a whole page, in the store's name */
function page(html, t, pathname, query, origin) {
  if (!t) return html;
  const h = head(t, pathname, query, origin);
  return fill(html, t).replace(/<title>[\s\S]*?<\/title>/i, () => "<title>" + esc(h.title) + "</title>").replace(/<meta name="description"[^>]*>\s*/i, "").replace(/<\/head>/i, () => h.html + "</head>");
}
function manifest(t) {
  const s = settingsOf(t), brand = (s.brand && s.brand.name) || t.name, th = s.theme || {};
  const letter = esc((brand.match(/[A-Za-z0-9]/) || ["S"])[0].toUpperCase()), bg = /^#[0-9a-f]{6}$/i.test(th.header || "") ? th.header : "#1f2937";
  return { name: brand, short_name: brand.slice(0, 12), start_url: "/", display: "standalone", background_color: "#ffffff", theme_color: bg,
    icons: [{ src: "data:image/svg+xml," + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" fill="${bg}"/><text x="256" y="350" font-size="288" font-family="Georgia,serif" font-weight="700" fill="#fff" text-anchor="middle">${letter}</text></svg>`), sizes: "any", type: "image/svg+xml" }] };
}

module.exports = { head, page, manifest, legal, legalGaps, LEGAL };
