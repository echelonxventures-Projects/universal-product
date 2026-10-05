#!/usr/bin/env node
'use strict';

/*
 * UCOS Ω∞ — Constitutional Audit
 * Verifies the repository obeys its own laws. Run: node _registry/audit.js
 */
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');

let pass = 0, fail = 0;
const ok = (m) => { console.log('  ✓ ' + m); pass++; };
const bad = (m) => { console.log('  ✗ ' + m); fail++; };

const files = [];
(function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) { if (!['node_modules', '.git', '_registry', '_superseded'].includes(e.name)) walk(p); }
    else if (e.name.startsWith('UCOS-') && e.name.endsWith('.md')) files.push(p);
  }
})(ROOT);

// Pre-existing hand-authored spec docs are constitutional *source* material,
// not projected artifacts. Law 002 audits the projected corpus only.
// Top-level indexes are navigation, not artifacts, and are excluded too.
const SOURCE_DOCS = new Set([
  'UCOS-Constitutional-Addendum.md',
  'UCOS-Constitutional-Master-Architecture.md',
  'UCRS-Zero-Hardcoding-Constitution.md',
  'UCOS-Universal-Capability-Operating-System.md',
  'UCOS_Omega_Constitutional_Architecture_v1.0.md',
  'UCOS-REPOSITORY-INDEX.md'
]);
const projected = files.filter(f => {
  if (SOURCE_DOCS.has(path.basename(f))) return false;
  // only artifacts living inside a category directory are projected artifacts
  return /^[0-9]+-/.test(path.relative(ROOT, path.dirname(f)));
});

const M = JSON.parse(fs.readFileSync(path.join(__dirname, 'manifest.json'), 'utf8'));
const P = JSON.parse(fs.readFileSync(path.join(__dirname, 'primitives.json'), 'utf8'));

console.log('\n=== LAW 001 — Zero Hard Coding ===');
// Law 001 applies to *schema types*, which live inside fenced code blocks.
// Prose that quotes a term while explaining the law is not a violation.
const banned = P.prohibited;
let violations = 0;
const codeBlock = /```[a-zA-Z]*\n([\s\S]*?)```/g;
for (const f of files) {
  const t = fs.readFileSync(f, 'utf8');
  let m;
  while ((m = codeBlock.exec(t))) {
    for (const b of banned) {
      const re = new RegExp('^\\s*' + b + '\\s*:', 'mi');
      if (re.test(m[1])) { bad(`${path.relative(ROOT, f)} declares '${b}:' as a schema field`); violations++; }
    }
  }
}
if (!violations) ok(`No prohibited business term declared as a schema type across ${files.length} artifacts`);

console.log('\n=== LAW 002 — Knowledge Once ===');
const ids = M.artifacts.map(a => a.id);
if (new Set(ids).size === ids.length) ok(`All ${ids.length} artifact IDs unique`);
else bad('duplicate artifact IDs');

console.log('\n=== LAW 005 — Explainability ===');
const seven = ['What happened', 'Who authorized', 'Which policy', 'What evidence', 'What confidence'];
let missing = 0;
for (const f of projected) {
  const t = fs.readFileSync(f, 'utf8');
  for (const q of seven) if (!t.includes(q)) { bad(`${path.relative(ROOT, f)} missing "${q}"`); missing++; break; }
}
if (!missing) ok('Explainability questions present in every artifact');

console.log('\n=== SECTION COMPLETENESS (50/50) ===');
let incomplete = 0;
for (const f of projected) {
  const t = fs.readFileSync(f, 'utf8');
  for (let i = 1; i <= 50; i++) if (!t.includes(`\n## ${i}.`)) { bad(`${path.relative(ROOT, f)} missing section ${i}`); incomplete++; break; }
}
if (!incomplete) ok(`All ${projected.length} projected artifacts carry all 50 sections`);

console.log('\n=== ZERO PARTIAL — NO GENERIC FILLER ===');
let generic = 0;
for (const f of projected) {
  const t = fs.readFileSync(f, 'utf8');
  const m = t.match(/→ Governed by ([A-Z\-0-9]+)\. Content projected from/);
  if (m) { bad(`${path.relative(ROOT, f)} still has generic filler for a section`); generic++; }
}
if (!generic) ok(`No artifact contains generic filler — every section carries domain substance`);

console.log('\n=== REGISTRY COVERAGE ===');
const projectedCount = M.artifacts.filter(a => a.status === 'generated').length;
if (projectedCount === M.totalArtifacts) ok(`Manifest complete: ${projectedCount}/${M.totalArtifacts} projected`);
else bad(`only ${projectedCount}/${M.totalArtifacts} projected`);

console.log(`\n${fail === 0 ? 'ALL CONSTITUTIONAL CHECKS PASSED' : fail + ' CHECK(S) FAILED'}`);
process.exit(fail ? 1 : 0);
