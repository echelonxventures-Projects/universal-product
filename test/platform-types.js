/* LUXORA Platform — every type of commerce platform, end to end: the engines that complete
   them (product options, bookings, make-an-offer, auctions, shopper selling, buyer–seller
   messages, group buying, substitutions), the line terms that carry their prices through the
   bag and checkout, and a platform kind per type that starts from its blend. Runs a real
   server on its own throwaway database; nothing here touches the network. */
"use strict";
const path = require("path");
const fs = require("fs");
const DB = path.join(__dirname, "platform-types.db");
process.env.LX_DB = DB;
const { spawn } = require("child_process");
const PORT = 8889;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const mk = () => {
  const c = new Map();
  const H = () => [...c].map(x => x[0] + "=" + x[1]).join("; ");
  return async (p, m, b) => {
    const o = { method: m || "GET", headers: Object.assign({ Cookie: H() }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}) };
    if (b !== undefined) o.body = JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const text = await r.text();
    let body; try { body = JSON.parse(text); } catch (e) { body = { _raw: text }; }
    return { status: r.status, body };
  };
};
const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };
const Q = "?store=luxora";
const shopper = async tag => {
  const C = mk(); await C("/api/session" + Q);
  const r = await C("/api/auth/register" + Q, "POST", { name: "Pat " + tag, email: "pat-" + tag + "@example.com", password: "Correct-Horse-" + tag + "-9" });
  if (r.status !== 200) throw new Error("register " + tag + " " + JSON.stringify(r.body));
  return C;
};
const sqlAt = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB, LX_LOG: "", LX_OFFLINE: "1" }, stdio: ["ignore", "ignore", "pipe"] });
  let stderr = ""; srv.stderr.on("data", d => { stderr += d; });
  for (let i = 0; i < 120 && !(await alive()); i++) await sleep(500);
  if (!(await alive())) { console.error("server failed to boot\n" + stderr); process.exit(1); }
  const db = require(path.join(__dirname, "..", "lib", "db.js"));

  try {
    const A = mk(); await A("/api/session" + Q);
    ok((await A("/api/auth/login" + Q, "POST", { email: "admin@luxora.shop", password: "admin123" })).status === 200, "store admin signs in");
    const P = mk(); await P("/api/session");
    ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "platform owner signs in");
    for (const k of ["product_options", "bookings", "price_negotiation", "auctions", "peer_listings", "conversations", "group_buying", "substitutions"])
      ok((await A("/api/capabilities/enable" + Q, "POST", { capability: k })).status === 200, "switches on " + k);
    const tune = (k, param, value) => A("/api/capabilities/param" + Q, "POST", { capability: k, param, value });
    /* many new accounts checking out from one address in seconds is what risk screening blocks */
    await A("/api/capabilities/disable" + Q, "POST", { capability: "fraud_screen" });
    const pick = n => db.all("SELECT id, price FROM products WHERE tenant_id=1 AND lifecycle='published' AND deleted_at IS NULL AND stock > 20 AND price > 40 AND price < 900 ORDER BY id LIMIT ?", n);
    const [p1, p2, p3, p4, p5, p6, p7] = pick(7);
    const cart = async C => (await C("/api/cart" + Q)).body;
    const checkout = (C, extra) => C("/api/checkout" + Q, "POST", Object.assign({ name: "Pat", address: "1 Main St", city: "Springfield", zip: "12345", gateway: "cod" }, extra || {}));
    const emptyCart = async C => { for (const it of (await cart(C)).items) await C(`/api/cart/${encodeURIComponent(it.product.id)}${Q}&line=${encodeURIComponent(it.line)}`, "DELETE"); };

    console.log("▸ PRODUCT OPTIONS — modifiers, add-ons, personal text");
    {
      const size = await A("/api/admin/options" + Q, "POST", { code: "size", name: "Size", kind: "choice", min_select: 1, max_select: 1, values: [{ code: "s", name: "Small" }, { code: "l", name: "Large", price_delta: 3 }] });
      const extras = await A("/api/admin/options" + Q, "POST", { code: "extras", name: "Extras", kind: "choice", min_select: 0, max_select: 2, values: [{ code: "cheese", name: "Cheese", price_delta: 1.5 }, { code: "olives", name: "Olives", price_delta: 1 }, { code: "basil", name: "Basil", price_delta: 0.5 }] });
      const note = await A("/api/admin/options" + Q, "POST", { code: "engrave", name: "Engraving", kind: "text", min_select: 0, max_length: 12 });
      ok(size.status === 200 && extras.status === 200 && note.status === 200 && size.body.group.values.length === 2, "option groups are defined once with their values", size.body);
      const at = await A(`/api/admin/options/products/${encodeURIComponent(p1.id)}${Q}`, "PUT", { groups: [size.body.group.id, extras.body.group.id, note.body.group.id] });
      ok(at.status === 200 && at.body.groups.length === 3, "and attached to a product");
      const S = await shopper("opt");
      const pp = (await S(`/api/products/${encodeURIComponent(p1.id)}${Q}`)).body;
      ok(pp.options.length === 3 && pp.options[0].values.some(v => v.code === "l"), "the product page offers them");
      ok((await S("/api/cart" + Q, "POST", { id: p1.id, qty: 1, terms: { options: { extras: ["cheese"] } } })).status === 400, "a required group must be chosen");
      ok((await S("/api/cart" + Q, "POST", { id: p1.id, qty: 1, terms: { options: { size: ["l"], extras: ["cheese", "olives", "basil"] } } })).status === 400, "a group's maximum holds");
      ok((await S("/api/cart" + Q, "POST", { id: p1.id, qty: 1, terms: { options: { size: ["xl"] } } })).status === 400, "an unknown value is refused");
      ok((await S("/api/cart" + Q, "POST", { id: p1.id, qty: 1, terms: { options: { size: ["s"], engrave: "far too long for it" } } })).status === 400, "personal text is limited");
      await S("/api/cart" + Q, "POST", { id: p1.id, qty: 2, terms: { options: { size: ["l"], extras: ["cheese"], engrave: "AB" } } });
      await S("/api/cart" + Q, "POST", { id: p1.id, qty: 1, terms: { options: { size: ["s"] } } });
      const c = await cart(S);
      const big = c.items.find(i => (i.term_labels || []).some(l => /Large/.test(l))), small = c.items.find(i => (i.term_labels || []).some(l => /Small/.test(l)));
      ok(c.items.length === 2 && big && small, "the same product with different options is two lines", c.items.map(i => i.term_labels));
      ok(big && Math.abs(big.unitBase - (p1.price + 4.5)) < 0.01 && big.qty === 2, "a line's options add their price changes", big && big.unitBase);
      ok(small && Math.abs(small.unitBase - p1.price) < 0.01, "a plain choice adds nothing");
      ok(big && big.term_labels[0].includes("Engraving: “AB”"), "personal text is shown on the line", big && big.term_labels);
      const co = await checkout(S);
      ok(co.status === 200, "checkout takes both lines", co.body);
      const oi = db.all("SELECT * FROM order_items WHERE order_id=(SELECT id FROM orders WHERE num=?)", co.body.order.num);
      ok(oi.length === 2 && oi.some(x => /Large/.test(x.terms)), "the order keeps each line's options", oi.map(x => x.terms));
      await A("/api/admin/options" + Q, "POST", { id: extras.body.group.id, code: "extras", name: "Extras", kind: "choice", values: [{ code: "olives", name: "Olives", price_delta: 1 }] });
      await S("/api/cart" + Q, "POST", { id: p1.id, qty: 1, terms: { options: { size: ["s"], extras: ["olives"] } } });
      const k = await P("/api/platform/registries/optionKinds", "POST", { item: { key: "gift_note", name: "Gift note", takes_text: true } });
      ok(k.status === 200, "a new kind of option group is a registry row");
      await emptyCart(S);
      /* services done for the item, plans that run for months, artwork proofed before making, samples */
      const pX = p6;
      const fit = await A("/api/admin/options" + Q, "POST", { code: "fit", name: "Installation", kind: "service", values: [{ code: "install", name: "Install at home", price_delta: 25 }] });
      const cover = await A("/api/admin/options" + Q, "POST", { code: "cover", name: "Protection", kind: "plan", values: [{ code: "two_years", name: "Two years", price_delta: 40, months: 24 }] });
      const art = await A("/api/admin/options" + Q, "POST", { code: "art", name: "Your artwork", kind: "artwork", min_select: 0, max_length: 200 });
      const smp = await A("/api/admin/options" + Q, "POST", { code: "sample", name: "Sample", kind: "sample", values: [{ code: "swatch", name: "Swatch", price_delta: 2 }] });
      ok(cover.body.group.values[0].extra.months === 24, "a plan's value declares its months");
      await A(`/api/admin/options/products/${encodeURIComponent(pX.id)}${Q}`, "PUT", { groups: [fit.body.group.id, cover.body.group.id, art.body.group.id, smp.body.group.id] });
      await S("/api/cart" + Q, "POST", { id: pX.id, qty: 1, terms: { options: { fit: ["install"], cover: ["two_years"], art: "https://example.com/art.png" } } });
      const big2 = (await S("/api/cart" + Q)).body.items.find(i => i.product.id === pX.id && !/Swatch/.test([].concat(i.term_labels).join(" ")));
      ok(big2 && Math.abs(big2.unitBase - (pX.price + 65)) < 0.01, "a service and a plan add their prices to the line", big2 && big2.unitBase);
      const s3 = await S("/api/cart" + Q, "POST", { id: pX.id, qty: 5, terms: { options: { sample: ["swatch"] } } });
      const sampleLine = (await S("/api/cart" + Q)).body.items.find(i => i.product.id === pX.id && /Swatch/.test([].concat(i.term_labels).join(" ")));
      ok(sampleLine && Math.abs(sampleLine.unitBase - 2) < 0.01 && sampleLine.qty <= 2, "a sample sets the line's price and caps how many a bag holds", [s3.status, sampleLine && sampleLine.unitBase, sampleLine && sampleLine.qty]);
      const co2 = await checkout(S);
      ok(co2.status === 200, "checkout takes them", co2.body);
      const fu = (await A("/api/admin/options/follow-ups" + Q)).body.followUps.filter(f => f.order_id === db.get("SELECT id FROM orders WHERE num=?", co2.body.order.num).id);
      const visit = fu.find(f => f.group_code === "fit"), plan = fu.find(f => f.group_code === "cover"), proof = fu.find(f => f.group_code === "art");
      ok(visit && visit.state && !plan.next.length && plan.ends_at && proof && proof.detail.includes("art.png"), "the order leaves a visit to schedule, a plan in force until its end, and a proof to send", fu.map(f => [f.group_code, f.status, f.ends_at]));
      await A("/api/admin/options/follow-ups/" + visit.id + Q, "POST", { action: "schedule", scheduled_for: "2030-01-02 10:00" });
      await A("/api/admin/options/follow-ups/" + proof.id + Q, "POST", { action: "send_proof", proof_url: "https://example.com/proof.png" });
      const mine = (await S("/api/options/follow-ups" + Q)).body.followUps.find(f => f.id === proof.id);
      ok(mine && mine.awaiting, "the shopper sees the proof awaiting their answer");
      const ans = await S("/api/options/follow-ups/" + proof.id + Q, "POST", { action: "approve" });
      ok(ans.status === 200 && ans.body.followUp.state.key === mine.next.find(n => n !== "open"), "and approves it", ans.body);
      ok((await S("/api/options/follow-ups/" + visit.id + Q, "POST", { action: "complete" })).status === 409, "a shopper cannot close the store's own work");
      await emptyCart(S);
    }

    console.log("▸ BOOKINGS — appointments and stays");
    let S2;
    {
      const allWeek = Object.fromEntries([0, 1, 2, 3, 4, 5, 6].map(d => [String(d), [["00:00", "23:59"]]]));
      const stylist = await A("/api/admin/bookings/resources" + Q, "POST", { code: "stylist-1", name: "Stylist One", kind: "staff", capacity: 1, tz: "UTC", hours: allWeek });
      ok(stylist.status === 200 && stylist.body.resource.hours["3"], "a resource has weekly hours in its own zone", stylist.body);
      ok((await A("/api/admin/bookings/resources" + Q, "POST", { code: "bad", name: "x", hours: { 9: [["09:00", "17:00"]] } })).status === 400, "hours are keyed by weekday");
      const cfg = await A(`/api/admin/bookings/products/${encodeURIComponent(p2.id)}${Q}`, "PUT", { mode: "timed", resource_ids: [stylist.body.resource.id], duration_min: 60, step_min: 60 });
      ok(cfg.status === 200 && cfg.body.config.mode_row.engine === "slots", "a product is booked in time slots", cfg.body);
      S2 = await shopper("book");
      const pp = (await S2(`/api/products/${encodeURIComponent(p2.id)}${Q}`)).body;
      ok(pp.booking && pp.booking.resources.length === 1, "the product page says it is bookable");
      const day = new Date(Date.now() + 2 * 864e5).toISOString().slice(0, 10);
      const av = await S2(`/api/bookings/availability${Q}&product=${encodeURIComponent(p2.id)}&date=${day}`);
      ok(av.status === 200 && av.body.slots.length >= 23, "a whole open day offers its hourly slots", av.body.slots && av.body.slots.length);
      const slot = av.body.slots[10];
      const h = await S2("/api/bookings/hold" + Q, "POST", { product_id: p2.id, start: slot.start });
      ok(h.status === 200 && h.body.booking.state.key === "held", "the shopper holds a slot", h.body);
      const other = await shopper("book2");
      ok((await other("/api/bookings/hold" + Q, "POST", { product_id: p2.id, start: slot.start })).status === 409, "a full slot cannot be held twice");
      ok(!(await S2(`/api/bookings/availability${Q}&product=${encodeURIComponent(p2.id)}&date=${day}`)).body.slots.some(x => x.start === slot.start), "and drops out of availability");
      ok((await S2("/api/bookings/hold" + Q, "POST", { product_id: p2.id, start: slot.start.replace(":00:00", ":30:00") })).status === 400, "a time between slots is refused");
      const add = await S2("/api/cart" + Q, "POST", { id: p2.id, qty: 3, terms: { booking: { id: h.body.booking.id } } });
      const line = add.body.items.find(i => i.line_terms && i.line_terms.booking);
      ok(add.status === 200 && line && line.qty === 1 && /Stylist One/.test(line.term_labels[0]), "the booking rides on its line, one per line", line);
      const co = await checkout(S2);
      ok(co.status === 200, "checkout confirms it", co.body);
      const b = db.get("SELECT * FROM bookings WHERE id=?", h.body.booking.id);
      ok(b.status === "confirmed" && b.order_id && !b.hold_until, "the booking is confirmed against the order", b);
      const ci = await A(`/api/admin/bookings/${b.id}${Q}`, "POST", { action: "check_in" });
      ok(ci.status === 200 && ci.body.booking.state.key === "checked_in", "staff check the customer in");
      /* a lapsed hold */
      const h2 = await other("/api/bookings/hold" + Q, "POST", { product_id: p2.id, start: av.body.slots[12].start });
      db.run("UPDATE bookings SET hold_until='2000-01-01 00:00:00' WHERE id=?", h2.body.booking.id);
      ok((await other("/api/cart" + Q, "POST", { id: p2.id, terms: { booking: { id: h2.body.booking.id } } })).status === 400, "a lapsed hold cannot go in the bag");
      ok((await A("/api/admin/bookings/sweep" + Q, "POST", {})).body.expired === 1, "and the sweep expires it");
      /* a stay, priced per night */
      const room = await A("/api/admin/bookings/resources" + Q, "POST", { code: "room-1", name: "Garden Room", kind: "room", capacity: 1, tz: "UTC", hours: Object.fromEntries([0, 1, 2, 3, 4, 5, 6].map(d => [String(d), [["15:00", "23:00"]]])) });
      await A(`/api/admin/bookings/products/${encodeURIComponent(p3.id)}${Q}`, "PUT", { mode: "stay", resource_ids: [room.body.resource.id], min_units: 1, max_units: 14 });
      const from = new Date(Date.now() + 5 * 864e5).toISOString().slice(0, 10), to = new Date(Date.now() + 8 * 864e5).toISOString().slice(0, 10);
      const stay = await S2("/api/bookings/hold" + Q, "POST", { product_id: p3.id, from, to });
      ok(stay.status === 200 && stay.body.booking.units === 3, "a stay of three nights is held", stay.body);
      const sc = await S2("/api/cart" + Q, "POST", { id: p3.id, terms: { booking: { id: stay.body.booking.id } } });
      const sl = sc.body.items.find(i => i.line_terms && i.line_terms.booking);
      ok(sl && Math.abs(sl.unitBase - p3.price * 3) < 0.01, "and priced per night", sl && sl.unitBase);
      ok((await S2(`/api/bookings/${stay.body.booking.id}/cancel${Q}`, "POST", {})).status === 200, "a held stay can be cancelled");
      await emptyCart(S2);
    }

    console.log("▸ MAKE AN OFFER");
    {
      const S = await shopper("offer");
      ok((await S("/api/price-offers" + Q, "POST", { product_id: p4.id, amount: +(p4.price * 0.3).toFixed(2) })).status === 400, "an offer under the floor is refused");
      ok((await S("/api/price-offers" + Q, "POST", { product_id: p4.id, amount: p4.price })).status === 400, "an offer at the list price is refused");
      const o = await S("/api/price-offers" + Q, "POST", { product_id: p4.id, amount: +(p4.price * 0.7).toFixed(2), qty: 2 });
      ok(o.status === 200 && o.body.offer.state.key === "open" && !o.body.offer.awaiting_you, "a fair offer waits for the seller", o.body);
      ok((await S(`/api/price-offers/${o.body.offer.id}${Q}`, "POST", { action: "accept" })).status === 409, "the shopper cannot accept their own offer");
      const ctr = await A(`/api/admin/price-offers/${o.body.offer.id}${Q}`, "POST", { action: "counter", amount: +(p4.price * 0.85).toFixed(2) });
      ok(ctr.status === 200 && ctr.body.offer.state.key === "countered", "the store counters", ctr.body);
      const acc = await S(`/api/price-offers/${o.body.offer.id}${Q}`, "POST", { action: "accept" });
      ok(acc.status === 200 && acc.body.offer.agreed && Math.abs(acc.body.offer.amount - p4.price * 0.85) < 0.02, "the shopper accepts the counter — the counter is the price", acc.body);
      const add = await S("/api/cart" + Q, "POST", { id: p4.id, qty: 5, terms: { offer: { id: o.body.offer.id } } });
      const line = add.body.items.find(i => i.line_terms && i.line_terms.offer);
      ok(line && line.qty === 2 && Math.abs(line.unitBase - p4.price * 0.85) < 0.02, "the agreed price holds for the agreed quantity", line && [line.qty, line.unitBase]);
      ok((await checkout(S)).status === 200, "the shopper buys at it");
      ok(db.get("SELECT status FROM price_offers WHERE id=?", o.body.offer.id).status === "used", "and the offer is used up");
      await tune("price_negotiation", "auto_accept_pct", 90);
      const auto = await S("/api/price-offers" + Q, "POST", { product_id: p4.id, amount: +(p4.price * 0.95).toFixed(2) });
      ok(auto.body.offer.agreed, "an offer over the store's threshold is accepted at once", auto.body);
      await tune("price_negotiation", "auto_accept_pct", 0);
    }

    console.log("▸ AUCTIONS — automatic bidding, reserve, last-minute protection");
    {
      const ends = new Date(Date.now() + 3600e3).toISOString();
      const a = await A("/api/admin/auctions" + Q, "POST", { product_id: p5.id, start_price: 10, reserve_price: 80, ends_at: ends });
      ok(a.status === 200 && a.body.auction.live && a.body.auction.next_bid === 10, "staff open an auction from 10", a.body);
      const id = a.body.auction.id;
      const B1 = await shopper("bid1"), B2 = await shopper("bid2");
      ok((await B1(`/api/auctions/${id}/bid${Q}`, "POST", { max_amount: 5 })).status === 400, "a bid under the start is refused");
      const b1 = await B1(`/api/auctions/${id}/bid${Q}`, "POST", { max_amount: 50 });
      ok(b1.status === 200 && b1.body.auction.leading && b1.body.auction.current_price === 10 && !b1.body.auction.reserve_met, "the first bidder leads at the start, the reserve not met", b1.body);
      const b2 = await B2(`/api/auctions/${id}/bid${Q}`, "POST", { max_amount: 40 });
      ok(b2.body.auction.outbid && b2.body.auction.current_price === 41, "a lower maximum is outbid at once — one step above it", b2.body);
      const b3 = await B2(`/api/auctions/${id}/bid${Q}`, "POST", { max_amount: 120 });
      ok(b3.body.auction.leading && b3.body.auction.current_price === 80 && b3.body.auction.reserve_met, "a higher maximum leads, and the price rises to the reserve once it is met", b3.body);
      const note = db.get("SELECT * FROM notifications WHERE kind='auction_update' AND owner=(SELECT owner FROM auction_bids WHERE auction_id=? ORDER BY id LIMIT 1) ORDER BY id DESC", id);
      ok(note && /outbid/.test(note.title), "the first bidder is told they were outbid", note);
      db.run("UPDATE auctions SET ends_at=? WHERE id=?", sqlAt(Date.now() + 60e3), id);
      await B1(`/api/auctions/${id}/bid${Q}`, "POST", { max_amount: 90 });
      const ext = db.get("SELECT ends_at FROM auctions WHERE id=?", id).ends_at;
      ok(new Date(ext.replace(" ", "T") + "Z").getTime() > Date.now() + 2 * 60e3, "a last-minute bid extends the end", ext);
      db.run("UPDATE auctions SET ends_at=? WHERE id=?", sqlAt(Date.now() - 1000), id);
      const mine = (await B2("/api/auctions/mine" + Q)).body.auctions.find(x => x.id === id);
      /* the runner-up's most was 90, where the store's step is 1 */
      ok(mine && mine.won && mine.final_price === 91, "at the end the leader wins at one step above the runner-up", mine);
      ok((await B1("/api/cart" + Q, "POST", { id: p5.id, terms: { auction: { id } } })).status === 404, "only the winner can buy at the winning price");
      const add = await B2("/api/cart" + Q, "POST", { id: p5.id, qty: 3, terms: { auction: { id } } });
      const line = add.body.items.find(i => i.line_terms && i.line_terms.auction);
      ok(line && line.qty === 1 && line.unitBase === 91, "the winner buys one at the winning bid", line);
      ok((await checkout(B2)).status === 200 && db.get("SELECT status FROM auctions WHERE id=?", id).status === "paid", "and the auction is paid");
      const bn = await A("/api/admin/auctions" + Q, "POST", { product_id: p6.id, start_price: 20, buy_now_price: 300, ends_at: ends });
      ok(bn.body.auction.buy_now_price === 300, "an auction can offer buy-it-now");
      const bnx = await B1(`/api/auctions/${bn.body.auction.id}/buy-now${Q}`, "POST", {});
      ok(bnx.status === 200 && bnx.body.auction.won && bnx.body.auction.final_price === 300, "buying it now ends it at once", bnx.body);
    }

    console.log("▸ SHOPPER SELLING, OFFERS AND MESSAGES BETWEEN SHOPPERS");
    {
      const seller = await shopper("seller");
      const dept = db.get("SELECT key FROM departments WHERE tenant_id=1 AND active=1 ORDER BY position LIMIT 1").key;
      const l = await seller("/api/listings" + Q, "POST", { title: "Vintage film camera", description: "Works perfectly, light wear", price: 120, qty: 1, condition: "used", dept });
      ok(l.status === 200 && l.body.listing.state.key === "draft", "a shopper drafts a listing", l.body);
      ok((await seller("/api/listings" + Q, "POST", { title: "x", price: 5, condition: "mint-ish" })).status === 400, "conditions come from the registry");
      ok((await seller(`/api/listings/${l.body.listing.id}/action${Q}`, "POST", { action: "approve" })).status === 403, "a seller cannot approve their own listing");
      const sub = await seller(`/api/listings/${l.body.listing.id}/action${Q}`, "POST", { action: "submit" });
      ok(sub.body.listing.state.key === "submitted", "and submits it for review");
      const rev = await A(`/api/admin/listings/${l.body.listing.id}${Q}`, "POST", { action: "approve" });
      ok(rev.status === 200 && rev.body.listing.on_sale && rev.body.listing.product_id, "staff approve it — it is on sale as a product", rev.body);
      const pid = rev.body.listing.product_id;
      const buyer = await shopper("buyer");
      const pp = (await buyer(`/api/products/${encodeURIComponent(pid)}${Q}`)).body;
      ok(pp.product && pp.sold_by_shopper === "Pat", "the product page says a shopper sells it", pp.sold_by_shopper);
      const conv = await buyer("/api/conversations" + Q, "POST", { subject: "product", ref: pid, body: "Does it come with a lens? Email me at me@example.com" });
      ok(conv.status === 200 && conv.body.conversation.with === "Pat" && /\[hidden\]/.test(conv.body.messages[0].body), "a buyer messages the seller — contact details hidden", conv.body);
      const inbox = (await seller("/api/conversations" + Q)).body.conversations;
      ok(inbox.length === 1 && inbox[0].unread === 1 && inbox[0].side === "seller", "the seller sees it unread");
      await seller(`/api/conversations/${conv.body.conversation.id}${Q}`, "POST", { body: "Yes, a 50mm" });
      ok((await buyer(`/api/conversations/${conv.body.conversation.id}${Q}`)).body.messages.length === 2, "and answers");
      ok((await mk()(`/api/conversations/${conv.body.conversation.id}${Q}`)).status === 401, "nobody else can read it");
      const off = await buyer("/api/price-offers" + Q, "POST", { product_id: pid, amount: 100 });
      ok(off.status === 200, "the buyer makes an offer on the listing");
      ok((await A(`/api/admin/price-offers/${off.body.offer.id}${Q}`, "POST", { action: "accept" })).status === 404, "staff do not answer for a shopper's listing");
      const received = (await seller("/api/price-offers" + Q)).body.received;
      ok(received.some(x => x.id === off.body.offer.id && x.awaiting_you === true), "the seller sees the offer they received, and that it is their move");
      const acc = await seller(`/api/price-offers/${off.body.offer.id}${Q}`, "POST", { action: "accept" });
      ok(acc.status === 200 && acc.body.offer.agreed, "the seller accepts", acc.body);
      await buyer("/api/cart" + Q, "POST", { id: pid, terms: { offer: { id: off.body.offer.id } } });
      const co = await checkout(buyer);
      ok(co.status === 200, "the buyer buys at the agreed price", co.body);
      const lst = db.get("SELECT * FROM peer_listings WHERE id=?", l.body.listing.id);
      ok(lst.sold === 1 && lst.status === "sold", "the listing is sold out", lst);
      const e = db.get("SELECT * FROM peer_earnings WHERE listing_id=?", lst.id);
      ok(e && e.status === "pending" && e.commission === 10 && e.net === 90, "the proceeds less 10% commission are held", e);
      db.run("UPDATE peer_earnings SET release_at='2000-01-01 00:00:00' WHERE id=?", e.id);
      const before = db.get("SELECT balance FROM wallets WHERE tenant_id=1 AND owner=?", lst.owner);
      require(path.join(__dirname, "..", "lib", "listings.js")).releaseDue(1);
      const after = db.get("SELECT balance FROM wallets WHERE tenant_id=1 AND owner=?", lst.owner);
      ok(after && after.balance - (before ? before.balance : 0) === 90, "and credited to the seller's wallet after the hold", [before, after]);
    }

    console.log("▸ GROUP BUYING");
    {
      const g = await A("/api/admin/group-buys" + Q, "POST", { product_id: p7.id, group_price: +(p7.price * 0.6).toFixed(2), min_members: 2, max_members: 3, ends_at: new Date(Date.now() + 3600e3).toISOString() });
      ok(g.status === 200 && g.body.group.needed === 2, "a group price needs two members", g.body);
      const M1 = await shopper("grp1");
      const pp = (await M1(`/api/products/${encodeURIComponent(p7.id)}${Q}`)).body;
      ok(pp.group && pp.group.joinable, "the product page offers the group");
      const add = await M1("/api/cart" + Q, "POST", { id: p7.id, qty: 1, terms: { group: { id: g.body.group.id } } });
      const line = add.body.items.find(i => i.line_terms && i.line_terms.group);
      ok(line && Math.abs(line.unitBase - p7.price * 0.6) < 0.02, "joining buys at the group price");
      const co = await checkout(M1);
      ok(co.status === 200 && (await M1("/api/group-buys" + Q)).body.groups[0].members === 1, "the shopper is a member", co.body);
      ok((await M1("/api/cart" + Q, "POST", { id: p7.id, terms: { group: { id: g.body.group.id } } })).status === 400, "and cannot join twice");
      db.run("UPDATE group_campaigns SET ends_at=? WHERE id=?", sqlAt(Date.now() - 1000), g.body.group.id);
      await A("/api/admin/group-buys/tick" + Q, "POST", {});
      const gr = (await M1("/api/group-buys" + Q)).body.groups[0];
      ok(gr.state.key === "failed", "a group that fell short fails", gr);
      const o = db.get("SELECT status FROM orders WHERE num=?", co.body.order.num);
      const w = db.get("SELECT balance FROM wallets WHERE tenant_id=1 AND owner LIKE '%:u:%' AND owner=(SELECT owner FROM orders WHERE num=?)", co.body.order.num);
      ok(w && Math.abs(w.balance - p7.price * 0.6) < 0.05, "and the member is refunded to their wallet", [o, w]);
      const g2 = await A("/api/admin/group-buys" + Q, "POST", { product_id: p7.id, group_price: +(p7.price * 0.7).toFixed(2), min_members: 2, max_members: 2, ends_at: new Date(Date.now() + 3600e3).toISOString() });
      for (const tag of ["grp2", "grp3"]) {
        const M = await shopper(tag);
        await M("/api/cart" + Q, "POST", { id: p7.id, terms: { group: { id: g2.body.group.id } } });
        const r = await checkout(M);
        ok(r.status === 200, tag + " joins the second group", r.body);
      }
      ok(db.get("SELECT status FROM group_campaigns WHERE id=?", g2.body.group.id).status === "succeeded", "a full group succeeds at once");
    }

    console.log("▸ SUBSTITUTIONS");
    {
      const S = await shopper("subs");
      const [a1, a2, a3] = db.all("SELECT id, price FROM products WHERE tenant_id=1 AND lifecycle='published' AND deleted_at IS NULL AND stock > 20 AND price > 40 ORDER BY id DESC LIMIT 3");
      const cheaper = db.get("SELECT id, price FROM products WHERE tenant_id=1 AND lifecycle='published' AND deleted_at IS NULL AND stock > 0 AND price < ? AND price > 1 ORDER BY price DESC LIMIT 1", a1.price);
      ok((await S("/api/cart" + Q, "POST", { id: a1.id, terms: { substitute: { policy: "specific" } } })).status === 400, "a named substitute must be named");
      await S("/api/cart" + Q, "POST", { id: a1.id, terms: { substitute: { policy: "best_match" } } });
      await S("/api/cart" + Q, "POST", { id: a2.id, terms: { substitute: { policy: "ask_me" } } });
      await S("/api/cart" + Q, "POST", { id: a3.id, terms: { substitute: { policy: "none" } } });
      const c = await cart(S);
      ok(c.items.every(i => /If unavailable/.test((i.term_labels || [])[0] || "")), "each line shows the shopper's choice");
      const co = await checkout(S);
      ok(co.status === 200, "the order is placed with each line's choice", co.body);
      const oid = db.get("SELECT id FROM orders WHERE num=?", co.body.order.num).id;
      const view = (await A(`/api/admin/substitutions/${oid}${Q}`)).body;
      ok(view.lines.length === 3 && view.lines.every(l => l.policy), "the picker sees every line's choice", view.lines);
      const w0 = (db.get("SELECT balance FROM wallets WHERE tenant_id=1 AND owner=(SELECT owner FROM orders WHERE id=?)", oid) || { balance: 0 }).balance;
      const s1 = await A(`/api/admin/substitutions/${oid}${Q}`, "POST", { product_id: a1.id, substitute_id: cheaper.id });
      ok(s1.status === 200 && s1.body.substitution.state.key === "applied" && s1.body.substitution.refund > 0, "best match is applied at once, refunding a cheaper substitute's difference", s1.body);
      const s2 = await A(`/api/admin/substitutions/${oid}${Q}`, "POST", { product_id: a2.id, substitute_id: cheaper.id });
      ok(s2.body.substitution.state.key === "proposed", "ask-me waits for the shopper");
      const mineS = (await S("/api/substitutions" + Q)).body.substitutions;
      ok(mineS.some(x => x.id === s2.body.substitution.id), "who sees the proposal");
      const rj = await S(`/api/substitutions/${s2.body.substitution.id}${Q}`, "POST", { action: "reject" });
      ok(rj.status === 200 && rj.body.substitution.state.key === "refunded", "rejecting refunds the line", rj.body);
      ok((await A(`/api/admin/substitutions/${oid}${Q}`, "POST", { product_id: a3.id, substitute_id: cheaper.id })).status === 409, "a line the shopper wants refunded cannot be substituted");
      const un = await A(`/api/admin/substitutions/${oid}${Q}`, "POST", { product_id: a3.id, unavailable: true });
      ok(un.status === 200 && un.body.substitution.state.key === "refunded", "it is refunded instead");
      const w1 = db.get("SELECT balance FROM wallets WHERE tenant_id=1 AND owner=(SELECT owner FROM orders WHERE id=?)", oid).balance;
      ok(Math.abs((w1 - w0) - (s1.body.substitution.refund + a2.price + a3.price)) < 0.05, "every refund reached the shopper's wallet", [w0, w1]);
    }

    console.log("▸ A PLATFORM KIND PER TYPE");
    {
      const kinds = (await P("/api/platform/kinds")).body;
      const keys = (kinds.kinds || []).map(k => k.key);
      for (const k of ["quick_commerce", "omnichannel_retail", "b2b_wholesale", "super_app", "resale", "auction_house", "services", "rentals", "food_delivery", "group_buying"])
        ok(keys.includes(k), "the " + k + " kind is served");
      const owner = n => ({ owner: { name: "Owner " + n, email: "owner@" + n + ".test", password: "Str0ng-" + n + "-pass" } });
      const t = await P("/api/platform/tenants", "POST", { name: "Second Hand Co", slug: "secondhand", country: "IN", mode: "resale", ...owner("secondhand") });
      ok(t.status === 200 && t.body.archetype === "blend_resale", "a resale platform launches from its blend", t.body.error || t.body.archetype);
      const comp = db.all("SELECT capability FROM capability_values WHERE tenant_id=? AND enabled=1", t.body.tenant.id).map(r => r.capability);
      ok(["peer_listings", "conversations", "price_negotiation", "auctions", "escrow"].every(k => comp.includes(k)), "with selling, messages, offers, auctions and escrow on", comp);
      const sv = await P("/api/platform/tenants", "POST", { name: "Cut & Style", slug: "cutstyle", country: "IN", mode: "services", ...owner("cutstyle") });
      ok(sv.status === 200 && sv.body.archetype === "blend_services", "a services platform launches with bookings", sv.body.error);
    }
  } catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
  srv.kill();
  console.log(`\n${passed} passed, ${failed} failed`);
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
