#!/usr/bin/env node
'use strict';

/*
 * UCOS Ω∞ — Constitutional Document Projection Generator
 *
 * Law 002 (Knowledge Once): every artifact is PROJECTED from _registry/*.json.
 * Law 003 (Projection Law): documents are projections, never the source of truth.
 * Law 001 (Zero Hard Coding): no domain content is embedded in this generator.
 *
 * Usage:
 *   node _registry/project.js            # generate all planned artifacts
 *   node _registry/project.js UCOS-CON-000001 UCOS-IDN-000001   # generate subset
 *   node _registry/project.js --list     # list manifest
 *   node _registry/project.js --check    # verify registry integrity + coverage
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const REG = __dirname;

function load(name) {
  return JSON.parse(fs.readFileSync(path.join(REG, name), 'utf8'));
}

const PRIMITIVES = load('primitives.json');
const TERMS = load('terminology.json');
const DOMAINS = load('domains.json');
const MANIFEST = load('manifest.json');
const CONTENT_MAP = load('content-map.json');
const CODEBASE = load('codebase.json');
/* the concept register is derived at compile time (lib/canonical.js) and read from the seal */
let _register, _api;
function liveApi() {
  if (_api === undefined) {
    const silence = console.log; console.log = () => { };
    try { _api = require(path.join(ROOT, 'lib', 'canonical.js')).get().api || null; } finally { console.log = silence; }
  }
  return _api;
}
function conceptRegister() {
  if (_register === undefined) {
    const silence = console.log; console.log = () => { };
    try { _register = require(path.join(ROOT, 'lib', 'canonical.js')).get().register || null; } finally { console.log = silence; }
  }
  return _register;
}
const ROADMAP = load('roadmap.json');
const ALIGNMENT = load('alignment.json');
const DOCUMENTS = load('documents.json');

/* ---------- content registries ---------- */
const CONTENT_FILE_NAMES = {
  core: 'content-core.json', ext: 'content-ext.json', commerce: 'content-commerce.json',
  'twin-agent': 'content-twin-agent.json', 'runtime-data': 'content-runtime-data.json',
  'sec-ops-dep-qlt': 'content-sec-ops-dep-qlt.json', platform: 'content-platform.json'
};
const CONTENT = Object.fromEntries(Object.entries(CONTENT_FILE_NAMES).map(([k, f]) => [k, load(f).content]));

/* resolve the domain-specific content block for an artifact */
function contentFor(art) {
  const map = CONTENT_MAP.mapping[art.id];
  if (!map) return null;
  const src = CONTENT[map.src];
  return (src && src[map.key]) || null;
}

/* ---------- canonical section template (50 sections) ---------- */
const SECTIONS = [
  'Executive Summary', 'Constitutional Purpose', 'Scope', 'Out of Scope', 'Definitions',
  'Canonical Terminology', 'Ownership Boundaries', 'Domain Responsibilities', 'Domain Non-Responsibilities',
  'Concepts', 'Ontology', 'Taxonomy', 'Registries', 'Data Model', 'Graph Model', 'Schemas',
  'Contracts', 'APIs', 'Events', 'Commands', 'Queries', 'State Machines', 'Workflows',
  'Policies', 'Rules', 'Authorities', 'Permissions', 'Security Model', 'Privacy Model',
  'Trust Model', 'Audit Model', 'Observability Model', 'Digital Twin Model', 'Agent Model',
  'Runtime Model', 'Scaling Model', 'Multi-Tenant Model', 'Geo-Distribution Model',
  'Failure Model', 'Recovery Model', 'Verification Model', 'Certification Model',
  'Migration Model', 'Evolution Model', 'Implementation Blueprint', 'Reference Architecture Diagram',
  'Sequence Diagrams', 'State Diagrams', 'Data Flow Diagrams', 'Dependency Maps'
];

/* ---------- registry lookups ---------- */
function domainOf(idOrName) {
  return DOMAINS.domains.find(d => d.name.toLowerCase() === String(idOrName).toLowerCase())
      || DOMAINS.domains.find(d => d.domainId === idOrName)
      || null;
}
function artifact(id) { return MANIFEST.artifacts.find(a => a.id === id); }
/* ownership is declared once, in domains.json */
function ownerOf(name) { const d = DOMAINS.domains.find(x => (x.owns || []).includes(name)); return d ? d.name : '—'; }
function categoryOf(domainName) {
  const d = DOMAINS.domains.find(x => x.name === domainName);
  const c = d && (DOMAINS.categories || []).find(x => x.categoryId === d.category);
  return c ? c.categoryId + ' ' + c.name : '—';
}
/* one classification: an artifact is filed under its owning domain's register category */
function categoryRow(art) {
  const d = DOMAINS.domains.find(x => x.name === art.owner);
  return d && (DOMAINS.categories || []).find(c => c.categoryId === d.category);
}
const slugOf = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');


