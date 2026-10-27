/* LUXORA Platform — money, exactly (PR-016).
   One representation: an amount is a whole number of MINOR units of one currency, and a
   currency's minor unit is data (its `decimals` in Value's master, lib/registry.js). Nothing
   here does binary floating-point arithmetic on money: a JS number coming in is read through
   its shortest decimal spelling (String(n): 1.005 is "1.005", not 1.00499999999999989…), held
   as a BigInt scaled by a power of ten, and rounded once, by a NAMED rule.

   The rule is configuration (lib/seed/money.json): a platform default and per-currency
   overrides. Which rule a market uses is the owner's decision; this module only guarantees
   that the same rule is applied the same way everywhere and that no amount is ever rounded
   by accident of representation. */
"use strict";
const POLICY = require("./seed/money.json");

/* rounding rules, applied to the digits beyond the target precision */
const MODES = new Set(["half-up", "half-even", "half-down", "up", "down", "ceiling", "floor"]);

const fail = m => Object.assign(new Error(m), { code: "money_invalid" });

/* any amount → { neg, int: BigInt, scale } with value = ±int / 10^scale, exactly as written */
function parse(x) {
  if (typeof x === "bigint") return { neg: x < 0n, int: x < 0n ? -x : x, scale: 0 };
  if (typeof x === "number" && !Number.isFinite(x)) throw fail("Not a finite amount: " + x);
  const s = typeof x === "number" ? String(x) : String(x == null ? "" : x).trim();
  const m = /^([+-])?(\d*)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/.exec(s);
  if (!m || (m[2] === "" && (m[3] || "") === "")) throw fail("Not an amount: " + x);
  const frac = m[3] || "";
  let int = BigInt((m[2] || "0") + frac);
  let scale = frac.length - Number(m[4] || 0);
  if (scale < 0) { int *= 10n ** BigInt(-scale); scale = 0; }
  return { neg: m[1] === "-" && int !== 0n, int, scale };
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

function modeFor(currency) {
  const c = currency ? String(currency).toUpperCase() : "";
  const m = (POLICY.currencies && POLICY.currencies[c] && POLICY.currencies[c].rounding) || POLICY.rounding;
  if (!MODES.has(m)) throw fail("Unknown rounding rule: " + m);
  return m;
}
function checkDecimals(d) {
  const n = Number(d);
  if (!Number.isInteger(n) || n < 0 || n > 18) throw fail("A currency's decimals are a whole number from 0 to 18, not " + d);
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
/* the same as a safe JS integer — what a column, a ledger or a gateway takes */
function toMinor(x, decimals, mode) {
  const v = toMinorBig(x, decimals, mode);
  const n = Number(v);
  if (!Number.isSafeInteger(n)) throw fail("Amount out of range: " + x);
  return n;
}
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
function allocate(totalMinor, weights) {
  const total = BigInt(totalMinor);
  const w = weights.map(x => toMinorBig(x, 12, "half-even"));
  if (!w.length || w.some(x => x < 0n)) throw fail("Weights are one or more non-negative numbers");
  const sum = w.reduce((a, b) => a + b, 0n);
  if (sum === 0n) throw fail("Weights may not all be zero");
  const neg = total < 0n, t = neg ? -total : total;
  const parts = w.map(x => (t * x) / sum);
  let left = t - parts.reduce((a, b) => a + b, 0n);
  const order = w.map((x, i) => ({ i, rem: (t * x) % sum })).sort((a, b) => (b.rem > a.rem ? 1 : b.rem < a.rem ? -1 : a.i - b.i));
  for (const o of order) { if (left === 0n) break; parts[o.i] += 1n; left -= 1n; }
  return parts.map(p => Number(neg ? -p : p));
}

/* the configured rule for a currency, applied — what the rest of the platform calls */
const roundIn = (x, decimals, currency) => round(x, decimals, modeFor(currency));
const toMinorIn = (x, decimals, currency) => toMinor(x, decimals, modeFor(currency));
const convertIn = (x, rate, decimals, currency) => convert(x, rate, decimals, modeFor(currency));

module.exports = { MODES, parse, toMinor, toMinorBig, fromMinor, format, round, convert, convertMinor, allocate, modeFor, roundIn, toMinorIn, convertIn };
