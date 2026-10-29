/* LUXORA Platform — money is exact (lib/money.js, PR-016).
   The reproductions recorded in PRODUCTION_READINESS.md (1.005 → 1.00, 2.675 → 2.67, 10.235 →
   10.23) round by the configured rule; amounts reach a gateway in the currency's own minor unit
   (a three-decimal currency was sent at a tenth of its amount); a split never loses or invents a
   minor unit; and the shown-currency conversion multiplies exactly. Properties are checked over
   seeded random amounts, so a failure names an input that reproduces it. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "money-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const M = require("../lib/money.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message) || re.test(e.code || ""), n, e.message); } };
/* a small deterministic generator: the same seed gives the same inputs on every run */
let seed = 20261027;
const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;

console.log("money — the recorded reproductions round by the rule");
ok(M.round(1.005, 2, "half-up") === 1.01 && M.round(2.675, 2, "half-up") === 2.68 && M.round(10.235, 2, "half-up") === 10.24, "1.005 → 1.01, 2.675 → 2.68, 10.235 → 10.24 under half-up (toFixed gave 1.00, 2.67, 10.23)");
ok(M.round(2.675, 2, "half-even") === 2.68 && M.round(2.665, 2, "half-even") === 2.66 && M.round(-2.675, 2, "half-up") === -2.68, "half-even goes to the even digit; half-up is half away from zero for negatives");
ok(M.round(0.1 + 0.2, 2, "half-up") === 0.3 && M.round([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1].reduce((a, b) => a + b, 0), 2, "half-up") === 1, "float noise below the precision does not move an amount");
ok(M.round(1.239, 2, "down") === 1.23 && M.round(1.231, 2, "up") === 1.24 && M.round(-1.231, 2, "ceiling") === -1.23 && M.round(-1.231, 2, "floor") === -1.24 && M.round(1.235, 2, "half-down") === 1.23, "down, up, ceiling, floor and half-down each do what they name");
const lines = [0.335, 0.335, 0.335];
const perLine = lines.reduce((a, l) => a + M.toMinor(l, 2, "half-up"), 0), once = M.toMinor("1.005", 2, "half-up");
ok(perLine === 102 && once === 101, "per-line and once-per-document rounding differ by design (102 vs 101) — which one applies is the written policy, not chance");

console.log("\nmoney — parsing is exact or refused");
ok(M.toMinor("12.34", 2, "half-up") === 1234 && M.toMinor(1e-7, 2, "half-up") === 0 && M.toMinor(1.5e-2, 2, "half-up") === 2, "a number's exponent spelling (1e-7, 0.015) parses exactly");
ok(M.toMinor("1e3", 2, "half-up") === 100000 && M.toMinor("-0.005", 2, "half-up") === -1 && M.toMinor("-0.004", 2, "half-up") === 0, "1e3 is 1000; signs survive; a rounded-away negative is zero");
ok(Object.is(M.toMinor("-0.004", 2, "half-up"), 0), "never a negative zero");
throws(() => M.toMinor("12,34", 2, "half-up"), /Not an amount/, "a locale comma is not an amount");
throws(() => M.toMinor(NaN, 2, "half-up"), /finite/, "NaN is refused");
throws(() => M.toMinor("1", 2, "nearest"), /rounding rule/, "an unknown rule is refused");
throws(() => M.toMinor("1", 2.5, "half-up"), /decimals/, "fractional decimals are refused");
throws(() => M.toMinor("1e30", 2, "half-up"), /range/, "an amount beyond a safe integer is refused");
ok(M.format(12345, 3) === "12.345" && M.format(-5, 2) === "-0.05" && M.format(1500, 0) === "1500", "format gives the exact decimal string at the currency's decimals");

console.log("\nmoney — conversion multiplies exactly");
ok(M.convert(60.47, 1, 2, "half-up") === 60.47 && M.convert(100, 0.012345, 2, "half-up") === 1.23 && M.convert(1.005, 1, 2, "half-up") === 1.01, "amount × rate, rounded once");
ok(M.convert(39.3, 83.12, 0, "half-up") === 3267 && M.convert(-10, 1.5, 2, "half-up") === -15, "to a zero-decimal currency; negative amounts");