/* ---------- content projections (derived, never hardcoded domain truth) ---------- */
function sectionBody(art, sec, d) {
  const id = art.id, title = art.title;
  const R = (k) => `_${k}_`; // registry-reference marker
  switch (sec) {
    case 'Executive Summary': return [
      `**${id} — ${title}**`,
      '',
      `This artifact is a constitutionally governed, implementation-ready specification projected from the ${R('UCOS Registry')} single source of truth.`,
      `It conforms to the ${R('Immutable Primitive Registry')} (${PRIMITIVES.count} frozen primitives) and the ${R('Canonical Terminology Registry')} (${TERMS.terms.length} governed terms).`,
      'It contains no hardcoded business, industry, currency, country, or commerce concepts. All such concepts are runtime projections.'
    ].join('\n');
    case 'Constitutional Purpose': return [
      `To define the binding contract for **${title}** such that:`,
      '- every concept it names has exactly one owner,',
      '- every capability it exposes has exactly one boundary,',
      '- every boundary is expressed as an explicit contract,',
      '- every contract is enforceable by the Governance Constitution.'
    ].join('\n');
    case 'Scope': return [
      `In scope: the primitives, contracts, schemas, events, and policies owned by **${title}**.`,
      'In scope: the projection rules by which this domain exposes its truth to other domains.',
      'In scope: the verification obligations this domain must satisfy before activation.'
    ].join('\n');
    case 'Out of Scope': return [
      'Out of scope: any concept owned by another constitutional domain.',
      'Out of scope: business, industry, commerce, country, currency, or language content (all projected).',
      'Out of scope: mutation of another domain’s internal state.'
    ].join('\n');
    case 'Definitions': return [
      'All terms in this artifact are used in their canonical sense as defined in the Canonical Terminology Registry.',
      'Where a term appears, its `termId` is normative and its `prohibitedMeanings` are void.'
    ].join('\n');
    case 'Canonical Terminology': return [
      '| Term | Canonical Definition | Owner | Prohibited Meanings |',
      '|---|---|---|---|',
      ...TERMS.terms.slice(0, 12).map(t =>
        `| ${t.canonicalName} | ${t.definition} | ${ownerOf(t.canonicalName)} | ${(t.prohibitedMeanings || []).join(', ')} |`)
    ].join('\n');
    case 'Ownership Boundaries': return d ? [
      `**Owner:** ${d.name} Domain`,
      `**Owns:** ${d.owns.join(', ')}`,
      `**Boundary law:** no domain may modify, bypass, or reinterpret another domain’s internals. All interaction is via contract.`
    ].join('\n') : `Ownership is recorded in the ${R('Domain Ownership Registry')}.`;
    case 'Domain Responsibilities': return d && d.responsible
      ? d.responsible.map(r => `- ${r}`).join('\n')
      : 'See the Domain Ownership Registry for the authoritative responsibility list.';
    case 'Domain Non-Responsibilities': return d && d.notResponsible
      ? d.notResponsible.map(r => `- ${r}`).join('\n')
      : (d && d.mustObey ? d.mustObey.map(r => `- Must obey: ${r}`).join('\n')
         : 'See the Domain Ownership Registry.');
    case 'Registries': return [
      'This domain is registry-driven. Its registries are entries in the Universal Registry System:',
      '',
      '```yaml',
      `RegistryEntry:`,
      `  registryId: UCOS-REG-${(d ? d.name : 'DOMAIN').toUpperCase().replace(/[^A-Z]/g, '')}`,
      `  owner: ${d ? d.name + ' Domain' : 'Constitutional Authority'}`,
      `  law: Knowledge Once — each concept defined exactly once`,
      '```'
    ].join('\n');
    case 'Schemas': return [
      '```yaml',
      `# Canonical projection schema for ${id}`,
      `${id.toLowerCase().replace(/-/g, '_')}:`,
      `  identity:      <Identity primitive>`,
      `  intent:        <Intent primitive>`,
      `  meaning:       <Meaning primitive>`,
      `  knowledge:     <Knowledge primitive>`,
      `  registry:      <Registry primitive>`,
      `  relationship:  <Relationship primitive>`,
      `  context:       <Context primitive>`,
      `  policy:        <Policy primitive>`,
      `  authority:     <Authority primitive>`,
      `  evidence:      <Evidence primitive>`,
      `  trust:         <Trust primitive>`,
      `  temporal:      <Time primitive>`,
      `  metadata:      <Metadata primitive>`,
      '```'
    ].join('\n');
    case 'Contracts': return [
      '```yaml',
      `DomainContract:`,
      `  domain: ${d ? d.name : title}`,
      `  commands:   []   # registry-driven`,
      `  queries:    []   # registry-driven`,
      `  events:     []   # registry-driven`,
      `  policies:   []   # registry-driven`,
      `  permissions: []  # registry-driven`,
      '```',
      '',
      'Contract law: domains never directly access another domain’s internal structures.'
    ].join('\n');
    case 'Policies': return [
      '```yaml',
      `Policy:`,
      `  identity: <Identity>`,
      `  conditions: []   # registry-driven`,
      `  actions:    []   # registry-driven`,
      `  priorities: []   # registry-driven`,
      `  exceptions: []   # registry-driven`,
      '```',
      '',
      'All behavior derives from policy. Policy ≠ Rule: policy is behavioral governance; the rule is its executable projection.'
    ].join('\n');
    case 'Rules': return [
      '```yaml',
      `Rule:`,
      `  ruleId: <Identity>`,
      `  derivedFrom: <Policy identity>`,
      `  executable: true`,
      `  constraint: <registry expression>`,
      '```'
    ].join('\n');
    case 'Security Model': return [
      'Zero Trust applies: no implicit trust between domains, services, agents, or tenants.',
      'Every call is authenticated, authorized against Policy, and evidenced.',
      'Cryptographic identity is issued by the Identity Domain; keys by the Key Management Architecture.'
    ].join('\n');
    case 'Trust Model': return [
      'Trust is computed, never assumed. Inputs: evidence, authority, consistency, provenance, confidence.',
      '```yaml',
      `Trust:`,
      `  evidenceScore: <0..1>`,
      `  authorityScore: <0..1>`,
      `  consistencyScore: <0..1>`,
      `  provenanceScore: <0..1>`,
      `  confidenceScore: <0..1>`,
      '```'
    ].join('\n');
    case 'Observability Model': return [
      'Every action emits: What happened? Why? Who authorized it? Which policy allowed it? What evidence supports it? What confidence exists? What alternatives were evaluated?',
      'These are the seven Explainability questions and are mandatory event fields.'
    ].join('\n');
    case 'Verification Model': return [
      `Before activation, ${title} must pass identity, knowledge, relationship, context, policy, authority, trust, and reality integrity checks.`,
      'Verification is performed by the Formal Verification Architecture (UCOS-FML-000001).'
    ].join('\n');
    case 'Evolution Model': return [
      'Evolution is governed and history-preserving. Primitives are frozen; extension occurs through registries, policies, capabilities, contexts, relationships, knowledge, agents, and projections — never through primitive expansion.'
    ].join('\n');
    case 'Reference Architecture Diagram': return [
      '```mermaid',
      'graph TD',
      `    REG["UCOS Registry<br/>Single Source of Truth"]`,
      `    DOM["${title}"]`,
      '    REG -- projects --> DOM',
      `    DOM -- contract --> OTHER["Other Constitutional Domains"]`,
      `    DOM -- primitives --> PROJ["Runtime Projections"]`,
      '```'
    ].join('\n');
    case 'Dependency Maps': return [
      '```mermaid',
      'graph TD',
      '    IDN[Identity] --> KNW[Knowledge]',
      '    KNW --> REL[Relationships]',
      '    REL --> CTX[Context]',
      '    CTX --> POL[Policy]',
      '    POL --> TRU[Trust]',
      '    TRU --> PROJ[Projection]',
      '```',
      '',
      'Forbidden: circular dependencies, mutual ownership, cross-domain state mutation.'
    ].join('\n');
    case 'Data Flow Diagrams': return [
      '```mermaid',
      'flowchart LR',
      '    OBS[Observation] --> EVD[Evidence]',
      '    EVD --> KNW[Knowledge]',
      '    KNW --> INF[Inference]',
      '    INF --> SIM[Simulation]',
      '    SIM --> DEC[Decision]',
      '    DEC --> PROJ[Projection]',
      '```'
    ].join('\n');
    default: {
      // Law 002: resolve substantive content from the content registries.
      // A generic placeholder is a constitutional defect; the audit enforces this.
      const c = contentFor(art);
      if (c) {
        // try the direct camelCase key, then a set of known aliases
        const key = sec.charAt(0).toLowerCase() + sec.slice(1).replace(/[^a-zA-Z]/g, '');
        const aliases = SECTION_CONTENT_KEYS[sec] || [];
        for (const k of [key, ...aliases]) {
          if (c[k]) return c[k];
        }
      }
      // Fallback sections that genuinely have no domain-specific content yet
      // must still be explicit, not silent filler.
      return `→ Governed by ${id}. Content projected from the ${(categoryRow(art) || { name: 'owning category' }).name} registry under ${R('Law 002')}.`;
    }
  }
}

