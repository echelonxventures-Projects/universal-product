/* LUXORA Platform - structured editors for the product domain (shared by both consoles)

   Media and attributes are structured data the storefront renders directly (the product
   gallery reads {kind,label,url|emoji}), so operators edit them as rows — never as
   hand-written JSON. Media kinds come from the registry's mediaKinds vocabulary, so a
   new kind (drone footage, inspection report…) is a registry row, not a front-end change.

   Each editor owns a model array/object, re-renders its own DOM on add/remove, and syncs
   every keystroke back into the model — so the console reads the value at save time with
   a returned accessor and never has to parse a textarea. the escaper comes from the console
   script that includes this one. */
"use strict";

const DEFAULT_KINDS = [{ key: "image", name: "Image" }, { key: "video", name: "Video" }];
/* private escaper under a unique name: the console scripts declare their own global
   `esc`, and two top-level declarations in classic scripts is a fatal SyntaxError. A
   re-render from a timer or a late event must never throw on escaping being unavailable. */
const escAttr = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

/* ---------- media ---------- */
function mediaRowHtml(m, kinds) {
  const opts = (kinds || DEFAULT_KINDS).map(k => `<option value="${escAttr(k.key)}" ${k.key === (m.kind || "image") ? "selected" : ""}>${escAttr(k.name)}</option>`).join("");
  return `<div class="mrow">
    <select class="mrow-kind" data-mk>${opts}</select>
    <input class="mrow-label" data-ml placeholder="Label (e.g. Front view)" value="${escAttr(m.label || "")}">
    <input class="mrow-val" data-mv placeholder="https://… image or video URL, or an emoji" value="${escAttr(m.url || m.emoji || "")}">
    <button type="button" class="p-btn sm danger" data-mx title="Remove this media">✕</button></div>`;
}
/* mount(root, items, kinds) -> getValue(). Redraws on add/remove; syncs on input. */
function mediaEditor(root, items, kinds) {
  if (!root) return () => [];
  const ks = (kinds && kinds.length ? kinds : DEFAULT_KINDS);
  const model = Array.isArray(items) ? items.map(m => ({ ...m })) : [];
  const render = () => {
    root.innerHTML = model.map(m => mediaRowHtml(m, ks)).join("") +
      `<div class="medit-foot"><button type="button" class="p-btn sm" data-madd>+ Add media</button>
       <small class="medit-hint">A URL renders the real asset in the storefront; an emoji renders as a coloured tile.</small></div>`;
    root.querySelectorAll(".mrow").forEach((r, i) => {
      const sync = () => {
        const mv = r.querySelector("[data-mv]").value || "";
        delete model[i].url; delete model[i].emoji;
        model[i].kind = r.querySelector("[data-mk]").value;
        model[i].label = r.querySelector("[data-ml]").value;
        if (/^https?:\/\//i.test(mv.trim())) model[i].url = mv.trim();
        else if (mv.trim()) model[i].emoji = mv.trim();
      };
      r.addEventListener("input", sync);
      r.querySelector("[data-mk]").addEventListener("change", sync);
      r.querySelector("[data-mx]").onclick = () => { model.splice(i, 1); render(); };
    });
    const add = root.querySelector("[data-madd]");
    if (add) add.onclick = () => { model.push({ kind: ks[0].key, label: "", url: "" }); render(); };
  };
  render();
  return () => model.map(m => ({ ...m }));
}

/* ---------- key/value attributes ---------- */
function kvRowHtml(k, v) {
  return `<div class="mrow">
    <input class="mrow-key" data-ak placeholder="Key (e.g. material)" value="${escAttr(k)}">
    <input class="mrow-val" data-av placeholder="Value (e.g. organic cotton)" value="${escAttr(v)}">
    <button type="button" class="p-btn sm danger" data-ax title="Remove this attribute">✕</button></div>`;
}
/* mount(root, obj) -> getValue(). Custom attributes as key/value rows. */
function kvEditor(root, obj) {
  if (!root) return () => ({});
  const model = Array.isArray(obj) || typeof obj !== "object" ? [] : Object.entries(obj).map(([k, v]) => [String(k), String(v)]);
  const render = () => {
    root.innerHTML = model.map(([k, v]) => kvRowHtml(k, v)).join("") +
      `<div class="medit-foot"><button type="button" class="p-btn sm" data-aadd>+ Add attribute</button>
       <small class="medit-hint">Anything the universe doesn't declare above — the storefront shows it in the product's details.</small></div>`;
    root.querySelectorAll(".mrow").forEach((r, i) => {
      const sync = () => { model[i][0] = r.querySelector("[data-ak]").value; model[i][1] = r.querySelector("[data-av]").value; };
      r.addEventListener("input", sync);
      r.querySelector("[data-ax]").onclick = () => { model.splice(i, 1); render(); };
    });
    const add = root.querySelector("[data-aadd]");
    if (add) add.onclick = () => { model.push(["", ""]); render(); };
  };
  render();
  return () => {
    const out = {};
    for (const [k, v] of model) if (String(k).trim()) out[String(k).trim()] = v;
    return out;
  };
}
