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
ok(tax.computeLegacy({ perLine: false, taxRate: 0.25, goodsBase: 10.7, otherTaxable: 0 }) === 2.68, "tax on 10.70 at 25% is 2.68 (toFixed gave 2.67)", tax.computeLegacy({ perLine: false, taxRate: 0.25, goodsBase: 10.7, otherTaxable: 0 }));
ok(tax.computeLegacy({ perLine: true, taxRate: 0.1, lines: [{ unitBase: 3.35, qty: 1 }, { unitBase: 3.35, qty: 2 }], otherTaxable: 0 }) === 1.01, "per-line tax sums before it rounds once (3 × 0.335 → 1.01)");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