console.log("\nmoney — properties over seeded random amounts");
let bad = null;
for (let i = 0; i < 4000 && !bad; i++) {
  const d = [0, 2, 3][i % 3];
  const minor = Math.floor(rnd() * 1e9) - 5e8;
  const back = M.toMinor(M.fromMinor(minor, d), d, "half-even");
  if (back !== minor) bad = { minor, d, back };
}
ok(!bad, "minor → number → minor is the identity at 0, 2 and 3 decimals (4,000 values)", bad);
bad = null;
for (let i = 0; i < 2000 && !bad; i++) {
  const total = Math.floor(rnd() * 1e7) * (i % 7 ? 1 : -1);
  const n = 1 + Math.floor(rnd() * 9);
  const w = Array.from({ length: n }, () => Math.floor(rnd() * 1000) / 10);
  if (w.every(x => x === 0)) w[0] = 1;
  const parts = M.allocate(total, w);
  const sum = parts.reduce((a, b) => a + b, 0);
  const exact = w.map(x => total * x / w.reduce((a, b) => a + b, 0));
  if (sum !== total || parts.some((p, k) => Math.abs(p - exact[k]) >= 1 + 1e-6)) bad = { total, w, parts };
}
ok(!bad, "an allocation always sums to the total and no part is a whole minor unit off its share (2,000 splits)", bad);
ok(JSON.stringify(M.allocate(100, [1, 1, 1])) === "[34,33,33]" && JSON.stringify(M.allocate(-100, [1, 1, 1])) === "[-34,-33,-33]", "1.00 in three is 0.34 + 0.33 + 0.33, ties to the earlier part");
throws(() => M.allocate(100, [0, 0]), /zero/, "all-zero weights are refused");
bad = null;
for (let i = 0; i < 3000 && !bad; i++) {
  /* an exact three-decimal amount as a string; half-up to two is decided by its last digit alone */
  const thousandths = Math.floor(rnd() * 2e6) - 1e6, a = Math.abs(thousandths);
  const s = (thousandths < 0 ? "-" : "") + Math.floor(a / 1000) + "." + String(a % 1000).padStart(3, "0");
  const hundredths = Math.floor(a / 10) + (a % 10 >= 5 ? 1 : 0);
  const want = (thousandths < 0 && hundredths ? -1 : 1) * hundredths;
  if (M.toMinor(s, 2, "half-up") !== want || M.toMinor(Number(s), 2, "half-up") !== want) bad = { s, want, got: M.toMinor(s, 2, "half-up"), fromNumber: M.toMinor(Number(s), 2, "half-up") };
}
ok(!bad, "every three-decimal amount rounds half-up to two by its last digit, as a string and as a JS number (3,000 values)", bad);

console.log("\nmoney — the configured rule");
ok(M.MODES.has(M.modeFor()) && M.modeFor("XYZ") === M.modeFor(), "the platform default applies to a currency without an override", M.modeFor());

console.log("\nmoney — what a gateway is sent (lib/spec.js)");
const silence = console.log; console.log = () => { };
require("../lib/db.js");
console.log = silence;
const spec = require("../lib/spec.js");
ok(spec.minorUnits(12.345, "KWD") === 12345, "12.345 of a three-decimal currency is 12345 minor units (amount×100 sent 1235, a tenth)", spec.minorUnits(12.345, "KWD"));
ok(spec.minorUnits(1.005, "USD") === 101 && spec.minorUnits(12.34, "USD") === 1234 && spec.minorUnits(1500, "JPY") === 1500, "1.005 is 101 (was 100); 12.34 is 1234; ¥1,500 is 1500");
throws(() => spec.minorUnits(10, "QQQ"), /Unknown currency/, "a currency the master does not know is refused, not sent as ×100");
const ctx = spec.buildCtx({}, { amount: 12.345, currency: "KWD" });
ok(ctx.amountCents === 12345 && ctx.money === "12.345", "the spec tokens: {{amountCents}} 12345, {{money}} \"12.345\"", { c: ctx.amountCents, m: ctx.money });
const jp = spec.buildCtx({}, { amount: 1500, currency: "JPY" });
ok(jp.money === "1500" && jp.amountCents === 1500, "a zero-decimal currency's {{money}} has no decimal point");
const note = spec.buildCtx({}, { to: "x", subject: "y" });
ok(note.amountCents === undefined && note.money === undefined, "a call with no currency (a notification) has no payment tokens");

