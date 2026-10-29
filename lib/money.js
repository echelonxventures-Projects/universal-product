/* LUXORA Platform — money, exactly (PR-016).
   One representation: an amount is a whole number of MINOR units of one currency, and a
   currency's minor unit is data (its `decimals` in Value's master, lib/registry.js). Nothing
   here does binary floating-point arithmetic on money: a JS number coming in is read through
   its decimal spelling (see `parse`), held as a BigInt scaled by a power of ten, and rounded
   once, by a NAMED rule.

   The rule is governed configuration (lib/money-policy.js): a platform rule and per-currency
   rules, versioned on the kernel and changed only through its approval lifecycle, seeded from
   lib/seed/money.json. Which rule a market uses is the owner's decision; this module only
   guarantees that the rule in force is applied the same way everywhere and that no amount is
   ever rounded by accident of representation.

   The contract (docs/money.md is its written form):
     MONEY      { minor: BigInt, currency: "KWD", scale: 3 } — frozen; made only by `of`,
                `rounded`, `ofMinor`; scale is the currency's decimals from the master when the
                amount was made (a stored row keeps the scale it was written at)
     RATE       an exchange rate, tax rate or any factor: a decimal read exactly, never money
     PERCENT    a rate × 100 (commission 5 = 5 %), read exactly
     QUANTITY   a count or measure; a whole quantity multiplies exactly, a fractional one rounds
                once at the money's scale
     ROUNDING   once per operation that can leave the scale (a rate, a fractional quantity, a
                conversion), by the currency's named rule; sums, differences and whole
                quantities never round
     SERIAL     { v: 1, amount: "12.340", currency: "KWD", minor: "12340", scale: 3,
                rounding: "half-up" } — strings, so no reader turns an amount into a float
     RANGE      arithmetic is unbounded (BigInt); a stored or projected amount must be a safe
                integer of minor units (|minor| ≤ 2^53 − 1), anything larger is refused */
"use strict";

/* rounding rules, applied to the digits beyond the target precision */
const MODES = new Set(["half-up", "half-even", "half-down", "up", "down", "ceiling", "floor"]);
const SERIAL_VERSION = 1;
/* a double carries 15 significant decimal digits reliably (DBL_DIG); see `numberText` */
const NUMBER_DIGITS = 15;

const fail = (m, code, status) => Object.assign(new Error(m), { code: code || "money_invalid", status: status || 400 });

const sigDigits = s => s.replace(/^[+-]/, "").replace(/[eE].*$/, "").replace(".", "").replace(/^0+/, "").length;
/* a JS number's decimal value. Its shortest spelling (String) is exact for any number written
   with up to 15 significant digits (1.005 is "1.005", not 1.00499999999999989…). A spelling
   longer than that is the residue of binary arithmetic upstream (0.1 + 0.2 is
   0.30000000000000004): it is read at 15 significant digits, the precision a double
   guarantees. An amount that truly needs more digits is passed as a string or a BigInt. */
function numberText(n) {
  const s = String(n);
  return sigDigits(s) <= NUMBER_DIGITS ? s : String(Number(n.toPrecision(NUMBER_DIGITS)));
}

/* any amount → { neg, int: BigInt, scale } with value = ±int / 10^scale, exactly as written */
function parse(x) {
  if (typeof x === "bigint") return { neg: x < 0n, int: x < 0n ? -x : x, scale: 0 };
  if (typeof x === "number" && !Number.isFinite(x)) throw fail("Not a finite amount: " + x);
  const s = typeof x === "number" ? numberText(x) : String(x == null ? "" : x).trim();
  const m = /^([+-])?(\d*)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/.exec(s);
  if (!m || (m[2] === "" && (m[3] || "") === "")) throw fail("Not an amount: " + x);
  const frac = m[3] || "";
  let int = BigInt((m[2] || "0") + frac);
  let scale = frac.length - Number(m[4] || 0);
  if (scale < 0) { int *= 10n ** BigInt(-scale); scale = 0; }
  return { neg: m[1] === "-" && int !== 0n, int, scale };
}
/* the same value with trailing zero digits dropped: how many decimals it really has */
function normalize(p) {
  let { int, scale } = p;
  while (scale > 0 && int % 10n === 0n) { int /= 10n; scale--; }
  return { neg: p.neg && int !== 0n, int, scale };
}

