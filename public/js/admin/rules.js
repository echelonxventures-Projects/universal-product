/* LUXORA Platform — the rules domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vSettings() {
  const { settings: st, countries, taxModes, currencies } = await api("/admin/settings");
  const geo = { countries, taxModes, currencies };
  const reg = await api("/meta");
  /* the feature flags ARE capability atoms — read the catalog so the settings view
     labels each with its real name and points to where it is tuned */
  const cat = await api("/capabilities").catch(() => ({}));
  const capAtoms = {}; let capNote = "";
  if (cat && cat.catalog) {
    for (const c of cat.catalog) if (c.settings_atom) capAtoms[c.key] = c;
    const n = Object.keys(capAtoms).length;
    if (n) capNote = `The <b>${n}</b> toggles marked <span class="p-tag">atom</span> live in <b>◈ Capabilities</b> — switch and tune them there; this checkbox is the same bit.`;
  }
  const sec = (name, title, html) => `<div class="p-panel" data-sec="${name}"><h2>${title}</h2>${html}</div>`;
  const inp = (path, label, val, type = "text") => `<label><span>${label}</span><input data-set="${path}" type="${type}" step="any" value="${esc(val)}"></label>`;
  return `
  ${sec("brand", "Brand", `<div class="p-form"><div class="row">
    ${inp("brand.name", "Store name", st.brand.name)}${inp("brand.wordmark", "Wordmark", st.brand.wordmark)}</div>
    ${inp("brand.tagline", "Tagline", st.brand.tagline)}${inp("brand.supportEmail", "Support email", st.brand.supportEmail)}
    <label><span>Logo (emoji, text or inline SVG)</span><textarea data-set="brand.logo" rows="2">${esc(st.brand.logo || "")}</textarea></label>
    ${inp("brand.poweredBy", "Powered-by line", st.brand.poweredBy)}
    ${inp("brand.footerNote", "Footer note ({year} {brand})", st.brand.footerNote)}</div>`)}
  ${sec("theme", "Theme & Aesthetics", `<div class="p-form"><div class="row3">
    ${inp("theme.bg", "Background", st.theme.bg, "color")}${inp("theme.surface", "Surface", st.theme.surface, "color")}${inp("theme.ink", "Ink", st.theme.ink, "color")}
    ${inp("theme.header", "Header", st.theme.header, "color")}${inp("theme.accent", "Accent", st.theme.accent, "color")}${inp("theme.accentDeep", "Accent deep", st.theme.accentDeep, "color")}
    ${inp("theme.link", "Link", st.theme.link, "color")}${inp("theme.star", "Stars", st.theme.star, "color")}${inp("theme.deal", "Deal red", st.theme.deal, "color")}
    </div><div class="row">
    ${inp("theme.radius", "Corner radius", st.theme.radius)}${inp("theme.radiusBtn", "Button radius", st.theme.radiusBtn)}</div>
    ${inp("theme.fontDisplay", "Display font stack", st.theme.fontDisplay)}${inp("theme.fontBody", "Body font stack", st.theme.fontBody)}
    <label><span>Custom CSS</span><textarea data-set="theme.customCSS" rows="4">${esc(st.theme.customCSS || "")}</textarea></label>
    <div class="swatch-row">${[["Gold Noir", "#C6A15B", "#0C0E13"], ["Rose Atelier", "#B76E79", "#1A1214"], ["Emerald", "#2E8B6E", "#0E1A16"], ["Midnight Blue", "#5B9BD5", "#0B1220"], ["Terracotta", "#C46A4A", "#1C1210"]].map(([n, a, h]) => `<button class="swatch" title="${n}" data-preset="${a}|${h}" style="background:linear-gradient(135deg,${a},${h})"></button>`).join("")}</div></div>`)}
  ${sec("commerce", "Commerce & Localization", `<div class="p-form"><div class="row3">
    <label><span>Country <em class="p-tag">(drives currency, symbol, locale, default tax — managed in Platform → Geo)</em></span><select data-set="commerce.country">${geo.countries.map(c => `<option ${st.commerce.country === c.code ? "selected" : ""} value="${c.code}">${esc(c.name)} (${esc(c.currency)} ${esc(c.symbol)})</option>`).join("")}</select></label>
    <label><span>Currency <em class="p-tag">(default: jurisdiction currency — pick another to sell in a different settlement currency at live FX)</em></span><select data-set="commerce.currency"><option value="">— from country (${esc(geo.countries.find(c => c.code === st.commerce.country) ? geo.countries.find(c => c.code === st.commerce.country).currency : "")}) —</option>${geo.currencies.map(x => `<option value="${x.code}" ${st.commerce.currency === x.code ? "selected" : ""}>${esc(x.name)} (${x.code} ${esc(x.symbol)}) · 1=${x.usd} USD</option>`).join("")}</select></label>
    ${inp("commerce.symbol", "Symbol (blank = from country)", st.commerce.symbol || "")}
    <label><span>Locale <em class="p-tag">(blank = from country)</em></span><input data-set="commerce.locale" value="${esc(st.commerce.locale || "")}"></label>
    <label><span>Tax mode <em class="p-tag">(blank = country default)</em></span><select data-set="commerce.taxMode"><option value="">— country default —</option>${geo.taxModes.map(t => `<option value="${t.key}" ${st.commerce.taxMode === t.key ? "selected" : ""}>${esc(t.label)} (${esc(t.description || t.key)})</option>`).join("")}</select></label>
    <label><span>Tax rate (0-1, blank = country default)</span><input data-set="commerce.taxRate" type="number" step="any" value="${st.commerce.taxRate == null ? "" : st.commerce.taxRate}"></label>
    ${inp("commerce.freeShipThreshold", "Free shipping ≥", st.commerce.freeShipThreshold, "number")}${inp("commerce.shipFee", "Shipping fee", st.commerce.shipFee, "number")}
    ${inp("commerce.daysPriority", "Priority days", st.commerce.daysPriority, "number")}${inp("commerce.daysStandard", "Standard days", st.commerce.daysStandard, "number")}
    ${inp("commerce.perPage", "Results per page", st.commerce.perPage, "number")}${inp("commerce.cartMaxQty", "Cart max qty", st.commerce.cartMaxQty, "number")}
    </div></div>`)}
  ${sec("features", "Feature Flags", `<div class="p-form"><div class="row3">
    ${Object.entries(st.features).map(([k, v]) => {
      const atom = (capAtoms || {})[k.replace(/([A-Z])/g, (_, c) => "_" + c.toLowerCase())];
      return `<label style="display:flex;gap:8px;align-items:center" title="${esc(atom ? atom.description : "a settings row, not yet an atom")}"><input type="checkbox" data-feat="${k}" ${v ? "checked" : ""}> ${esc(atom ? atom.label : k)}${atom ? ' <span class="p-tag">atom</span>' : ""}</label>`;
    }).join("")}
    </div>${capNote ? `<p class="hint" style="grid-column:1/-1">${capNote}</p>` : ""}</div>`)}
  ${sec("copy", "Copy & Wording", `<div class="p-form"><div class="row">
    ${Object.entries(st.copy).slice(0, 24).map(([k, v]) => inp("copy." + k, k, v)).join("")}</div></div>`)}
  ${sec("mode", "Deployment Mode", `<div class="p-form"><div class="row">
    <label><span>Mode</span><select id="modeSel">${reg.deployModes.map(m => `<option value="${m.key}" ${TT.tenant.mode === m.key ? "selected" : ""}>${m.name} — ${m.desc}</option>`).join("")}</select></label>
    <label><span>Industries (empty = all)</span><input id="modeInds" value="${esc((TT.tenant.industries || []).join(","))}" placeholder="furniture,grocery"></label></div>
    <button class="p-btn" id="modeSave">Apply mode</button>`)}
  <div style="display:flex;gap:12px"><button class="p-btn primary" id="setSave">Save all settings</button>
    <button class="p-btn danger" id="setReset">Reset to defaults</button></div>`;
}
function wireSettings() {
  $$("[data-preset]").forEach(b => b.onclick = () => {
    const [a, h] = b.dataset.preset.split("|");
    $('[data-set="theme.accent"]').value = a; $('[data-set="theme.header"]').value = h;
  });
  $("#setSave").onclick = async () => {
    const body = { brand: {}, theme: {}, commerce: {}, copy: {}, features: {} };
    $$("[data-set]").forEach(i => {
      const [sec, key] = i.dataset.set.split(".");
      body[sec][key] = i.type === "number" ? Number(i.value) : i.value;
    });
    $$("[data-feat]").forEach(cb => body.features[cb.dataset.feat] = cb.checked);
    for (const k of Object.keys(body)) if (!Object.keys(body[k]).length) delete body[k];
    await api("/admin/settings", "PUT", body);
    TT = await api("/config");
    toast("Settings saved — storefront updated live");
  };
  $("#setReset").onclick = async () => { if (confirm("Reset all settings to platform defaults?")) { await api("/admin/settings/reset", "POST"); TT = await api("/config"); render(); } };
  $("#modeSave").onclick = async () => {
    await api("/admin/mode", "PUT", { mode: $("#modeSel").value, industries: $("#modeInds").value.split(",").map(x => x.trim()).filter(Boolean) });
    TT = await api("/config"); toast("Deployment mode applied"); render();
  };
}

screen("settings", { group: "Settings", label: "⚙️ Settings", order: 0, render: async () => await vSettings(), wire: async () => { wireSettings(); } });