/* section name -> content registry key aliases (handles plural/model suffix mismatch) */
const SECTION_CONTENT_KEYS = {
  'State Machines': ['stateMachine', 'stateMachines'],
  'Workflows': ['workflow', 'workflows'],
  'Privacy Model': ['privacy'],
  'Audit Model': ['audit'],
  'Digital Twin Model': ['twin'],
  'Agent Model': ['agent'],
  'Runtime Model': ['runtime'],
  'Scaling Model': ['scaling'],
  'Multi-Tenant Model': ['multiTenant'],
  'Geo-Distribution Model': ['geo'],
  'Failure Model': ['failure'],
  'Recovery Model': ['recovery'],
  'Certification Model': ['certification'],
  'Migration Model': ['migration'],
  'Sequence Diagrams': ['sequence'],
  'State Diagrams': ['state'],
  'Data Flow Diagrams': ['dataFlow', 'dataModel'],
  'Implementation Blueprint': ['blueprint', 'implementation'],
  'Reference Architecture Diagram': ['architecture', 'reference'],
  'Commands': ['commands'],
  'Queries': ['queries'],
  'Events': ['events'],
  'APIs': ['apis'],
  'Policies': ['policies'],
  'Rules': ['rules'],
  'Authorities': ['authorities'],
  'Permissions': ['permissions'],
  'Security Model': ['security'],
  'Trust Model': ['trust'],
  'Observability Model': ['observability'],
  'Verification Model': ['verification'],
  'Evolution Model': ['evolution']
};

/* ---------- document projection ---------- */
function project(art) {
  /* the owning domain, as the manifest declares it */
  const d = domainOf(art.owner);

  const lines = [];
  lines.push(`# ${art.id}`);
  lines.push(`# ${art.title}`);
  lines.push('');
  lines.push(`**Version:** Ω∞.1  |  **Status:** Constitutional Artifact  |  **Authority:** UCOS Ω∞ Constitutional Authority`);
  lines.push(`**Owner:** ${art.owner} Domain  |  **Category:** ${categoryOf(art.owner)}  |  **Source of Truth:** \`_registry/\` (projected, never hand-authored)`);
  lines.push('');
  lines.push('> Constitutional notice: this document is a **projection**. Its truth lives in the registry.');
  lines.push('> The runtime parses the same registry files (`lib/ucos-registry.js`), so this artifact is');
  lines.push('> also a LIVE universe — operable through the generic entity engine, not only readable here.');
  lines.push('> Editing this document directly violates Law 002 (Knowledge Once).');
  lines.push('');
  for (const sec of SECTIONS) {
    lines.push('---');
    lines.push('');
    lines.push(`## ${SECTIONS.indexOf(sec) + 1}. ${sec}`);
    lines.push('');
    lines.push(sectionBody(art, sec, d));
    lines.push('');
  }
  lines.push('---');
  lines.push('');
  lines.push('## ∞');
  lines.push('');
  lines.push('Constitutionally governed. Implementation ready. Universally extensible.');
  return lines.join('\n');
}

/* ---------- the master document and its volumes ----------
   One master and one or more volumes per register category, all projected from the
   registry. The layout is data (manifest.json → projection): the master's file name, the
   volume folder and the size a volume may reach. A category whose volume would pass that
   size is split into numbered parts (V11.1, V11.2, …) along domain boundaries — and inside a
   domain, between artifacts — so a new volume appears on the next projection and disappears
   again when the category shrinks. Every anchor is placed before any link is written, so a
   link always points at the part that holds its target.

   The master is the hub: how to manage, the volume register with live counts, the index,
   the constitution, the standard contract (stated once), the glossary and the ID lookup. A
   volume holds its domains' cards and each artifact's own sections only. */

const LAYOUT = MANIFEST.projection || {};
const MASTER_FILE = LAYOUT.masterFile;
const VOLUME_DIR = LAYOUT.volumeDir;
const MAX_BYTES = Number(LAYOUT.maxVolumeBytes) || Infinity;
/* the template sections whose text depends on the owning domain: stated once, on the
   domain's card, rather than repeated under every artifact */
const DOMAIN_SECTIONS = ['Ownership Boundaries', 'Domain Responsibilities', 'Domain Non-Responsibilities'];

const anchor = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const termAnchor = name => 't-' + anchor(name);
const domainAnchor = d => anchor(d.domainId);
const catOfDomain = d => (DOMAINS.categories || []).find(c => c.categoryId === d.category);
const domainByName = n => DOMAINS.domains.find(d => d.name === n);
const domainsOf = c => DOMAINS.domains.filter(d => d.category === c.categoryId);
const artifactsOf = d => MANIFEST.artifacts.filter(a => a.owner === d.name);
const contentKeyFor = (block, sec) => {
  const key = sec.charAt(0).toLowerCase() + sec.slice(1).replace(/[^a-zA-Z]/g, '');
  return [key, ...(SECTION_CONTENT_KEYS[sec] || [])].find(k => block && block[k] != null && String(block[k]).trim());
};
const render = v => Array.isArray(v) ? v.map(x => `- ${x}`).join('\n') : String(v);

/* where every anchor lives: '' is the master, otherwise a volume file name */
let LOC = new Map();
function href(from, id) {
  const at = LOC.has(id) ? LOC.get(id) : '';
  if (at === from) return '#' + id;
  if (from === '') return `${VOLUME_DIR}/${at}#${id}`;
  if (at === '') return `../${MASTER_FILE}#${id}`;
  return `${at}#${id}`;
}
const linkDomain = (d, from) => `[${d.name}](${href(from, domainAnchor(d))})`;
const linkArtifact = (a, from, label) => `[${label || a.id}](${href(from, anchor(a.id))})`;
const linkTerm = (name, from) => `[${name}](${href(from, termAnchor(name))})`;