/* integer division of a non-negative n by d under a rule; neg is the sign of the whole value */
function divRound(n, d, neg, mode) {
  const q = n / d, r = n % d;
  if (r === 0n) return q;
  const twice = r * 2n;
  const away = mode === "up" ? true
    : mode === "down" ? false
    : mode === "ceiling" ? !neg
    : mode === "floor" ? neg
    : twice > d ? true
    : twice < d ? false
    : mode === "half-up" ? true
    : mode === "half-down" ? false
    : (q % 2n) === 1n; /* half-even */
  return away ? q + 1n : q;
}

/* the rule the money policy in force names for a currency (its own, else the platform's) */
function modeFor(currency) {
  const m = require("./money-policy.js").ruleFor(currency);
  if (!MODES.has(m)) throw fail("Unknown rounding rule: " + m);
  return m;
}
function checkDecimals(d) {
  const n = Number(d);
  if (d === null || d === "" || !Number.isInteger(n) || n < 0 || n > 18) throw fail("A currency's decimals are a whole number from 0 to 18, not " + d);
  return n;
}
function checkMode(mode) { if (!MODES.has(mode)) throw fail("Unknown rounding rule: " + mode); return mode; }

/* amount → minor units (BigInt) at `decimals`, rounded once by `mode` */
function toMinorBig(x, decimals, mode) {
  const d = checkDecimals(decimals); checkMode(mode);
  const p = parse(x);
  const shift = d - p.scale;
  const mag = shift >= 0 ? p.int * 10n ** BigInt(shift) : divRound(p.int, 10n ** BigInt(-shift), p.neg, mode);
  return p.neg ? -mag : mag;
}
const MAX_MINOR = BigInt(Number.MAX_SAFE_INTEGER);
function safe(v, what) {
  if (v > MAX_MINOR || v < -MAX_MINOR) throw fail("Amount out of range: " + what, "money_range");
  return Number(v);
}
/* the same as a safe JS integer — what a column, a ledger or a gateway takes */
function toMinor(x, decimals, mode) { return safe(toMinorBig(x, decimals, mode), x); }
/* minor units → "12.340" at 3 decimals: the exact decimal string a gateway or a receipt shows */
function format(minor, decimals) {
  const d = checkDecimals(decimals);
  const v = BigInt(minor), neg = v < 0n, a = neg ? -v : v;
  const base = 10n ** BigInt(d);
  return (neg ? "-" : "") + (a / base).toString() + (d ? "." + (a % base).toString().padStart(d, "0") : "");
}
/* minor units → the nearest JS number; its shortest spelling is exactly the decimal amount */
const fromMinor = (minor, decimals) => Number(format(minor, decimals));
/* round an amount to `decimals` by `mode` and give it back as a number */
const round = (x, decimals, mode) => fromMinor(toMinorBig(x, decimals, mode), decimals);

/* amount × rate (an FX rate or any factor), multiplied exactly, rounded once */
function convertMinor(x, rate, decimals, mode) {
  const a = parse(x), r = parse(rate);
  const neg = a.neg !== r.neg && a.int !== 0n && r.int !== 0n;
  const prod = (neg ? "-" : "") + a.int * r.int + "e-" + (a.scale + r.scale);
  return toMinor(prod, decimals, mode);
}
const convert = (x, rate, decimals, mode) => fromMinor(convertMinor(x, rate, decimals, mode), decimals);

/* split a whole minor amount across weights so the parts sum to it exactly (largest remainder;
   ties go to the earlier part) — for refunds, settlements and per-line allocation */
