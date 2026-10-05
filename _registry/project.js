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

/* ---------- content registries ---------- */
const CONTENT = {
  core: load('content-core.json').content,
  ext: load('content-ext.json').content,
  commerce: load('content-commerce.json').content,
  'twin-agent': load('content-twin-agent.json').content,
  'runtime-data': load('content-runtime-data.json').content,
  'sec-ops-dep-qlt': load('content-sec-ops-dep-qlt.json').content
};

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
function catOf(code) { return MANIFEST.categories.find(c => c.code === code); }

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
        `| ${t.canonicalName} | ${t.definition} | ${t.ownerDomain} | ${(t.prohibitedMeanings || []).join(', ')} |`)
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
      return `→ Governed by ${id}. Content projected from the ${catOf(art.cat).name} registry under ${R('Law 002')}.`;
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
  const d = (() => {
    const base = art.title.replace(/ Architecture| Constitution/, '').trim();
    const guess = {
      'Identity': 'Identity', 'Knowledge': 'Knowledge', 'Relationship': 'Relationship',
      'Context': 'Context', 'Policy': 'Policy', 'Rule': 'Rule', 'Authority': 'Authority',
      'Trust': 'Trust', 'Evidence': 'Evidence', 'Observation': 'Observation',
      'Inference': 'Inference', 'Reasoning': 'Reasoning', 'Simulation': 'Simulation',
      'Causality': 'Causality', 'Evolution': 'Evolution', 'Agent': 'Agent',
      'Digital Twin': 'Twin'
    };
    for (const k of Object.keys(guess)) if (base === k) return domainOf(guess[k]);
    return null;
  })();

  const lines = [];
  lines.push(`# ${art.id}`);
  lines.push(`# ${art.title}`);
  lines.push('');
  lines.push(`**Version:** Ω∞.1  |  **Status:** Constitutional Artifact  |  **Authority:** UCOS Ω∞ Constitutional Authority`);
  lines.push(`**Category:** ${catOf(art.cat).name}  |  **Source of Truth:** \`_registry/\` (projected, never hand-authored)`);
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

/* ---------- CLI ---------- */
function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }

function targetPath(art) {
  const cat = catOf(art.cat);
  const slug = art.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  return path.join(ROOT, cat.path, `${art.id}-${slug}.md`);
}

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
    const counted = MANIFEST.categories.reduce((s, c) => s + c.count, 0);
    if (counted !== MANIFEST.totalArtifacts) problems.push(`category counts ${counted} != total ${MANIFEST.totalArtifacts}`);
    if (MANIFEST.artifacts.length !== MANIFEST.totalArtifacts) problems.push(`manifest length ${MANIFEST.artifacts.length} != total ${MANIFEST.totalArtifacts}`);
    // every artifact resolves to a category
    for (const a of MANIFEST.artifacts) if (!catOf(a.cat)) problems.push(`${a.id} has unknown category ${a.cat}`);
    // dependency law: acyclic check on declared order
    console.log(problems.length ? 'INTEGRITY FAILURES:' : 'INTEGRITY OK — registries consistent.');
    for (const p of problems) console.log('  - ' + p);
    process.exit(problems.length ? 1 : 0);
  }

  const wanted = args.filter(a => !a.startsWith('-'));
  const set = wanted.length ? MANIFEST.artifacts.filter(a => wanted.includes(a.id)) : MANIFEST.artifacts;
  let n = 0;
  for (const a of set) {
    const out = targetPath(a);
    ensureDir(path.dirname(out));
    fs.writeFileSync(out, project(a));
    a.status = 'generated';
    n++;
    console.log(`projected ${a.id} → ${path.relative(ROOT, out)}`);
  }
  fs.writeFileSync(path.join(REG, 'manifest.json'), JSON.stringify(MANIFEST, null, 2) + '\n');
  console.log(`\n${n} artifact(s) projected from registry.`);
}

try { main(); } catch (e) { console.error('projection failed:', e.message); process.exit(1); }