console.log("\nmoney — the platform's helpers use it");
const tax = require("../lib/tax.js");
ok(tax.computeLegacy({ perLine: false, taxRate: 0.25, goodsBase: 10.7, otherTaxable: 0, currency: "USD" }) === 2.68, "tax on 10.70 at 25% is 2.68 (toFixed gave 2.67)", tax.computeLegacy({ perLine: false, taxRate: 0.25, goodsBase: 10.7, otherTaxable: 0, currency: "USD" }));
ok(tax.computeLegacy({ perLine: true, taxRate: 0.1, lines: [{ unitBase: 3.35, qty: 1 }, { unitBase: 3.35, qty: 2 }], otherTaxable: 0, currency: "USD" }) === 1.01, "per-line tax sums before it rounds once (3 × 0.335 → 1.01)");

console.log("\nmoney — tax is rounded at its currency's own scale");
const TX = require("../lib/tax.js");
ok(M.toString(TX.computeExact({ perLine: false, taxRate: "0.08", goods: M.of("1234", "JPY"), other: M.zero("JPY"), currency: "JPY" })) === "99", "8 % of ¥1,234 is ¥99 (98.72 rounded at zero decimals — a fixed two decimals gave 98.72)");
ok(M.toString(TX.computeExact({ perLine: false, taxRate: "0.05", goods: M.of("12.345", "KWD"), other: M.zero("KWD"), currency: "KWD" })) === "0.617", "5 % of 12.345 KWD is 0.617 (three decimals)");
ok(M.toString(TX.computeExact({ perLine: true, taxRate: "0.1", currency: "USD", goods: M.of("10.05", "USD"), other: M.of("-5", "USD"), lines: [{ amount: M.of("3.35", "USD") }, { amount: M.of("6.70", "USD"), rate: "0" }] })) === "0.34", "per line, each line's own rate, unrounded until the document; negative other taxable taxes nothing");
const iq = TX.quote({ tenantId: 0, country: "XX", currency: "KWD", lines: [{ id: "a", amount: "1.005", tax_rule: { rate: 0.05 } }] });
ok(iq.currency === "KWD" && iq.lines[0].amount === 1.005 && iq.tax === 0.05, "a quote is in its currency: 1.005 KWD stays 1.005 and its 5 % tax is 0.050", iq);
const inc = TX.quote({ tenantId: 0, country: "XX", currency: "USD", inclusive: true, lines: [{ id: "a", amount: "118.00", tax_rule: { rate: 0.18 } }] });
ok(inc.lines[0].net === 100 && inc.lines[0].tax === 18, "an inclusive line splits exactly: 118.00 at 18 % is 100.00 net + 18.00 tax", inc.lines[0]);

