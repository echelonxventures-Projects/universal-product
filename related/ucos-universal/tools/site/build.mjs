import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync, statSync, rmSync } from 'node:fs';
import { join, dirname, relative, posix } from 'node:path';
import { Marked } from 'marked';

const REPO = new URL('../../', import.meta.url).pathname.replace(/\/$/, '');
const OUTDIR = process.argv[2];               // scratchpad/site
const GH = 'https://github.com/echelonxventures-Projects/UCOS-UNIVERSAL/blob/main/';
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const slug = t => t.toLowerCase().replace(/<[^>]+>/g, '').replace(/&amp;/g, '&')
  .replace(/[^\p{L}\p{N}\s_-]/gu, '').trim().replace(/\s/g, '-');

// ---------------------------------------------------------------- collect documents
const docs = [];   // {src, key, group, label, title}
const add = (src, key, group) => {
  const md = readFileSync(join(REPO, src), 'utf8');
  const h1 = (md.match(/^# (.+)$/m) || [, key])[1].replace(/`/g, '');
  let label = h1;
  const u = h1.match(/^(U\d+) — (.*?)( Universe)? Constitution$/);
  if (u) label = `${u[1]} ${u[2]}`;
  label = label.replace(/^UCOS — /, '').replace(/^TM-[A-Z-]+ — /, '').replace(/^Runbook — /, 'Runbook: ').replace(/ \(template\)$/, '');
  const adr = h1.match(/^ADR-(\d+): (.*)$/);
  if (adr) label = `${adr[1]} ${adr[2]}`;
  docs.push({ src, key, group, label, title: h1 });
};
add('constitutions/README.md', 'universes', 'Overview');
add('constitutions/COVERAGE-REGISTER.md', 'coverage-register', 'Overview');
add('constitutions/TEMPORAL-BINDING-MATRIX.md', 'temporal-binding-matrix', 'Overview');
add('constitutions/INDUSTRY-PRODUCT-DOMAIN-CATALOGUE.md', 'industry-catalogue', 'Overview');
add('spec/README.md', 'spec', 'Overview');
for (const f of readdirSync(join(REPO, 'engineering')).filter(f => f.endsWith('.md')).sort())
  add(`engineering/${f}`, 'engineering-' + f.replace('.md', '').toLowerCase(), 'Engineering');
const uni = readdirSync(join(REPO, 'constitutions')).filter(d => /^U\d+-/.test(d) && existsSync(join(REPO, 'constitutions', d, 'constitution.md')))
  .sort((a, b) => parseInt(a.slice(1)) - parseInt(b.slice(1)));
for (const d of uni) add(`constitutions/${d}/constitution.md`, d, 'Universes');
add('docs/adr/README.md', 'adr', 'Decisions');
for (const f of readdirSync(join(REPO, 'docs/adr')).filter(f => /^ADR-\d+/.test(f)).sort()) add(`docs/adr/${f}`, f.replace('.md', ''), 'Decisions');
add('docs/threat-models/README.md', 'threat-models', 'Threat models');
for (const f of readdirSync(join(REPO, 'docs/threat-models')).filter(f => f.endsWith('.md') && f !== 'README.md').sort())
  add(`docs/threat-models/${f}`, 'tm-' + f.replace('.md', ''), 'Threat models');
for (const f of ['COST-MODEL.md', 'COMMERCIAL-MODEL.md', 'TEAM-AND-ROADMAP-PLAN.md', 'VALIDATION-PLAN.md'])
  add(`business/${f}`, 'business-' + f.replace('.md', '').toLowerCase(), 'Business');
for (const f of readdirSync(join(REPO, 'business/legal')).filter(f => f.endsWith('.md')).sort())
  add(`business/legal/${f}`, 'legal-' + f.replace('.md', '').toLowerCase(), 'Business');
add('docs/runbooks/README.md', 'runbooks', 'Operations');
for (const f of readdirSync(join(REPO, 'docs/runbooks')).filter(f => f.endsWith('.md') && f !== 'README.md').sort())
  add(`docs/runbooks/${f}`, 'runbook-' + f.replace('.md', ''), 'Operations');
add('CONTRIBUTING.md', 'contributing', 'Overview');
const bySrc = Object.fromEntries(docs.map(d => [d.src, d]));

// ---------------------------------------------------------------- markdown renderer
function makeMarked(srcPath, fromDocs) {
  const used = new Set();
  const toc = [];
  const m = new Marked({ gfm: true });
  m.use({ renderer: {
    heading({ tokens, depth }) {
      const text = this.parser.parseInline(tokens);
      let id = slug(text), n = 1; const base = id;
      while (used.has(id)) id = `${base}-${n++}`;
      used.add(id);
      if (depth === 2) toc.push({ id, text });
      return `<h${depth} id="${id}">${text}</h${depth}>\n`;
    },
    code({ text, lang }) {
      if (lang === 'mermaid') return `<figure class="diagram"><pre class="mermaid">${esc(text)}</pre></figure>\n`;
      const boxy = (!lang || lang === 'text') && /[┌╔═│─▓]/.test(text);
      const label = lang && lang !== 'text' ? `<span class="lang">${esc(lang)}</span>` : '';
      return `<div class="block${boxy ? ' wire' : ''}">${label}<pre><code>${esc(text)}</code></pre></div>\n`;
    },
    table(token) {
      const head = token.header.map(c => `<th>${this.parser.parseInline(c.tokens)}</th>`).join('');
      const rows = token.rows.map(r => `<tr>${r.map(c => `<td>${this.parser.parseInline(c.tokens)}</td>`).join('')}</tr>`).join('\n');
      return `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>\n`;
    },
    link({ href, title, tokens }) {
      const text = this.parser.parseInline(tokens);
      let out = href;
      if (!/^[a-z]+:|^#/.test(href)) {
        const [p, hash] = href.split('#');
        const target = posix.normalize(posix.join(posix.dirname(srcPath), p)).replace(/\/$/, '');
        const d = bySrc[target] || bySrc[target + '/README.md'] || bySrc[target + '/constitution.md'];
        if (d) out = (fromDocs ? '' : 'docs/') + d.key + '.html' + (hash ? '#' + hash : '');
        else out = GH + target;
      }
      const ext = /^https?:/.test(out) ? ' target="_blank" rel="noopener"' : '';
      return `<a href="${esc(out)}"${title ? ` title="${esc(title)}"` : ''}${ext}>${text}</a>`;
    }
  }});
  return { m, toc };
}

// ---------------------------------------------------------------- shared style
const tpl = readFileSync(new URL('./template.html', import.meta.url), 'utf8');
const style = tpl.slice(tpl.indexOf('<style>'), tpl.indexOf('</style>') + 8);
const fonts = tpl.slice(tpl.indexOf('<link rel="preconnect"'), tpl.indexOf('<style>'));
const extraCss = `<style>
:root { padding-block: env(safe-area-inset-top, 0px) env(safe-area-inset-bottom, 0px); }
.crumbs { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; padding-top: 28px; font: 600 12px/1.4 var(--font-mono); letter-spacing: .04em; text-transform: uppercase; color: var(--muted); }
.crumbs a { color: var(--accent); text-decoration: none; }
.doc > h1 { margin: 14px 0 18px; font: 800 clamp(30px, 4.4vw, 46px)/1.05 var(--font-display); font-stretch: 80%; letter-spacing: -.01em; text-wrap: balance; }
.toc a.current { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
.pager { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; margin-top: 56px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 14px; }
.pager a { text-decoration: none; }
.lib { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 1fr)); gap: 28px 32px; margin-top: 24px; }
.lib section { min-width: 0; }
.lib h2 { margin: 0 0 8px; padding: 0; border: 0; font: 700 13px/1.3 var(--font-body); text-transform: uppercase; letter-spacing: .08em; color: var(--muted); }
.lib ul { list-style: none; margin: 0; padding: 0; font-size: 15px; }
.lib li + li { margin-top: 2px; }
.lib a { text-decoration: none; }
.lib .n { font-family: var(--font-mono); font-size: 12px; color: var(--muted); margin-right: 6px; }
.lib-panel { margin-top: 28px; padding: 18px 20px; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; max-width: 760px; }
.lib-panel h2 { margin: 0 0 6px; padding: 0; border: 0; font: 700 13px/1.3 var(--font-body); text-transform: uppercase; letter-spacing: .08em; color: var(--muted); }
.lib-panel p { margin: 0 0 10px; font-size: 15px; }
.lib-panel ul { display: flex; flex-wrap: wrap; gap: 6px 18px; list-style: none; margin: 0; padding: 0; font-size: 15px; }
.lib-panel li + li { margin-top: 0; }
</style>`;
const groups = ['Overview', 'Engineering', 'Universes', 'Decisions', 'Threat models', 'Operations', 'Business'];
function libNav(prefix, currentKey, masterHref) {
  let s = `<li class="nav-part">Start</li>\n<li><a href="${masterHref}"><span class="n">◆</span>Master architecture</a></li>\n<li><a href="${prefix}library.html"${currentKey === 'library' ? ' class="current" aria-current="page"' : ''}><span class="n">≡</span>Library index</a></li>\n`;
  for (const g of groups) {
    s += `<li class="nav-part">${g}</li>\n`;
    for (const d of docs.filter(d => d.group === g)) {
      const m = d.label.match(/^(U\d+|\d{3}) (.*)$/);
      const lab = m ? `<span class="n">${m[1].replace(/^U/, '')}</span>${esc(m[2])}` : esc(d.label);
      s += `<li><a href="${prefix}${d.key}.html"${d.key === currentKey ? ' class="current" aria-current="page"' : ''}>${lab}</a></li>\n`;
    }
  }
  return s;
}
const filterScript = `<script>
(function () {
  var input = document.getElementById('toc-filter');
  if (input) input.addEventListener('input', function () {
    var q = input.value.trim().toLowerCase();
    document.querySelectorAll('#toc li').forEach(function (li) {
      if (li.classList.contains('nav-part')) { li.hidden = q !== ''; return; }
      li.hidden = q !== '' && li.textContent.toLowerCase().indexOf(q) === -1;
    });
  });
  var cur = document.querySelector('#toc a.current');
  if (cur) cur.scrollIntoView({ block: 'center' });
})();
</script>`;
const mermaidScript = `<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
<script>
(function () {
  if (!window.mermaid) return;
  var root = document.documentElement, t = root.getAttribute('data-theme');
  var dark = t === 'dark' || (t !== 'light' && window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
  mermaid.initialize({ startOnLoad: false, theme: dark ? 'dark' : 'neutral', securityLevel: 'strict' });
  mermaid.run({ querySelector: 'pre.mermaid', suppressErrors: true });
})();
</script>`;
function page({ title, key, bodyHtml, hasMermaid, prev, next }) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(title)} · UCOS</title>
${fonts}${style}
${extraCss}
</head>
<body>
<aside class="rail" aria-label="Library">
  <div class="brand">UCOS Ω∞<small>Specification library</small></div>
  <div class="filter"><input id="toc-filter" type="search" placeholder="Filter documents" aria-label="Filter documents"></div>
  <ol class="toc" id="toc">
${libNav('', key, '../index.html')}
  </ol>
</aside>
<main>
  <article class="doc">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">UCOS master</a><span>/</span><a href="library.html">Library</a></nav>
${bodyHtml}
    <nav class="pager" aria-label="Previous and next">${prev ? `<a href="${prev.key}.html">← ${esc(prev.label)}</a>` : '<span></span>'}${next ? `<a href="${next.key}.html">${esc(next.label)} →</a>` : ''}</nav>
    <p class="foot">Rendered from the UCOS repository · source <code>${esc(key === 'library' ? 'docs/' : (docs.find(d => d.key === key) || {}).src || '')}</code></p>
  </article>
</main>
${filterScript}
${hasMermaid ? mermaidScript : ''}
</body>
</html>
`;
}

// ---------------------------------------------------------------- render docs
if (existsSync(join(OUTDIR, 'docs'))) rmSync(join(OUTDIR, 'docs'), { recursive: true });
mkdirSync(join(OUTDIR, 'docs'), { recursive: true });
let mer = 0;
docs.forEach((d, i) => {
  const md = readFileSync(join(REPO, d.src), 'utf8');
  const { m } = makeMarked(d.src, true);
  const html = m.parse(md);
  const hasMermaid = html.includes('class="mermaid"');
  if (hasMermaid) mer++;
  writeFileSync(join(OUTDIR, 'docs', d.key + '.html'), page({ title: d.label, key: d.key, bodyHtml: html, hasMermaid, prev: docs[i - 1], next: docs[i + 1] }));
});
// library index
let lib = `<h1>Specification library</h1>\n<p>Every companion document of the master architecture: ${uni.length} universe constitutions, the coverage and temporal registers, engineering designs, ${docs.filter(d => d.group === 'Decisions').length - 1} architecture decisions, ${docs.filter(d => d.group === 'Threat models').length - 1} threat models and the business pack. Machine-readable files (schemas, manifests, rules) live in the repository and are linked from the pages that describe them.</p>\n<div class="lib">\n`;
for (const g of groups) {
  lib += `<section><h2>${g}</h2><ul>\n`;
  for (const d of docs.filter(d => d.group === g)) {
    const m = d.label.match(/^(U\d+|\d{3}) (.*)$/);
    lib += `<li><a href="${d.key}.html">${m ? `<span class="n">${m[1]}</span>${esc(m[2])}` : esc(d.label)}</a></li>\n`;
  }
  lib += `</ul></section>\n`;
}
lib += `</div>\n`;
writeFileSync(join(OUTDIR, 'docs', 'library.html'), page({ title: 'Specification library', key: 'library', bodyHtml: lib, hasMermaid: false }));

// ---------------------------------------------------------------- master page (index)
let mmd = readFileSync(join(REPO, 'UCOS-MASTER-ARCHITECTURE.md'), 'utf8');
const version = (mmd.match(/\| Version \| ([\d.]+) \((\d+) amendments/) || []);
mmd = mmd.slice(mmd.indexOf('# PART I — FOUNDATIONS'));
const toc = []; const used = new Set();
const mm = makeMarked('UCOS-MASTER-ARCHITECTURE.md', false).m;
mm.use({ renderer: {
  heading({ tokens, depth }) {
    const text = this.parser.parseInline(tokens);
    let id = slug(text), n = 1; const base = id;
    while (used.has(id)) id = `${base}-${n++}`;
    used.add(id);
    if (depth === 1) toc.push({ part: true, id, text });
    if (depth === 2) toc.push({ part: false, id, text });
    if (depth === 1) {
      const m = text.match(/^PART ([IVX]+) — (.*)$/);
      if (m) return `<header class="part" id="${id}"><span class="part-no">Part ${m[1]}</span><h1>${m[2]}</h1></header>\n`;
    }
    return `<h${depth} id="${id}">${text}</h${depth}>\n`;
  }
}});
// turn backticked repo paths into links on the master page
const body = mm.parse(mmd).replace(/<code>((?:constitutions|engineering|docs|business|spec)\/[^<]*?)<\/code>/g, (all, p) => {
  const clean = p.replace(/\/$/, '');
  const d = bySrc[clean] || bySrc[clean + '/README.md'];
  return d ? `<a href="docs/${d.key}.html"><code>${p}</code></a>` : all;
});
let nav = '';
for (const t of toc) {
  if (t.part) { const m = t.text.match(/^PART ([IVX]+) — (.*)$/); nav += `<li class="nav-part">${m ? `<span>Part ${m[1]}</span> ${m[2]}` : t.text}</li>\n`; }
  else { const m = t.text.match(/^(\d+)\.\s+(.*)$/); nav += `<li><a href="#${t.id}">${m ? `<span class="n">${m[1]}</span>${m[2]}` : t.text}</a></li>\n`; }
}
nav += `<li class="nav-part">Library</li>\n<li><a href="docs/library.html"><span class="n">≡</span>All documents</a></li>\n<li><a href="docs/universes.html"><span class="n">◇</span>Universe index</a></li>\n<li><a href="docs/adr.html"><span class="n">◇</span>Decisions (ADRs)</a></li>\n<li><a href="docs/threat-models.html"><span class="n">◇</span>Threat models</a></li>\n<li><a href="docs/business-team-and-roadmap-plan.html"><span class="n">◇</span>Team, budget, roadmap</a></li>\n`;
const wires = (mmd.match(/^### W\d+ /gm) || []).length;
const diagrams = (mmd.match(/^```mermaid/gm) || []).length;
const sections = toc.filter(t => !t.part).length;
const libPanel = `
      <div class="lib-panel">
        <h2>Specification library</h2>
        <p>${uni.length} universe constitutions, engineering designs, ${docs.filter(d => d.group === 'Decisions').length - 1} ADRs, ${docs.filter(d => d.group === 'Threat models').length - 1} threat models and the business pack, each on its own page.</p>
        <ul>
          <li><a href="docs/library.html">All documents</a></li>
          <li><a href="docs/universes.html">Universe index</a></li>
          <li><a href="docs/coverage-register.html">Coverage register</a></li>
          <li><a href="docs/engineering-kernel-design.html">Kernel design</a></li>
          <li><a href="docs/adr.html">Decisions</a></li>
          <li><a href="docs/business-cost-model.html">Cost model</a></li>
        </ul>
      </div>`;
