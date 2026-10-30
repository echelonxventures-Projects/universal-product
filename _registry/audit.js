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

/* the projection is one master document and one volume per register category */
const MASTER = path.join(ROOT, 'UCOS-MASTER.md');
const VOLDIR = path.join(ROOT, 'volumes');
const M = JSON.parse(fs.readFileSync(path.join(__dirname, 'manifest.json'), 'utf8'));
const P = JSON.parse(fs.readFileSync(path.join(__dirname, 'primitives.json'), 'utf8'));
const D = JSON.parse(fs.readFileSync(path.join(__dirname, 'domains.json'), 'utf8'));
const read = f => { try { return fs.readFileSync(f, 'utf8'); } catch (e) { return null; } };
const volumes = (() => { try { return fs.readdirSync(VOLDIR).filter(f => f.endsWith('.md')).map(f => path.join(VOLDIR, f)); } catch (e) { return []; } })();
const files = [MASTER].concat(volumes).filter(f => read(f) != null);
const anchorOf = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

console.log('\n=== THE MASTER AND ITS VOLUMES ===');
if (read(MASTER)) ok('UCOS-MASTER.md exists'); else bad('UCOS-MASTER.md is missing — run node _registry/project.js');
const cats = D.categories || [];
const layout = M.projection || {};
const max = Number(layout.maxVolumeBytes) || Infinity;
const volOf = c => volumes.filter(f => new RegExp('^V' + c.categoryId.replace(/^C/, '') + '(\\.\\d+)?-').test(path.basename(f)));
const uncovered = cats.filter(c => !volOf(c).length).map(c => c.name);
if (!uncovered.length) ok(`${volumes.length} volumes cover all ${cats.length} register categories`);
else bad('categories with no volume: ' + uncovered.join(', '));
/* a volume may pass the limit only when it holds a single artifact entry that alone is larger */
const oversize = volumes.filter(f => Buffer.byteLength(read(f)) > max && (read(f).match(/\n#### /g) || []).length > 1).map(f => path.basename(f));
if (!oversize.length) ok(`every volume is within the ${Math.round(max / 1024)} KB limit, or is one artifact that alone is larger`);
else bad('volumes over the limit that should have split: ' + oversize.join(', '));
const stray = fs.readdirSync(ROOT, { withFileTypes: true }).filter(e => e.isDirectory() && /^[0-9]+-/.test(e.name)).map(e => e.name);
if (!stray.length) ok('no per-artifact folders remain'); else bad('per-artifact folders remain: ' + stray.join(', '));

console.log('\n=== LAW 001 — Zero Hard Coding ===');
// Law 001 applies to *schema types*, which live inside fenced code blocks.
// Prose that quotes a term while explaining the law is not a violation.
const banned = P.prohibited;
let violations = 0;
const codeBlock = /```[a-zA-Z]*\n([\s\S]*?)```/g;
for (const f of files) {
  const t = read(f);
  let m;
  while ((m = codeBlock.exec(t))) {
    for (const b of banned) {
      const re = new RegExp('^\\s*' + b + '\\s*:', 'mi');
      if (re.test(m[1])) { bad(`${path.relative(ROOT, f)} declares '${b}:' as a schema field`); violations++; }
    }
  }
}
if (!violations) ok(`No prohibited business term declared as a schema type across the master and ${volumes.length} volumes`);

console.log('\n=== LAW 002 — Knowledge Once ===');
const ids = M.artifacts.map(a => a.id);
if (new Set(ids).size === ids.length) ok(`All ${ids.length} artifact IDs unique`);
else bad('duplicate artifact IDs');
const masterText = read(MASTER) || '';
const std = masterText.indexOf('<a id="standard-contract">');
const volText = volumes.map(read).join('\n');
if (std > 0 && !volText.includes('### Executive Summary')) ok('The standard contract is stated once, in the master — no volume repeats it');
else bad('the standard contract is missing from the master or repeated in a volume');

console.log('\n=== LAW 005 — Explainability ===');
const seven = ['What happened', 'Who authorized', 'Which policy', 'What evidence', 'What confidence'];
const missingQ = seven.filter(q => !masterText.slice(std).includes(q));
if (!missingQ.length) ok('Explainability questions present in the standard contract every artifact inherits');
else bad('standard contract missing: ' + missingQ.join(', '));

console.log('\n=== SECTION COMPLETENESS ===');
let incomplete = 0;
for (const a of M.artifacts) {
  const at = volText.indexOf(`<a id="${anchorOf(a.id)}"></a>`);
  if (at < 0) { bad(`${a.id} has no entry in any volume`); incomplete++; continue; }
  const heading = volText.indexOf('\n#### ', at);
  const next = Math.min(...['\n#### ', '\n### ', '\n---'].map(h => { const i = volText.indexOf(h, heading + 1); return i < 0 ? Infinity : i; }));
  const entry = volText.slice(at, next === Infinity ? undefined : next);
  const sections = (entry.match(/\n##### /g) || []).length;
  if (sections !== 28) { bad(`${a.id} carries ${sections}/28 of its own sections`); incomplete++; }
}
if (!incomplete) ok(`All ${M.artifacts.length} artifacts carry all 28 of their own sections, plus the standard contract`);

console.log('\n=== ZERO PARTIAL — NO GENERIC FILLER ===');
const filler = files.filter(f => /→ Governed by ([A-Z\-0-9]+)\. Content projected from/.test(read(f)));
if (!filler.length) ok('No generic filler in the master or any volume');
else for (const f of filler) bad(`${path.relative(ROOT, f)} still has generic filler for a section`);

console.log('\n=== LINKS — EVERY REFERENCE RESOLVES ===');
const anchors = new Map(files.map(f => [path.resolve(f), new Set([...read(f).matchAll(/<a id="([^"]+)"/g)].map(m => m[1]))]));
let links = 0, broken = 0;
for (const f of files) {
  for (const m of read(f).matchAll(/\]\(([^)#\s]*)#([^)\s]+)\)/g)) {
    links++;
    const target = m[1] ? path.resolve(path.dirname(f), m[1]) : path.resolve(f);
    if (!(anchors.get(target) || new Set()).has(m[2])) { broken++; if (broken <= 5) bad(`${path.relative(ROOT, f)} → ${m[1]}#${m[2]} does not resolve`); }
  }
}
if (!broken) ok(`All ${links} links resolve to an anchor`);

console.log('\n=== REGISTRY COVERAGE ===');
const projectedCount = M.artifacts.filter(a => a.status === 'generated').length;
if (projectedCount === M.artifacts.length) ok(`Manifest complete: ${projectedCount}/${M.artifacts.length} projected`);
else bad(`only ${projectedCount}/${M.artifacts.length} projected`);

console.log(`\n${fail === 0 ? 'ALL CONSTITUTIONAL CHECKS PASSED' : fail + ' CHECK(S) FAILED'}`);
process.exit(fail ? 1 : 0);