console.log("\nmoney — the Money contract: an amount is exact minor units of one currency");
const USD = M.of("12.34", "USD"), KWD = M.of("12.345", "KWD"), JPY = M.of(1500, "JPY");
ok(USD.minor === 1234n && USD.scale === 2 && KWD.minor === 12345n && KWD.scale === 3 && JPY.minor === 1500n && JPY.scale === 0, "two-, three- and zero-decimal currencies take their scale from the currency master");
throws(() => M.of("12.345", "USD"), /At most 2 decimal/, "an amount with more decimals than its currency is refused, not rounded");
throws(() => M.of("1.5", "JPY"), /At most 0 decimal/, "a zero-decimal currency refuses a fraction");
ok(M.toString(M.rounded("12.345", "USD")) === "12.35" && M.toString(M.rounded("-12.345", "USD")) === "-12.35", "rounded() rounds once by the currency's named rule (half away from zero)");
throws(() => M.of("1", "QQQ"), /Unknown currency/, "a currency the master does not know has no scale: refused, never assumed to have 2");
throws(() => M.of("1", ""), /needs its currency/, "an amount without a currency is refused — no geographic or platform default is inferred");
throws(() => M.add(USD, M.of("1", "EUR")), /convert explicitly/, "two currencies are never added");
throws(() => M.add(USD, M.ofMinor(1000, "USD", 3)), /decimals/, "one currency at two scales is never added");
throws(() => M.add(USD, 5), /Not a money amount/, "a bare number is not money");
ok(M.toString(M.sub(M.of("0.10", "USD"), M.of("0.30", "USD"))) === "-0.20" && M.toString(M.neg(USD)) === "-12.34", "subtraction and negatives are exact");
ok(M.toString(M.sum(Array(10).fill(M.of("0.10", "USD")), "USD")) === "1.00", "ten lines of 0.10 sum to exactly 1.00 (floats give 0.9999999999999999)");
ok(M.toString(M.sum([], "KWD")) === "0.000", "an empty sum is that currency's zero, at its scale");
ok(M.toString(M.mulQty(USD, 3)) === "37.02" && M.toString(M.mulQty(M.of("0.99", "USD"), "2.5")) === "2.48", "a whole quantity multiplies exactly; a fractional one (2.5) rounds once");
throws(() => M.mulQty(USD, -1), /not negative/, "a negative quantity is refused");
ok(M.toString(M.pct(M.of("10.70", "USD"), 25)) === "2.68" && M.toString(M.pct(M.of("100", "KWD"), "2.5")) === "2.500", "a percentage is exact, rounded once at the currency's scale");
ok(M.toString(M.mulRate(M.of("10.70", "USD"), "0.25")) === "2.68", "a fractional rate is the same multiplication");
ok(M.toString(M.divRate(M.of("118.00", "USD"), "1.18")) === "100.00" && M.toString(M.divRate(M.of("10", "USD"), 3)) === "3.33", "division by a factor is exact, rounded once (an inclusive tax's net)");
throws(() => M.divRate(USD, 0), /positive/, "division by zero is refused");
ok(M.split(M.of("1.00", "USD"), 3).map(M.toString).join(" ") === "0.34 0.33 0.33" && M.toString(M.sum(M.split(M.of("1.00", "USD"), 3), "USD")) === "1.00", "a split's parts sum exactly to the amount");
ok(M.toString(M.convertTo(M.of("39.30", "USD"), "83.12", "JPY")) === "3267" && M.convertTo(M.of("39.30", "USD"), "83.12", "JPY").currency === "JPY", "conversion is the only way an amount changes currency, rounded once by the target's rule");
ok(M.toString(M.convertTo(M.of("1.000", "KWD"), "3.2614", "USD")) === "3.26" && M.toString(M.convertTo(M.of("100", "JPY"), "0.0067", "KWD")) === "0.670", "conversion between zero-, two- and three-decimal currencies");
throws(() => M.convertTo(USD, 0, "EUR"), /positive/, "a zero or negative exchange rate is refused");
ok(M.cmp(M.of("1.00", "USD"), M.of("0.99", "USD")) === 1 && M.eq(M.of("1", "USD"), M.of("1.00", "USD")) && M.toString(M.min(USD, M.of("1", "USD"))) === "1.00", "comparison is on minor units");
const big = M.ofMinor("123456789012345678901234567890", "USD", 2);
ok(M.toString(M.add(big, big)) === "2469135780246913578024691357.80", "arithmetic is unbounded (BigInt)");
throws(() => M.minorOf(big), /out of range/, "an amount beyond 2^53 − 1 minor units cannot be stored or projected — refused, never silently lost");
throws(() => M.ofMinor(2 ** 53, "USD"), /safe whole number/, "an unsafe number of minor units is refused");
throws(() => M.ofMinor("12.5", "USD"), /whole number/, "minor units are whole");

console.log("\nmoney — serialization is versioned and exact");
const ser = M.toJSON(KWD);
ok(JSON.stringify(ser) === '{"v":1,"amount":"12.345","currency":"KWD","minor":"12345","scale":3,"rounding":"half-up"}', "toJSON: strings for the amount and minor units, the currency, scale and rounding rule", ser);
ok(M.eq(M.fromJSON(JSON.parse(JSON.stringify(ser))), KWD), "a serialized amount reads back to the same exact amount");
throws(() => M.fromJSON({ ...ser, amount: "12.346" }), /disagree/, "a serialized amount whose minor and amount disagree is refused");
throws(() => M.fromJSON({ ...ser, v: 2 }), /version/, "an unknown serialization version is refused");
throws(() => JSON.stringify({ a: KWD }), /BigInt/, "a Money value cannot be JSON-serialized by accident (no silent fallback to a float)");

