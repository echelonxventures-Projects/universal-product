/* LUXORA Platform — fixed wording in the reader's language, for the storefront and both consoles.

   The words come from the backend: the message catalogue (lib/expression.js) in the language the
   reader chose, keyed "text:<wording>". Wherever a page shows exactly a wording the catalogue holds,
   the catalogue's text stands instead — text, hints and labels, as each part of a page appears.
   A leading icon or number ("📦 Products", "01 · Foundation") stays and the words after it are
   looked up. A person's own words are never in the catalogue. Runs once per page. */
function lxWords(dict, o) {
  o = o || {};
  if (window.__lxWords) { Object.assign(window.__lxWords.dict, dict || {}); window.__lxWords.run(document.body); return; }
  const D = Object.assign({}, dict || {});
  const look = k => D["text:" + k];
  const said = x => {
    const k = x.trim(); if (!k) return x;
    let t = look(k); if (t != null) return t === k ? x : x.replace(k, t);
    const m = /^([^\p{L}]+)(\p{L}[\s\S]*)$/u.exec(k);
    if (m && (t = look(m[2].trim())) != null && t !== m[2].trim()) return x.replace(k, m[1] + t);
    return x;
  };
  const SKIP = /^(SCRIPT|STYLE|TEXTAREA|CODE|PRE)$/;
  const run = root => {
    if (!root) return;
    if (root.nodeType === 3) { if (!SKIP.test((root.parentNode || {}).nodeName)) { const t = said(root.nodeValue); if (t !== root.nodeValue) root.nodeValue = t; } return; }
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    for (let n = root; n; n = w.nextNode()) {
      if (n.nodeType === 3) { if (!SKIP.test((n.parentNode || {}).nodeName)) { const t = said(n.nodeValue); if (t !== n.nodeValue) n.nodeValue = t; } }
      else if (n.nodeType === 1) {
        for (const a of ["placeholder", "title", "aria-label"]) { const v = n.getAttribute(a); if (v) { const t = said(v); if (t !== v) n.setAttribute(a, t); } }
        if (n.hasAttribute("data-lxlang") && !n.firstChild) picker(n);
      }
    }
  };
  /* the reader's choice of language, from the languages the backend can answer in */
  const picker = el => {
    const langs = o.languages || [];
    if (langs.length < 2) return;
    const s = document.createElement("select");
    s.setAttribute("aria-label", "Language"); s.className = "lx-lang";
    for (const l of langs) { const op = document.createElement("option"); op.value = l.key; op.textContent = l.native || l.name || l.key; if (l.key === o.lang) op.selected = true; s.appendChild(op); }
    s.onchange = () => { document.cookie = "azlang=" + encodeURIComponent(s.value) + "; path=/; max-age=31536000; samesite=lax"; location.reload(); };
    el.appendChild(s);
  };
  if (o.lang) document.documentElement.lang = o.lang;
  if (o.dir) document.documentElement.dir = o.dir;
  window.__lxWords = { dict: D, run, said };
  const start = () => {
    run(document.body);
    new MutationObserver(ms => { for (const m of ms) { if (m.type === "characterData") run(m.target); else m.addedNodes.forEach(n => { if (n.nodeType === 1 || n.nodeType === 3) run(n); }); } })
      .observe(document.body, { childList: true, subtree: true, characterData: true });
  };
  document.body ? start() : document.addEventListener("DOMContentLoaded", start);
}