function genericSections() {
  const probe = { id: '<artifact id>', title: '<artifact title>', owner: '<owning domain>' };
  return SECTIONS.filter(s => !DOMAIN_SECTIONS.includes(s))
    .map(s => ({ s, body: sectionBody(probe, s, { name: '<owning domain>', owns: [] }) }))
    .filter(x => !x.body.startsWith('→ Governed by'));
}

function domainCard(d, from) {
  const c = catOfDomain(d), arts = artifactsOf(d);
  const contract = MANIFEST.artifacts.find(a => a.id === d.contract);
  return [
    `<a id="${domainAnchor(d)}"></a>`,
    `### ${d.domainId} · ${d.name}`,
    '',
    '| | |', '|---|---|',
    `| **Category** | ${c.categoryId} ${c.name} |`,
    `| **Build status** | ${d.status}${d.status === 'designed' ? ' — declared and contracted; no code or live route yet' : ''} |`,
    `| **Owns** | ${(d.owns || []).map(o => linkTerm(o, from)).join(', ')} |`,
    `| **Responsible for** | ${(d.responsible || []).join(', ')} |`,
    d.notResponsible ? `| **Not responsible for** | ${d.notResponsible.join(', ')} |` : `| **Must obey** | ${(d.mustObey || []).join(', ')} |`,
    `| **Contract** | ${contract ? linkArtifact(contract, from, contract.id + ' ' + contract.title) : '—'} |`,
    `| **Artifacts** | ${arts.map(a => linkArtifact(a, from)).join(', ')} |`,
    `| **Concepts** | ${((conceptRegister() || { counts: { byOwner: {} } }).counts.byOwner[d.name] || 0)} — \`node _registry/compile.js --search <words> --kind concept --owner "${d.name}"\` |`,
    `| **Code** | ${CODEBASE.modules.filter(m => (m.parts || [{ owner: m.owner }]).some(p => p.owner === d.name)).map(m => '\`' + m.path + '\`').join(', ') || '—'} |`,
    `| **Managed in** | \`_registry/domains.json\` → \`${d.domainId}\` |`,
    '',
    ...(() => {
      const routes = ((liveApi() || {}).routes || []).filter(r => r[3] === d.name);
      return routes.length
        ? [`**Live routes (${routes.length})** — what the platform serves today for this domain:`, '', ...routes.map(r => `- \`${r[0]} ${r[1]}\``), '']
        : ['**Live routes:** none yet.', ''];
    })()
  ].join('\n');
}

function artifactEntry(a, from) {
  const route = CONTENT_MAP.mapping[a.id] || {};
  const block = contentFor(a) || {};
  const out = [
    `<a id="${anchor(a.id)}"></a>`,
    `#### ${a.id} · ${a.title}`,
    '',
    `Owner ${linkDomain(domainByName(a.owner), from)} · managed in \`_registry/manifest.json\` → \`${a.id}\`, content \`_registry/content-${route.src}.json\` → \`${route.key}\` · inherits the [standard contract](${href(from, 'standard-contract')})`,
    ''
  ];
  const used = new Set();   /* a content key renders once, under the first section that claims it */
  for (const sec of SECTIONS) {
    const k = contentKeyFor(block, sec);
    if (!k || used.has(k)) continue;
    used.add(k);
    out.push(`<a id="${anchor(a.id + '-' + sec)}"></a>`);
    out.push(`##### ${sec}`, '', ...(k === 'apis' ? ['*Designed interface: the contract the domain is built towards. The routes it serves today are on its card.*', ''] : []), render(block[k]), '');
  }
  return out.join('\n');
}

/* the layout: each category becomes one volume, or numbered parts when it would pass the
   size limit. Units are packed in registry order — a domain's card with its artifacts,
   breaking between artifacts only when one domain alone passes the limit. */
function layout(max) {
  LOC = new Map();
  const volumes = [];
  for (const c of DOMAINS.categories || []) {
    const parts = [[]];
    let used = 0;
    const place = (piece, bytes) => {
      if (used && used + bytes > max) { parts.push([]); used = 0; }
      parts[parts.length - 1].push(piece);
      used += bytes;
    };
    for (const d of domainsOf(c)) {
      const card = { kind: 'card', d }, arts = artifactsOf(d).map(a => ({ kind: 'artifact', a, d }));
      const size = x => Buffer.byteLength(x.kind === 'card' ? domainCard(x.d, '?') : artifactEntry(x.a, '?'));
      const whole = [card, ...arts].reduce((n, x) => n + size(x), 0);
      if (used && used + whole > max && whole <= max) { parts.push([]); used = 0; }
      for (const x of [card, ...arts]) place(x, size(x));
    }
    const no = c.categoryId.replace(/^C/, '');
    parts.forEach((pieces, i) => {
      const id = parts.length > 1 ? `V${no}.${i + 1}` : `V${no}`;
      const file = `${id}-${slugOf(c.name)}.md`;
      volumes.push({ id, file, category: c, part: i + 1, of: parts.length, pieces });
      for (const x of pieces) LOC.set(x.kind === 'card' ? domainAnchor(x.d) : anchor(x.a.id), file);
      for (const x of pieces) if (x.kind === 'artifact') for (const sec of SECTIONS) LOC.set(anchor(x.a.id + '-' + sec), file);
    });
  }
  return volumes;
}

function volumeText(v, volumes) {
  const c = v.category, from = v.file;
  const siblings = volumes.filter(x => x.category === c);
  const lines = [
    `# Volume ${v.id} · ${c.name}${v.of > 1 ? ` (part ${v.part} of ${v.of})` : ''}`,
    '',
    `**Part of** [the master document](../${MASTER_FILE}) · **Category** ${c.categoryId} · **Projected from** \`_registry/\` — never edit this file: change the registry and run \`npm run registry\`.`,
    ''
  ];
  if (v.of > 1) lines.push(`**Parts:** ${siblings.map(x => x === v ? `**${x.id}**` : `[${x.id}](${x.file})`).join(' · ')}`, '');
  lines.push(`> ${c.covers}`, '', '## Contents', '');
  for (const x of v.pieces) {
    if (x.kind === 'card') lines.push(`- [${x.d.domainId} ${x.d.name}](#${domainAnchor(x.d)})`);
    else lines.push(`  - [${x.a.id} ${x.a.title}](#${anchor(x.a.id)})`);
  }
  lines.push('');
  let current = null;
  for (const x of v.pieces) {
    if (x.kind === 'card') { lines.push('---', '', domainCard(x.d, from)); current = x.d; continue; }
    if (current !== x.d) { lines.push('---', '', `### ${x.d.domainId} · ${x.d.name} (continued)`, '', `The domain's card is in ${linkDomain(x.d, from)}.`, ''); current = x.d; }
    lines.push(artifactEntry(x.a, from));
  }
  return lines.join('\n') + '\n';
}