function allocateBig(total, weights) {
  const w = weights.map(x => toMinorBig(x, 12, "half-even"));
  if (!w.length || w.some(x => x < 0n)) throw fail("Weights are one or more non-negative numbers");
  const sum = w.reduce((a, b) => a + b, 0n);
  if (sum === 0n) throw fail("Weights may not all be zero");
  const neg = total < 0n, t = neg ? -total : total;
  const parts = w.map(x => (t * x) / sum);
  let left = t - parts.reduce((a, b) => a + b, 0n);
  const order = w.map((x, i) => ({ i, rem: (t * x) % sum })).sort((a, b) => (b.rem > a.rem ? 1 : b.rem < a.rem ? -1 : a.i - b.i));
  for (const o of order) { if (left === 0n) break; parts[o.i] += 1n; left -= 1n; }
  return parts.map(p => (neg ? -p : p));
}
const allocate = (totalMinor, weights) => allocateBig(BigInt(totalMinor), weights).map(p => safe(p, totalMinor));

/* the configured rule for a currency, applied — what the rest of the platform calls */
const roundIn = (x, decimals, currency) => round(x, decimals, modeFor(currency));
const toMinorIn = (x, decimals, currency) => toMinor(x, decimals, modeFor(currency));
const convertIn = (x, rate, decimals, currency) => convert(x, rate, decimals, modeFor(currency));

/* ============================== currencies ============================== */
/* a currency's precision is canonical data: its decimals in Value's master. A currency the
   master does not know has no defined minor unit, so it is refused — never assumed to have 2 */
/* read from the master, kept only until the next write through lib/db.js (its write counter),
   so an edited currency is never served stale */
let seen = { writes: -1, rows: new Map() };
function masterRow(c) {
  const D = require("./db.js"), w = typeof D.writes === "function" ? D.writes() : -2;
  if (w !== seen.writes || w === -2) seen = { writes: w, rows: new Map() };
  if (!seen.rows.has(c)) seen.rows.set(c, require("./registry.js").currency(c) || null);
  return seen.rows.get(c);
}
function currencyOf(code) {
  const c = code ? String(code).trim().toUpperCase() : "";
  if (!c) throw fail("An amount needs its currency", "currency_missing");
  const row = masterRow(c);
  if (!row || row.decimals == null || row.decimals === "") throw fail("Unknown currency: " + c, "currency_unknown");
  return { code: row.code, decimals: checkDecimals(row.decimals) };
}
const decimalsOf = code => currencyOf(code).decimals;

/* ============================== the Money value ============================== */
function make(minor, currency, scale) {
  if (typeof minor !== "bigint") throw fail("Money is made from a BigInt of minor units");
  return Object.freeze({ minor: minor === 0n ? 0n : minor, currency, scale });
}
const isMoney = x => !!x && typeof x === "object" && typeof x.minor === "bigint" && typeof x.currency === "string" && Number.isInteger(x.scale);
/* two amounts combine only in one currency at one scale: never silently across currencies */
function same(a, b) {
  if (!isMoney(a)) throw fail("Not a money amount: " + a);
  if (!isMoney(b)) throw fail("Not a money amount: " + b);
  if (a.currency !== b.currency) throw fail(`Cannot combine ${a.currency} with ${b.currency} — convert explicitly`, "currency_mismatch");
  if (a.scale !== b.scale) throw fail(`Cannot combine ${a.currency} at ${a.scale} and ${b.scale} decimals`, "scale_mismatch");
}
function expect(a, currency) {
  const c = currencyOf(currency);
  if (a.currency !== c.code) throw fail(`Expected ${c.code}, got ${a.currency}`, "currency_mismatch");
  return a;
}
/* an amount that must already be exact at the currency's scale: more decimals are refused */
function of(amount, currency) {
  if (isMoney(amount)) return expect(amount, currency);
  const c = currencyOf(currency);
  const p = normalize(parse(amount));
  if (p.scale > c.decimals) throw fail(`At most ${c.decimals} decimal place${c.decimals === 1 ? "" : "s"} for ${c.code}: ${amount}`, "money_precision");
  return make(toMinorBig(amount, c.decimals, "down"), c.code, c.decimals);
}
/* an amount rounded once, by the currency's rule, to its scale */
function rounded(amount, currency) {
  if (isMoney(amount)) return expect(amount, currency);
  const c = currencyOf(currency);
  return make(toMinorBig(amount, c.decimals, modeFor(c.code)), c.code, c.decimals);
}
/* minor units as stored: the row's own scale when it has one, else the master's */
function ofMinor(minor, currency, scale) {
  if (minor == null || minor === "") throw fail("No minor amount", "money_missing");
  const c = String(currency || "").trim().toUpperCase();
  if (!c) throw fail("An amount needs its currency", "currency_missing");
  const s = scale == null || scale === "" ? currencyOf(c).decimals : checkDecimals(scale);
  let v;
  if (typeof minor === "bigint") v = minor;
  else if (typeof minor === "number") { if (!Number.isSafeInteger(minor)) throw fail("Minor units are a safe whole number: " + minor, "money_range"); v = BigInt(minor); }
  else if (/^-?\d+$/.test(String(minor))) v = BigInt(String(minor));
  else throw fail("Minor units are a whole number: " + minor);
  return make(v, c, s);
}
const zero = currency => { const c = currencyOf(currency); return make(0n, c.code, c.decimals); };

