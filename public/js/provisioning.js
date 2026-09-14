/* LUXORA Platform - provisioning panel (platform policy: set once at platform setup, never per store) */
/* globals api, esc, $, $$, toast, money, render, P */
"use strict";

function pol_num(k, label, hint) {
  return '<label><span>' + label + '</span><input data-pol="' + k + '" type="number" step="1" min="1" value="__V' + k + '__"><em class="p-tag">' + (hint || "") + '</em></label>';
}
function pol_bool(k, label) {
  return '<label class="chk"><input type="checkbox" data-pol="' + k + '"> ' + label + '</label>';
}

async function vProvisioning() {
  const [cfg, sc, plans] = await Promise.all([api("/platform/config"), api("/platform/security"), api("/platform/plans")]);
  P.provisioned = !!cfg.provisionedAt;
  const pol = cfg.policy;
  let h = "";
  if (!cfg.provisionedAt) h += '<div class="prov-banner">⚠ Initial platform provisioning pending — save the security &amp; rollout policy below to mark the platform configured.</div>';
  h += '<div class="p-cards">'
    + '<div class="p-stat"><em>Status</em><b>' + (cfg.provisionedAt ? "Provisioned" : "SET UP NOW") + '</b><small>' + (cfg.provisionedAt ? "policy saved " + String(cfg.provisionedAt).slice(0, 10) : "policy not saved yet") + '</small></div>'
    + '<div class="p-stat"><em>Master key</em><b>' + esc(cfg.keyInfo.version) + '</b><small>' + cfg.keyInfo.count + ' key version(s) · rotation re-seals all secrets</small></div>'
    + '<div class="p-stat"><em>Pepper</em><b>' + (cfg.pepperConfigured ? "SET" : "env only") + '</b><small>LUXORA_PEPPER — never stored in DB</small></div>'
    + '<div class="p-stat"><em>TLS boot</em><b>' + (cfg.tlsBoot ? "ON" : "off") + '</b><small>LUX_TLS=1 → HTTPS</small></div>'
    + '</div>';
  h += '<div class="p-grid2"><div class="p-panel"><h2>Credential policy</h2><div class="p-form">'
    + pol_num("minPasswordLength", "Minimum password length", "default " + cfg.defaults.minPasswordLength)
    + pol_bool("requireLetterDigit", "Require letter + digit")
    + pol_bool("blockCommon", "Block common/breached passwords")
    + '<div class="row3"><label><span>scrypt log₂N</span><select data-pol="kdfV2.logN">' + [14, 15, 16, 17, 18, 19, 20].map(function (x) { return '<option ' + (pol.kdfV2.logN === x ? "selected" : "") + '>' + x + '</option>'; }).join("") + '</select></label>'
    + '<label><span>r</span><input data-pol="kdfV2.r" type="number" value="' + pol.kdfV2.r + '"></label>'
    + '<label><span>p</span><input data-pol="kdfV2.p" type="number" value="' + pol.kdfV2.p + '"></label></div>'
    + '<p class="p-tag">Applies to new/rotated credentials; existing hashes upgrade transparently on next login.</p></div></div>';
  h += '<div class="p-panel"><h2>Abuse control</h2><div class="p-form">'
    + pol_num("authPerMin", "Auth attempts / minute / IP")
    + pol_num("apiPerMin", "API requests / minute / IP")
    + pol_num("lockoutThreshold", "Failed logins before lockout")
    + pol_num("lockoutBaseSec", "First lockout seconds")
    + pol_num("lockoutCapSec", "Max lockout seconds")
    + '</div></div></div>';
  h += '<div class="p-grid2"><div class="p-panel"><h2>Session &amp; transport</h2><div class="p-form">'
    + pol_bool("csrfEnabled", "CSRF double-submit enforcement")
    + pol_bool("hsts", "Strict-Transport-Security (when TLS)")
    + pol_bool("demoHints", "Demo account hints on login screens")
    + pol_bool("cspInlineStyles", "Allow inline style attributes in CSP (disable for strictest mode)")
    + '<p class="p-tag">HttpOnly + SameSite cookie flags are structural and cannot be disabled.</p></div></div>';
  h += '<div class="p-panel"><h2>New-store defaults (applied at launch)</h2><div class="p-form">'
    + '<label><span>Default plan</span><select data-pol="provisioning.defaultPlanId">' + plans.plans.map(function (x) { return '<option value="' + x.id + '" ' + (pol.provisioning.defaultPlanId === x.id ? "selected" : "") + '>' + esc(x.name) + '</option>'; }).join("") + '</select></label>'
    + pol_bool("provisioning.seedCatalogByDefault", "Seed demo catalog on launch")
    + pol_bool("provisioning.sandboxGatewaysByDefault", "Gateways start in sandbox mode")
    + pol_bool("provisioning.currencyOverridesAllowed", "Allow stores to override settlement currency")
    + pol_bool("provisioning.couponsAllowed", "Stores may offer promo codes to customers")
    + pol_bool("provisioning.globalOffersAllowed", "Platform global offers/coupons apply across every store")
    + pol_bool("provisioning.fiscalContextsAllowed", "Allow customer-facing fiscal context pickers (procurement portals)")
    + '</div></div></div>';
  h += '<p><button class="p-btn primary" id="polSave">Save platform policy</button></p>';
  h += '<div class="p-panel"><h2>Layer scorecard</h2><div class="p-scroll-x"><table class="p-table"><thead><tr><th>#</th><th>Layer</th><th>Status</th><th>Detail</th></tr></thead><tbody>'
    + sc.layers.map(function (l) { return '<tr><td>' + l.n + '</td><td><b>' + esc(l.layer) + '</b></td><td><span class="badge published">' + esc(l.status) + '</span></td><td class="p-tag">' + esc(l.detail) + '</td></tr>'; }).join("")
    + '</tbody></table></div></div>';
  /* fill values after HTML is in place */
  setTimeout(function () {
    $$("[data-pol]").forEach(function (el) {
      var k = el.dataset.pol;
      var v = k.indexOf("kdfV2.") === 0 ? pol.kdfV2[k.slice(6)] : (k.indexOf("provisioning.") === 0 ? pol.provisioning[k.slice(13)] : pol[k]);
      if (el.type === "checkbox") el.checked = !!v; else if (el.tagName === "SELECT") el.value = String(v); else el.value = v;
    });
    wireProvisioning();
  }, 0);
  return h;
}

function wireProvisioning() {
  var btn = document.getElementById("polSave");
  if (!btn || btn.__wired) return;
  btn.__wired = true;
  btn.onclick = async function () {
    var body = { kdfV2: {}, provisioning: {} };
    $$("[data-pol]").forEach(function (el) {
      var k = el.dataset.pol;
      var val = el.type === "checkbox" ? el.checked : (el.type === "number" || +el.value === +el.value && el.value !== "" ? Number(el.value) : el.value);
      if (k.indexOf("kdfV2.") === 0) body.kdfV2[k.slice(6)] = val;
      else if (k.indexOf("provisioning.") === 0) body.provisioning[k.slice(13)] = val;
      else body[k] = val;
    });
    try { await api("/platform/config", "PUT", body); toast("Platform policy saved — enforced instantly across every store"); render(); }
    catch (e) { toast(e.message); }
  };
}