console.log("\nmoney — a JS number is read by its decimal spelling, at most 15 significant digits");
ok(M.numberText(0.1 + 0.2) === "0.3" && M.numberText(1.005) === "1.005" && M.numberText(12345678901234.5) === "12345678901234.5", "binary noise beyond 15 digits is read away; real digits are kept");
ok(M.toString(M.rounded(1.0049999999999999, "USD")) === "1.01", "a sum that lands a hair below a half (1.0049999999999999) rounds as the decimal it represents");

console.log("\nmoney — against an independent reference (Python decimal, test/fixtures/money-vectors.json)");
const V = require("./fixtures/money-vectors.json");
/* a currency of each scale in the master, its rule set through the governed money policy
   (lib/money-policy.js): one approved, published change per rule, the vectors of each rule run
   under it */
const curOf = { 0: "JPY", 2: "USD", 3: "KWD" };
const MP = require("../lib/money-policy.js"), POL = require("../lib/seed/money.json");
const APPROVE = [require("../lib/kernel.js").SEED.lifecycle.approvePermission];
const governed = currencies => { const c = MP.propose({ title: "money vectors", policy: { rounding: POL.rounding, currencies } }, "test.author"); MP.approve(c.id, "test.approver", APPROVE); return MP.publish(c.id, "test.approver").policy; };
let inForce = null;
const withMode = (code, mode, fn) => { if (inForce !== mode) { governed(Object.fromEntries(Object.values(curOf).map(k => [k, { rounding: mode }]))); inForce = mode; } return fn(); };
const byMode = list => [...list].sort((a, b) => (a.mode < b.mode ? -1 : a.mode > b.mode ? 1 : 0));
const check = (name, list, fn) => { let bad = null, n = 0; for (const v of byMode(list)) { n++; let got; try { got = fn(v); } catch (e) { got = "threw " + e.message; } if (got !== v.want) { bad = { v, got }; break; } } ok(!bad, name + " (" + n + " vectors)", bad); };
check("conversion amount × rate at the target's scale, every rule", V.convert, v => withMode(curOf[v.toScale], v.mode, () => M.convertTo(M.ofMinor(v.minor, curOf[v.scale], v.scale), v.rate, curOf[v.toScale]).minor.toString()));
check("percentages, every rule", V.pct, v => withMode(curOf[v.scale], v.mode, () => M.pct(M.ofMinor(v.minor, curOf[v.scale], v.scale), v.pct).minor.toString()));
check("fractional quantities, every rule", V.qty, v => withMode(curOf[v.scale], v.mode, () => M.mulQty(M.ofMinor(v.minor, curOf[v.scale], v.scale), v.qty).minor.toString()));
check("division by a factor, every rule", V.div, v => withMode(curOf[v.scale], v.mode, () => M.divRate(M.ofMinor(v.minor, curOf[v.scale], v.scale), v.div).minor.toString()));
check("rounding a decimal to a scale, every rule", V.round, v => withMode(curOf[v.scale], v.mode, () => M.rounded(v.amount, curOf[v.scale]).minor.toString()));
governed(POL.currencies || {});
ok(M.modeFor("USD") === POL.rounding, "the policy is back to its configured rule after the vectors");

console.log("\nmoney — properties of the Money operations (seeded)");
bad = null;
for (let i = 0; i < 3000 && !bad; i++) {
  const code = ["JPY", "USD", "KWD"][i % 3];
  const a = M.ofMinor(Math.floor(rnd() * 2e9) - 1e9, code), b = M.ofMinor(Math.floor(rnd() * 2e9) - 1e9, code);
  const n = 1 + Math.floor(rnd() * 7), parts = M.split(a, n);
  if (!M.eq(M.sub(M.add(a, b), b), a) || !M.eq(M.sum(parts, code), a) || parts.some(p => (p.minor - parts[0].minor) > 1n || (parts[0].minor - p.minor) > 1n) || !M.eq(M.fromJSON(M.toJSON(a)), a) || M.toNumber(a) !== Number(M.toString(a))) bad = { a: M.toString(a), b: M.toString(b), n };
}
ok(!bad, "(a + b) − b = a; a split sums to a with parts a minor unit apart; serialize → parse = a; the projection is the exact decimal (3,000 values)", bad);

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