function add(a, ...more) { let m = a.minor; for (const b of more) { same(a, b); m += b.minor; } return make(m, a.currency, a.scale); }
function sub(a, b) { same(a, b); return make(a.minor - b.minor, a.currency, a.scale); }
const neg = a => make(-a.minor, a.currency, a.scale);
/* the sum of amounts that must all be in `currency`; none sums to that currency's zero */
function sum(list, currency) { const z = zero(currency); return list.length ? add(expect(list[0], currency), ...list.slice(1)) : z; }
/* × a factor (a rate, a fraction, a fractional quantity), multiplied exactly, rounded once */
function mulRate(a, rate) {
  if (!isMoney(a)) throw fail("Not a money amount: " + a);
  const r = parse(rate);
  const v = (a.minor < 0n ? -a.minor : a.minor) * r.int;
  const negative = (a.minor < 0n) !== r.neg && v !== 0n;
  const q = divRound(v, 10n ** BigInt(r.scale), negative, modeFor(a.currency));
  return make(negative ? -q : q, a.currency, a.scale);
}
/* the exact product of two decimals (a unit price × a quantity, an amount × a rate), as a
   decimal string — nothing rounded; `rounded` then rounds it once where the policy says */
function times(a, b) {
  const x = parse(a), y = parse(b);
  const v = x.int * y.int;
  return (x.neg !== y.neg && v !== 0n ? "-" : "") + v + "e-" + (x.scale + y.scale);
}
/* ÷ a positive factor (an inclusive tax's 1 + rate, a unit count), divided exactly, rounded once */
function divRate(a, divisor) {
  if (!isMoney(a)) throw fail("Not a money amount: " + a);
  const d = parse(divisor);
  if (d.neg || d.int === 0n) throw fail("Divide by a positive amount, not " + divisor);
  const negative = a.minor < 0n, mag = negative ? -a.minor : a.minor;
  const q = divRound(mag * 10n ** BigInt(d.scale), d.int, negative, modeFor(a.currency));
  return make(negative ? -q : q, a.currency, a.scale);
}
/* the exact sum of decimals, as a decimal string (1 + a tax rate) */
function plus(...xs) {
  const ps = xs.map(parse); const sc = Math.max(0, ...ps.map(p => p.scale));
  let n = 0n; for (const p of ps) n += (p.neg ? -1n : 1n) * p.int * 10n ** BigInt(sc - p.scale);
  return (n < 0n ? "-" + -n : "" + n) + "e-" + sc;
}
/* × a quantity: a whole quantity is exact; a fractional one (2.5 kg) rounds once */
function mulQty(a, qty) {
  const q = parse(qty);
  if (q.neg) throw fail("A quantity is not negative: " + qty, "quantity_invalid");
  return mulRate(a, qty);
}
/* × a percentage (5 = 5 %) */
function pct(a, percent) { const p = parse(percent); return mulRate(a, (p.neg ? "-" : "") + p.int + "e-" + (p.scale + 2)); }
/* ÷ into n parts that sum exactly to the amount */
function split(a, n) { const k = Number(n); if (!Number.isInteger(k) || k < 1) throw fail("Split into a whole number of parts"); return allocateBig(a.minor, Array(k).fill(1)).map(p => make(p, a.currency, a.scale)); }
/* in proportion to weights, summing exactly to the amount */
const allocateMoney = (a, weights) => allocateBig(a.minor, weights).map(p => make(p, a.currency, a.scale));
/* into another currency at an explicit rate (target per source unit), rounded once by the
   target currency's rule — the only way an amount changes currency */