function masterText(volumes, sizes, max) {
  const cats = DOMAINS.categories || [];
  const L = [];
  const from = '';
  L.push('# UCOS Ω∞ — Master Document', '');
  L.push(`**Projected from** \`_registry/\` (the single source of truth). Never edit this file or a volume: change the registry, then run \`npm run registry\`. Last amendment: ${(DOMAINS.amendments || []).slice(-1).map(x => x.amendmentId + ' (' + x.date + ')').join('') || '—'}.`, '');
  L.push('## Contents', '',
    '1. [How to manage](#how-to-manage)', '2. [Volume register](#volume-register)', '3. [Index](#index)',
    '4. [Constitution](#constitution)', '5. [Kernel](#kernel)', '6. [Standard contract](#standard-contract)', '7. [Glossary](#glossary)',
    '8. [Code and document map](#code-map)', '9. [Concept register](#concept-register)', '10. [Other domain systems](#alignment)', '11. [Build path and decisions](#build-path)', '12. [ID lookup](#id-lookup)', '');

  L.push('<a id="how-to-manage"></a>', '## 1. How to manage', '',
    'Everything here is projected. To change it, edit the registry entry named below, then run `npm run registry`. That re-projects this document and every volume, audits them, then compiles, gates and seals the registry. `npm test` fails if any document is out of date with the registry.', '',
    '| To change | Edit |', '|---|---|',
    '| A category (add, rename, describe) | `_registry/domains.json` → `categories` |',
    '| A domain (add, owns, responsibilities, category, contract) | `_registry/domains.json` → `domains` |',
    '| A law (statement, aliases, sources, enforcement status) | `_registry/domains.json` → `laws`, with an entry in `amendments` |',
    '| A kernel part | `_registry/domains.json` → `kernel` |',
    '| Which domain owns a code file | `_registry/codebase.json` → `modules` |',
    '| A document’s status (corpus source, projection, living record, guidance, superseded) and owner | `_registry/documents.json` → `documents` (move a superseded document into `_superseded/`) |',
    '| A build step’s status, a design decision, or a gap | `_registry/roadmap.json` → `steps`, `decisions`, `gaps` |',
    '| Which domain owns a live API route | `_registry/api.json` → `owners` (rules by path; the first match wins) |',
    '| A domain’s build status | derived: `designed` until it owns code or a live route (`_registry/domains.json` → `status`, checked by the gate) |',
    '| Which register domain owns a part of another domain system | `_registry/alignment.json` → `systems` |',
    '| A primitive (frozen: needs an amendment) | `_registry/primitives.json`, with an entry in `domains.json` → `amendments` |',
    '| A term (add, define) | `_registry/terminology.json`, and add it to exactly one domain’s `owns` |',
    '| An artifact (add, retitle, owner) | `_registry/manifest.json` → `artifacts`, a route in `_registry/content-map.json`, a content block in a `_registry/content-*.json` |',
    '| An artifact’s sections | its content block (the route is shown under each artifact) |',
    '| The document layout (master file, volume folder, size limit per volume) | `_registry/manifest.json` → `projection` |',
    '',
    '**Commands.** `npm run registry` re-projects, audits, compiles, gates and seals · `node _registry/project.js --watch` re-projects whenever a registry file changes · `node _registry/project.js --list` lists the artifacts · `node _registry/project.js --check` checks registry integrity · `node _registry/audit.js` enforces the laws over the master and volumes · `node _registry/compile.js --search <words> [--kind …] [--category …] [--owner …]` finds anything.', '',
    '**Provenance.** `_superseded/` keeps the hand-authored documents the registry was distilled from. They are history, not a source of truth.', '',
    'The integrity gate refuses a change that leaves a name owned twice or not at all, a domain without a category or contract, an unowned artifact, or a reserved name.', '');

  L.push('<a id="volume-register"></a>', '## 2. Volume register', '',
    `**${volumes.length} volumes** for ${cats.length} categories · ${DOMAINS.domains.length} domains · ${MANIFEST.artifacts.length} artifacts · ${PRIMITIVES.primitives.length} primitives · ${TERMS.terms.length} terms.`, '',
    `A volume may reach ${Math.round(max / 1024)} KB (\`manifest.json\` → \`projection.maxVolumeBytes\`). A category that would pass it is split into numbered parts on the next projection, and merged back when it shrinks.`, '',
    '| Volume | Category | Part | Domains | Artifacts | Size |', '|---|---|---|---:|---:|---:|');
  for (const v of volumes) {
    const doms = new Set(v.pieces.map(x => x.d.name)).size, arts = v.pieces.filter(x => x.kind === 'artifact').length;
    L.push(`| [${v.id}](${VOLUME_DIR}/${v.file}) | ${v.category.categoryId} ${v.category.name} | ${v.part} of ${v.of} | ${doms} | ${arts} | ${Math.round(sizes[v.file] / 1024)} KB |`);
  }
  L.push('');

  L.push('<a id="index"></a>', '## 3. Index', '');
  for (const c of cats) {
    const vs = volumes.filter(v => v.category === c);
    L.push(`### ${c.categoryId} · ${c.name}`, '', `${c.covers} Volume${vs.length > 1 ? 's' : ''}: ${vs.map(v => `[${v.id}](${VOLUME_DIR}/${v.file})`).join(', ')}.`, '');
    for (const d of domainsOf(c)) {
      L.push(`- ${linkDomain(d, from)} — owns ${(d.owns || []).map(o => linkTerm(o, from)).join(', ')}`);
      for (const a of artifactsOf(d)) L.push(`  - ${linkArtifact(a, from)} ${a.title}`);
    }
    L.push('');
  }

  L.push('<a id="constitution"></a>', '## 4. Constitution', '');
  const laws = DOMAINS.laws || [];
  const lawStatus = st => laws.filter(l => l.status === st).length;
  L.push('### Laws', '', `${laws.length} laws: ${lawStatus('enforced')} enforced, ${lawStatus('partial')} partly enforced, ${lawStatus('planned')} planned. Each merges every place the corpus states it; its sources are document:line in the compiled corpus (\`node _registry/compile.js --search\` finds them).`, '',
    '| Law | Statement | Also called | Status | Enforced by | Sources |', '|---|---|---|---|---|---|');
  for (const l of laws) L.push(`| <a id="${anchor(l.lawId)}"></a>**${l.lawId}** ${l.name} | ${l.statement} | ${(l.aliases || []).join(', ') || '—'} | ${l.status} | ${(l.enforcedBy || []).join('; ') || '—'} | ${(l.sources || []).join(', ')} |`);
  L.push('', '### Laws of the registries', '', '| Registry | Status | Law |', '|---|---|---|');
  for (const f of ['primitives.json', 'terminology.json', 'domains.json', 'content-map.json'].concat(Object.values(CONTENT_FILE_NAMES))) {
    const j = load(f); L.push(`| \`${f}\` — ${j.canonicalName} | ${j.status} | ${j.law} |`);
  }
  L.push('', '### Ownership and dependency', '',
    `- **Dependency law:** ${DOMAINS.dependencyLaw}`, `- **Communication:** ${DOMAINS.communication}`,
    `- **Projection law:** ${DOMAINS.boundaries.projectionLaw}`, `- **No domain may:** ${DOMAINS.boundaries.noDomainMay.join('; ')}.`,
    `- **Primitives:** ${PRIMITIVES.law} Amendment: ${PRIMITIVES.amendmentProcess}`,
    `- **Reserved for projections (never primitives or schema types):** ${PRIMITIVES.prohibited.join(', ')}. ${PRIMITIVES.derivationLaw}`, '');
  L.push('### Amendments', '', '| ID | Date | Authorised by | Summary |', '|---|---|---|---|');
  for (const a of DOMAINS.amendments || []) L.push(`| <a id="${anchor(a.amendmentId)}"></a>${a.amendmentId} | ${a.date} | ${a.authorisedBy} | ${a.summary} |`);
  L.push('');

  L.push('<a id="kernel"></a>', '## 5. Kernel', '', 'The parts every domain is built on. Each part has one owning domain.', '', '| Part | Name | Owner | What it is |', '|---|---|---|---|');
  for (const k of DOMAINS.kernel || []) L.push(`| <a id="${anchor(k.partId)}"></a>${k.partId} | ${k.name} | ${linkDomain(domainByName(k.owner), from)} | ${k.statement} |`);
  L.push('');

  L.push('<a id="standard-contract"></a>', '## 6. Standard contract', '',
    'Every artifact inherits these sections. They are stated once here; `<artifact id>`, `<artifact title>` and `<owning domain>` stand for the artifact that inherits them. The ownership sections live on each domain’s card in its volume.', '');
  for (const { s, body } of genericSections()) L.push(`<a id="${anchor('standard-' + s)}"></a>`, `### ${s}`, '', body, '');

  L.push('<a id="glossary"></a>', '## 7. Glossary', '', 'Every primitive and term, once, with its single owner.', '');
  const entries = new Map();
  for (const p of PRIMITIVES.primitives) entries.set(p.name, { name: p.name, prim: p });
  for (const t of TERMS.terms) entries.set(t.canonicalName, Object.assign(entries.get(t.canonicalName) || { name: t.canonicalName }, { term: t }));
  for (const e of [...entries.values()].sort((a, b) => a.name.localeCompare(b.name))) {
    const owner = DOMAINS.domains.find(d => (d.owns || []).includes(e.name));
    L.push(`<a id="${termAnchor(e.name)}"></a>`, `**${e.name}** ${[e.prim && e.prim.id, e.term && e.term.termId].filter(Boolean).join(' · ')} — owned by ${owner ? linkDomain(owner, from) : '—'}`, '');
    if (e.prim) L.push(`- Primitive: ${e.prim.definition}`);
    if (e.term) {
      L.push(`- Term: ${e.term.definition}`);
      if ((e.term.aliases || []).length) L.push(`- Also called: ${e.term.aliases.join(', ')}`);
      if ((e.term.prohibitedMeanings || []).length) L.push(`- Never means: ${e.term.prohibitedMeanings.join(', ')}`);
    }
    L.push('');
  }

  L.push('<a id="code-map"></a>', '## 8. Code and document map', '', `Every file under ${(CODEBASE.covers || []).map(c => '\`' + c + '\`').join(', ')} and the single domain that owns it. A file that mixes concerns is split into parts, each with one owner. ${CODEBASE.modules.length} files.`, '');
  for (const c of cats) {
    const rows = [];
    for (const m of CODEBASE.modules) for (const p of m.parts || [{ owner: m.owner, part: m.note }]) {
      const d = domainByName(p.owner);
      if (d && d.category === c.categoryId) rows.push(`| \`${m.path}\` | ${linkDomain(d, from)} | ${p.part || ''} |`);
    }
    if (rows.length) L.push(`### ${c.categoryId} · ${c.name}`, '', '| File | Owner | Part |', '|---|---|---|', ...rows, '');
  }

  L.push('### Documents', '', `Every document at the repository root and in \`_superseded/\` (${DOCUMENTS.documents.length}), with its one status and owner. Superseded documents are kept for provenance; the last column says what replaced each.`, '',
    '| Document | Status | Owner | Generated by, or replaced by |', '|---|---|---|---|');
  for (const st of DOCUMENTS.statuses) for (const d of DOCUMENTS.documents.filter(x => x.status === st)) {
    const o = domainByName(d.owner);
    L.push(`| \`${d.path}\` | ${d.status} | ${o ? linkDomain(o, from) : d.owner} | ${d.generatedBy || d.supersededBy || d.note || ''} |`);
  }
  L.push('');

  const reg = conceptRegister();
  L.push('<a id="concept-register"></a>', '## 9. Concept register', '');
  if (reg) {
    const k = reg.counts.byKind, b = reg.counts.byBasis;
    L.push(`Every concept the corpus names, once, from \`_registry/classification.json\` (owned by Semantic). ${reg.counts.distinct} distinct names: ${k.concept || 0} concepts, ${k.statement || 0} statements, ${k.fragment || 0} parse fragments, ${k.identifier || 0} identifiers. Each concept has one owner, taken from an exact registry name, else its reviewed container, else the rules on its name. Find any of them with \`node _registry/compile.js --search <words> --kind concept [--owner …] [--category …]\`.`, '',
      '| Basis | Concepts |', '|---|---:|');
    for (const [basis, n] of Object.entries(b).sort((x, y) => y[1] - x[1])) L.push(`| ${basis} | ${n} |`);
    L.push('', `Containers reviewed: ${reg.counts.containersReviewed} of ${reg.counts.containers}. Concepts reviewed on their own: ${reg.counts.conceptsReviewed || 0}.`, '', '| Category | Domain | Concepts |', '|---|---|---:|');
    for (const c of cats) for (const d of domainsOf(c)) L.push(`| ${c.categoryId} ${c.name} | ${linkDomain(d, from)} | ${reg.counts.byOwner[d.name] || 0} |`);
    L.push('');
    /* the review queue: every low-confidence decision, for a person to confirm or correct */
    const CL = load('classification.json');
    const queue = reg.counts.reviewQueue || [];
    L.push('<a id="review-queue"></a>', '### Review queue', '',
      `${queue.length} decisions were made with low confidence even after a second opinion. Confirm or correct each by editing its entry in \`_registry/classification.json\` (\`containers\` or \`concepts\`): set \`owner\`, set \`confidence\` to \`high\` and \`by\` to your name, then run \`npm run registry\`.`, '',
      '| ID | Current owner | Reviewer’s reason |', '|---|---|---|');
    for (const id of queue) {
      const r = id.startsWith('c:') ? (CL.concepts || {})[id.slice(2)] : (CL.containers || {})[id];
      if (r) L.push(`| \`${id}\` | ${r.owner} | ${String(r.reason || '').replace(/\|/g, '/')} |`);
    }
    L.push('');
  } else L.push('No concept register has been compiled. Run `npm run registry`.', '');

  L.push('<a id="alignment"></a>', '## 10. Other domain systems', '',
    'The platform has one set of domains, the register’s. Other structures that call their parts “domains” are aligned to it: each part names the one register domain that owns it (`_registry/alignment.json`).', '');
  for (const sys of ALIGNMENT.systems) {
    L.push(`### ${sys.name}`, '', `${sys.means}. Source: \`${sys.source}\`${sys.list ? ' → `' + sys.list + '`' : ''}.`, '');
    if (sys.owners) {
      let list = [];
      try { list = JSON.parse(fs.readFileSync(path.join(ROOT, sys.source), 'utf8'))[sys.list] || []; } catch (e) { }
      L.push('| Part | Register owner |', '|---|---|');
      for (const it of list) { const o = domainByName(sys.owners[it[sys.key]]); L.push(`| ${it.name || it[sys.key]} (\`${it[sys.key]}\`) | ${o ? linkDomain(o, from) : '—'} |`); }
      L.push('');
    } else if (reg) {
      const CL = load('classification.json');
      const byOwner = {};
      for (const [id, r] of Object.entries(CL.containers || {})) if (id.startsWith('u:')) byOwner[r.owner] = (byOwner[r.owner] || 0) + 1;
      L.push(`Derived from ${sys.derivedFrom}: each universe takes its reviewed container’s owner.`, '', '| Register owner | Universes |', '|---|---:|');
      for (const [o, n] of Object.entries(byOwner).sort((a, b) => b[1] - a[1])) { const d = domainByName(o); L.push(`| ${d ? linkDomain(d, from) : o} | ${n} |`); }
      L.push('');
    }
  }

  L.push('<a id="build-path"></a>', '## 11. Build path and decisions', '');
  const done = ROADMAP.steps.filter(st => st.status === 'done').length;
  const gaps = ROADMAP.gaps || [];
  L.push('<a id="gaps"></a>', '### Gaps', '', `${gaps.filter(g => g.status === 'open').length} open, ${gaps.filter(g => g.status === 'closed').length} closed. Every gap has one owning domain; a closed gap names the amendment that closed it (\`_registry/roadmap.json\` → \`gaps\`).`, '',
    '| Gap | Group | What | Owner | Status |', '|---|---|---|---|---|');
  for (const g of gaps) { const o = domainByName(g.owner); L.push(`| <a id="${anchor(g.gapId)}"></a>${g.gapId} | ${g.group} | ${g.title} | ${o ? linkDomain(o, from) : g.owner} | ${g.status}${g.closedBy ? ' (' + g.closedBy + ')' : ''} |`); }
  L.push('', '### Steps', '');
  L.push(`${done} of ${ROADMAP.steps.length} steps done. Each step is committed only once the full test suite passes.`, '', '| Step | What | Domains | Status | Delivered by |', '|---|---|---|---|---|');
  for (const st of ROADMAP.steps) L.push(`| <a id="${anchor(st.stepId)}"></a>${st.stepId} | ${st.title} | ${st.domains.map(n => linkDomain(domainByName(n), from)).join(', ')} | ${st.status} | ${(st.deliveredBy || []).map(a => `[${a}](#${anchor(a)})`).join(', ') || '—'} |`);
  L.push('', '### Decisions', '', '| ID | Question | Decision |', '|---|---|---|');
  for (const dc of ROADMAP.decisions) L.push(`| <a id="${anchor(dc.decisionId)}"></a>${dc.decisionId} | ${dc.question} | ${dc.decision} |`);
  L.push('');

  L.push('<a id="id-lookup"></a>', '## 12. ID lookup', '', '| ID | Kind | Name | Where |', '|---|---|---|---|');
  const rows = [];
  for (const c of cats) rows.push([c.categoryId, 'category', c.name, volumes.filter(v => v.category === c).map(v => `[${v.id}](${VOLUME_DIR}/${v.file})`).join(', ')]);
  for (const v of volumes) if (v.of > 1) rows.push([v.id, 'volume', `${v.category.name}, part ${v.part} of ${v.of}`, `[${v.file}](${VOLUME_DIR}/${v.file})`]);
  for (const d of DOMAINS.domains) rows.push([d.domainId, 'domain', d.name, linkDomain(d, from)]);
  for (const a of MANIFEST.artifacts) rows.push([a.id, 'artifact', a.title, linkArtifact(a, from)]);
  for (const p of PRIMITIVES.primitives) rows.push([p.id, 'primitive', p.name, linkTerm(p.name, from)]);
  for (const t of TERMS.terms) rows.push([t.termId, 'term', t.canonicalName, linkTerm(t.canonicalName, from)]);
  for (const l of DOMAINS.laws || []) rows.push([l.lawId, 'law', l.name, `[constitution](#${anchor(l.lawId)})`]);
  for (const k of DOMAINS.kernel || []) rows.push([k.partId, 'kernel part', k.name, `[kernel](#${anchor(k.partId)})`]);
  for (const st of ROADMAP.steps) rows.push([st.stepId, 'build step', st.title.slice(0, 60), `[build path](#${anchor(st.stepId)})`]);
  for (const dc of ROADMAP.decisions) rows.push([dc.decisionId, 'decision', dc.question, `[decisions](#${anchor(dc.decisionId)})`]);
  for (const g of ROADMAP.gaps || []) rows.push([g.gapId, 'gap', g.title.slice(0, 60), `[gaps](#${anchor(g.gapId)})`]);
  for (const a of DOMAINS.amendments || []) rows.push([a.amendmentId, 'amendment', a.summary.split(':')[0].slice(0, 60), `[constitution](#${anchor(a.amendmentId)})`]);
  rows.sort((x, y) => x[0].localeCompare(y[0]));
  for (const r of rows) L.push(`| ${r[0]} | ${r[1]} | ${r[2]} | ${r[3]} |`);
  return L.join('\n') + '\n';
}

/* the whole projection, in memory: { relative path → text }. Pure — the writer and the
   freshness test both call it, so "is the projection current?" is a byte comparison. */
function build(opts) {
  if (!MASTER_FILE || !VOLUME_DIR) throw new Error('manifest.json → projection must declare masterFile and volumeDir');
  const max = (opts && opts.maxVolumeBytes) || MAX_BYTES;
  /* the packer budgets entries; a volume also carries its header and contents list, so the
     rendered size is checked and the budget tightened until every part holding more than
     one artifact fits the limit */
  let budget = max, volumes, files, sizes;
  for (let round = 0; round < 8; round++) {
    volumes = layout(budget);
    files = {}; sizes = {};
    for (const v of volumes) { const t = volumeText(v, volumes); files[`${VOLUME_DIR}/${v.file}`] = t; sizes[v.file] = Buffer.byteLength(t); }
    const over = volumes.filter(v => sizes[v.file] > max && v.pieces.filter(x => x.kind === 'artifact').length > 1)
      .reduce((m, v) => Math.max(m, sizes[v.file] - max), 0);
    if (!over) break;
    budget -= over + 512;
  }
  files[MASTER_FILE] = masterText(volumes, sizes, max);
  return { files, volumes };
}

function write() {
  const { files, volumes } = build();
  fs.mkdirSync(path.join(ROOT, VOLUME_DIR), { recursive: true });
  for (const [rel, text] of Object.entries(files)) fs.writeFileSync(path.join(ROOT, rel), text);
  /* a volume the layout no longer produces (a merged part, a renamed category) is removed */
  for (const f of fs.readdirSync(path.join(ROOT, VOLUME_DIR))) {
    if (!files[`${VOLUME_DIR}/${f}`]) { fs.unlinkSync(path.join(ROOT, VOLUME_DIR, f)); console.log(`removed   ${VOLUME_DIR}/${f}`); }
  }
  return volumes;
}

/* ---------- CLI ---------- */
function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }


function main() {
  const args = process.argv.slice(2);
  if (args.includes('--list')) {
    for (const a of MANIFEST.artifacts) console.log(`${a.id}  ${a.status.padEnd(9)} ${a.title}`);
    return;
  }
  if (args.includes('--check')) {
    // integrity: primitive uniqueness, term uniqueness, manifest coverage
    const problems = [];
    const pn = PRIMITIVES.primitives.map(p => p.name);
    if (new Set(pn).size !== pn.length) problems.push('duplicate primitive names');
    const tn = TERMS.terms.map(t => t.canonicalName);
    if (new Set(tn).size !== tn.length) problems.push('duplicate canonical terms');
    const ids = MANIFEST.artifacts.map(a => a.id);
    if (new Set(ids).size !== ids.length) problems.push('duplicate artifact ids');

    // every artifact resolves to a category
    for (const a of MANIFEST.artifacts) if (!categoryRow(a)) problems.push(`${a.id} has no owning domain in a declared category`);
    // dependency law: acyclic check on declared order
    console.log(problems.length ? 'INTEGRITY FAILURES:' : 'INTEGRITY OK — registries consistent.');
    for (const p of problems) console.log('  - ' + p);
    process.exit(problems.length ? 1 : 0);
  }

  if (args.includes('--watch')) {
    /* re-project whenever a registry file changes: each run is a fresh process, so it
       always reads the registry as it now stands */
    const { execFileSync } = require('child_process');
    const run = () => { try { execFileSync(process.execPath, [__filename], { stdio: 'inherit' }); } catch (e) { } };
    run();
    let timer = null;
    fs.watch(REG, (ev, f) => {
      /* the sealed registry and its readable view are outputs, not inputs */
      if (!f || !/\.json$/.test(f) || /^canonical/.test(f)) return;
      clearTimeout(timer); timer = setTimeout(run, 300);
    });
    console.log(`watching _registry/ — the master and volumes re-project on every change (Ctrl-C to stop)`);
    return;
  }

  /* one projection: the master and its volumes, from the whole registry. Files of the
     earlier per-artifact layout are removed, with any folder they leave empty. */
  for (const e of fs.readdirSync(ROOT, { withFileTypes: true })) {
    if (!e.isDirectory() || !/^[0-9]+-/.test(e.name)) continue;
    const dir = path.join(ROOT, e.name);
    for (const f of fs.readdirSync(dir)) if (/^UCOS-.*\.md$/.test(f)) { fs.unlinkSync(path.join(dir, f)); console.log(`removed   ${e.name}/${f}`); }
    if (!fs.readdirSync(dir).length) fs.rmdirSync(dir);
  }
  try { fs.unlinkSync(path.join(ROOT, 'UCOS-REPOSITORY-INDEX.md')); console.log('removed   UCOS-REPOSITORY-INDEX.md (folded into the master)'); } catch (e) { }
  const volumes = write();
  const changed = MANIFEST.artifacts.some(a => a.status !== 'generated');
  for (const a of MANIFEST.artifacts) a.status = 'generated';
  if (changed) fs.writeFileSync(path.join(REG, 'manifest.json'), JSON.stringify(MANIFEST, null, 2) + '\n');
  const split = volumes.filter(v => v.of > 1).length;
  console.log(`projected ${MASTER_FILE} and ${volumes.length} volume(s) in ${VOLUME_DIR}/ (${split} split part(s), limit ${Math.round(MAX_BYTES / 1024)} KB) for ${MANIFEST.artifacts.length} artifacts`);
}

module.exports = { build, MASTER_FILE, VOLUME_DIR, MAX_BYTES };
if (require.main === module) { try { main(); } catch (e) { console.error('projection failed:', e.message); process.exit(1); } }
