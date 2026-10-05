#!/usr/bin/env node
'use strict';
const fs = require('fs');

const files = [
  '_registry/content-core.json',
  '_registry/content-ext.json',
  '_registry/content-commerce.json',
  '_registry/content-twin-agent.json',
  '_registry/content-runtime-data.json',
  '_registry/content-sec-ops-dep-qlt.json'
];

for (const f of files) {
  const j = JSON.parse(fs.readFileSync(f, 'utf8'));
  let added = 0;
  for (const [key, c] of Object.entries(j.content)) {
    if (c.blueprint) continue;
    const tax = (c.taxonomy || '').split('.')[0].toLowerCase();
    const cmds = (c.commands || []).slice(0, 3).join(', ');
    c.blueprint = [
      'Build order for ' + key + ':',
      '(1) define registry entries — this domain owns ' + tax + ' as registry truth, not code;',
      '(2) implement the contract surface first (' + cmds + ') and validate against ' + key + ' boundaries;',
      '(3) event-source all state so history is reconstructable;',
      '(4) wire the enforcement points — authority check, policy guard, evidence binding, trace — in-line, with no bypass path;',
      '(5) add tests per the Testing Architecture, citing evidence per gate;',
      '(6) obtain Verification and Certification before activation.',
      'Acceptance: the Zero Partial and Law 001 audits pass, every action answers the seven explainability questions, and this domain mutates no other domain internals.'
    ].join(' ');
    added++;
  }
  fs.writeFileSync(f, JSON.stringify(j, null, 2) + '\n');
  console.log(f, '→ added blueprint to', added, 'entries');
}