let out = tpl.replaceAll('%%NAV%%', nav).replace('%%BODY%%', body)
  .replace(/<div><dt>Version<\/dt><dd>[^<]*<\/dd><\/div>/, `<div><dt>Version</dt><dd>${version[1]} · ${version[2]} amendments applied</dd></div>`)
  .replace(/<div><dt>Contents<\/dt><dd>[^<]*<\/dd><\/div>/, `<div><dt>Contents</dt><dd>${sections} sections · ${uni.length} universes · ${diagrams} diagrams · ${wires} wireframes</dd></div>`)
  .replace('<p class="stack-caption">The 13 canonical layers, foundation first. Select a layer to jump to its section.</p>', '<p class="stack-caption">The 13 canonical layers, foundation first. Select a layer to jump to its section.</p>' + libPanel)
  .replace(/UCOS-MASTER-ARCH v[\d.]+ · Source: UCOS-MASTER-ARCHITECTURE.md · Companion specs in constitutions\/, engineering\/ and spec\//, `UCOS-MASTER-ARCH v${version[1]} · Source: UCOS-MASTER-ARCHITECTURE.md · Companion documents in the <a href="docs/library.html">specification library</a>`)
  .replace(extraCssMarker(), '');
function extraCssMarker() { return '%%NONE%%'; }
out = out.replace('</style>', '.lib-panel{margin-top:28px;padding:18px 20px;background:var(--surface);border:1px solid var(--line);border-radius:6px;max-width:760px}.lib-panel h2{margin:0 0 6px;padding:0;border:0;font:700 13px/1.3 var(--font-body);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.lib-panel p{margin:0 0 10px;font-size:15px}.lib-panel ul{display:flex;flex-wrap:wrap;gap:6px 18px;list-style:none;margin:0;padding:0;font-size:15px}.lib-panel li+li{margin-top:0}\n</style>');
writeFileSync(join(OUTDIR, 'index.html'), out);
console.log('docs', docs.length + 1, 'with mermaid', mer, 'master sections', sections, 'wireframes', wires, 'diagrams', diagrams, 'version', version[1]);
