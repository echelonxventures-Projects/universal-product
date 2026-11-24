#!/usr/bin/env node
/* LUXORA Platform — is this install ready for real customers? Reads the install as it is and says
   what still stands in the way; changes nothing. Exit 1 while anything required is missing.

   node scripts/preflight.js            checks the install this environment points at
   (Platform admins see the same list at GET /api/platform/readiness.) */
"use strict";
const s = console.log; console.log = () => { };
const list = require("../lib/readiness.js").check();
console.log = s;
for (const c of list) console.log((c.ok ? "  ✓ " : c.required ? "  ✗ " : "  · ") + c.name + (c.ok || !c.fix ? "" : "\n      " + c.fix));
const left = list.filter(c => !c.ok && c.required).length;
console.log("\n" + (left ? left + " required item" + (left > 1 ? "s" : "") + " left" : "Ready"));
process.exit(left ? 1 : 0);