function convertTo(a, rate, toCurrency) {
  if (!isMoney(a)) throw fail("Not a money amount: " + a);
  const r = parse(rate);
  if (r.neg || r.int === 0n) throw fail("An exchange rate is positive: " + rate, "rate_invalid");
  const c = currencyOf(toCurrency);
  const negative = a.minor < 0n, mag = negative ? -a.minor : a.minor;
  /* value = mag/10^a.scale × r.int/10^r.scale, expressed at c.decimals */
  const num = mag * r.int * 10n ** BigInt(c.decimals), den = 10n ** BigInt(a.scale + r.scale);
  const q = divRound(num, den, negative, modeFor(c.code));
  return make(negative ? -q : q, c.code, c.decimals);
}
function cmp(a, b) { same(a, b); return a.minor < b.minor ? -1 : a.minor > b.minor ? 1 : 0; }
const eq = (a, b) => cmp(a, b) === 0;
const isZero = a => a.minor === 0n;
const isNegative = a => a.minor < 0n;
const min = (a, b) => (cmp(a, b) <= 0 ? a : b);
const max = (a, b) => (cmp(a, b) >= 0 ? a : b);
/* outward forms: the exact decimal string, a safe integer of minor units, and the JS number
   whose shortest spelling is that decimal — a projection for display and legacy readers,
   never something to compute with */
const toString = a => format(a.minor, a.scale);
const minorOf = a => safe(a.minor, toString(a));
const toNumber = a => { minorOf(a); return fromMinor(a.minor, a.scale); };
function toJSON(a) {
  return { v: SERIAL_VERSION, amount: toString(a), currency: a.currency, minor: a.minor.toString(), scale: a.scale, rounding: modeFor(a.currency) };
}
/* a serialized amount back: its minor, amount and scale must agree, and the version be known */
function fromJSON(o) {
  if (!o || typeof o !== "object") throw fail("Not a serialized amount");
  if (o.v !== SERIAL_VERSION) throw fail("Unknown money serialization version: " + o.v, "money_version");
  if (!/^-?\d+$/.test(String(o.minor))) throw fail("A serialized amount's minor is a whole number");
  const m = ofMinor(String(o.minor), o.currency, o.scale);
  if (o.amount != null && toString(m) !== String(o.amount)) throw fail("A serialized amount's minor and amount disagree", "money_inconsistent");
  return m;
}

module.exports = {
  MODES, SERIAL_VERSION, NUMBER_DIGITS, parse, normalize, numberText, toMinor, toMinorBig, fromMinor, format, round, convert, convertMinor, allocate, modeFor, roundIn, toMinorIn, convertIn,
  currencyOf, decimalsOf, isMoney, of, rounded, times, plus, divRate, ofMinor, zero, add, sub, neg, sum, mulRate, mulQty, pct, split, allocateMoney, convertTo,
  cmp, eq, isZero, isNegative, min, max, toString, minorOf, toNumber, toJSON, fromJSON
};
