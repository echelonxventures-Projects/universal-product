/* LUXORA Platform — the stores domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* the store's setup checklist (GET /api/admin/setup, the same steps the platform sees for it):
   each step done or pending, and a form to finish the pending ones */
async function vSetup() {
  const st = await api("/admin/setup");
  if (!st) return '<div class="p-empty">⚠️ Setup status unavailable</div>';

  const { steps, done, total, available } = st;
  const progress = total ? Math.round((done / total) * 100) : 0;

  return `
  <div class="p-wizard">
    <div class="wizard-header">
      <div class="wizard-progress">
        <div class="wizard-progress-bar">
          <div class="wizard-progress-fill" style="width:${progress}%"></div>
        </div>
        <span class="wizard-progress-text">${done} of ${total} steps complete (${progress}%)</span>
      </div>
      <h1>Welcome to ${esc(TT.tenant.name)}</h1>
      <p class="wizard-subtitle">Let&rsquo;s get your store ready. Each step takes 1&ndash;2 minutes.</p>
    </div>

    <div class="wizard-steps">
      ${steps.map((step, i) => `
        <div class="wizard-step ${step.done ? 'done' : (i === steps.findIndex(s => !s.done) ? 'current' : 'pending')}" data-key="${step.key}">
          <div class="step-marker">
            ${step.done ? '✓' : (i + 1)}
          </div>
          <div class="step-content">
            <h3>${esc(step.label)}</h3>
            <p class="step-note">${step.note ? esc(step.note) : 'Not started'}</p>
          </div>
          <div class="step-action">
            ${!step.done ? `<button class="p-btn primary" data-wizard-step="${step.key}">Start</button>` : '<span class="p-tag">Done</span>'}
          </div>
        </div>
      `).join('')}
    </div>

    ${done === total ? `
      <div class="wizard-complete">
        <h2>✓ You&rsquo;re all set!</h2>
        <p>Your store is configured and ready for business.</p>
        <div class="wizard-next">
          <button class="p-btn primary" data-view="dash">Go to Dashboard</button>
          <button class="p-btn" data-view="products">Add Your First Product</button>
          <button class="p-btn" data-view="settings">Review Settings</button>
        </div>
      </div>
    ` : ''}
  </div>`;
}

function wireSetup() {
  $$("[data-wizard-step]").forEach(btn => {
    btn.onclick = () => launchSetupStep(btn.dataset.wizardStep);
  });
  $$("[data-view]").forEach(btn => {
    btn.onclick = () => { view = btn.dataset.view; render(); };
  });
}

async function launchSetupStep(key) {
  const steps = {
    identity: () => launchIdentityStep(),
    owner: () => launchOwnerStep(),
    jurisdiction: () => launchJurisdictionStep(),
    tax: () => launchTaxStep(),
    payments: () => launchPaymentsStep(),
    shipping: () => launchShippingStep(),
    catalogue: () => launchCatalogueStep(),
    features: () => launchFeaturesStep(),
    capabilities: () => launchCapabilitiesStep(),
    plan: () => launchPlanStep()
  };
  if (steps[key]) await steps[key]();
  render();
}

async function launchIdentityStep() {
  const { settings: { brand } } = await api("/admin/settings");
  const html = `
    <div class="wizard-modal">
      <h2>Store Identity</h2>
      <form class="p-form" id="wizardIdentity">
        <label><span>Store Name</span><input name="name" value="${esc(brand.name)}" required></label>
        <label><span>Tagline</span><input name="tagline" value="${esc(brand.tagline)}" placeholder="Your store&rsquo;s tagline"></label>
        <label><span>Support Email</span><input name="supportEmail" type="email" value="${esc(brand.supportEmail)}"></label>
        <label><span>Logo (emoji or text)</span><textarea name="logo" rows="2">${esc(brand.logo || "")}</textarea></label>
        <button class="p-btn primary" type="submit">Save & Continue</button>
      </form>
    </div>
  `;
  await modal(html);
  const form = $("#wizardIdentity");
  form.onsubmit = async e => {
    e.preventDefault();
    const fd = new FormData(form);
    await api("/admin/settings", "PUT", { brand: Object.fromEntries(fd) });
    closeModal();
  };
}

async function launchOwnerStep() {
  const prof = await api("/admin/users").catch(() => ({ users: [] }));
  const admins = prof.users.filter(u => u.role === 'admin');
  const html = `
    <div class="wizard-modal">
      <h2>Owner / Admin Account</h2>
      ${admins.length ? `<p class="p-tag">Admin exists: ${esc(admins[0].email)}</p>` : ''}
      <form class="p-form" id="wizardOwner">
        <label><span>Full Name</span><input name="name" required></label>
        <label><span>Email</span><input name="email" type="email" required></label>
        <label><span>Password</span><input name="password" type="password" required minlength="10"></label>
        <label><span>Role</span><select name="staff_role"><option value="owner">Owner</option><option value="manager">Manager</option></select></label>
        <button class="p-btn primary" type="submit">Create Admin</button>
      </form>
    </div>
  `;
  await modal(html);
  $("#wizardOwner").onsubmit = async e => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api("/api/platform/users", "POST", { tenant_id: TT.tenant.id, name: fd.get('name'), email: fd.get('email'), password: fd.get('password'), role: 'admin', staff_role: fd.get('staff_role') });
    toast("Admin created");
    closeModal();
  };
}

async function launchJurisdictionStep() {
  const { settings: st, countries, taxModes } = await api("/admin/settings");
  const html = `
    <div class="wizard-modal">
      <h2>Jurisdiction & Legal Identity</h2>
      <form class="p-form" id="wizardJurisdiction">
        <label><span>Country</span><select name="country">${countries.map(c => `<option ${st.commerce.country === c.code ? 'selected' : ''} value="${c.code}">${esc(c.name)} (${c.code})</option>`).join('')}</select></label>
        <label><span>Legal Name</span><input name="legalName" value="${esc((await api("/platform/tenant/self").catch(() => ({ profile: {} }))).profile?.legalName || "")}" required></label>
        <label><span>Tax ID</span><input name="taxId" value="${esc((await api("/platform/tenant/self").catch(() => ({ profile: {} }))).profile?.taxId || "")}"></label>
        <label><span>Registration Address</span><textarea name="registrationAddress" rows="2">${esc((await api("/platform/tenant/self").catch(() => ({ profile: {} }))).profile?.registrationAddress || "")}</textarea></label>
        <button class="p-btn primary" type="submit">Save & Continue</button>
      </form>
    </div>
  `;
  await modal(html);
  $("#wizardJurisdiction").onsubmit = async e => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api("/api/platform/tenants/" + TT.tenant.id, "PUT", { jurisdiction: { country: fd.get('country'), legalName: fd.get('legalName'), taxId: fd.get('taxId'), registrationAddress: fd.get('registrationAddress') } });
    await api("/admin/settings", "PUT", { commerce: { country: fd.get('country') } });
    closeModal();
  };
}

async function launchTaxStep() {
  const { settings: st, countries, taxModes, currencies } = await api("/admin/settings");
  const geo = { countries, taxModes, currencies };
  const html = `
    <div class="wizard-modal">
      <h2>Tax Configuration</h2>
      <p class="p-tag">Set up how tax is calculated for your store</p>
      <form class="p-form" id="wizardTax">
        <label><span>Tax Mode</span><select name="taxMode"><option value="">&mdash; country default &mdash;</option>${geo.taxModes.map(t => `<option value="${t.key}" ${st.commerce.taxMode === t.key ? 'selected' : ''}>${esc(t.label)} (${esc(t.description || t.key)})</option>`).join('')}</select></label>
        <label><span>Tax Rate (0-1, blank = country default)</span><input name="taxRate" type="number" step="any" value="${st.commerce.taxRate == null ? '' : st.commerce.taxRate}"></label>
        <button class="p-btn primary" type="submit">Save & Continue</button>
      </form>
    </div>
  `;
  await modal(html);
  $("#wizardTax").onsubmit = async e => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api("/admin/settings", "PUT", { commerce: { taxMode: fd.get('taxMode') || null, taxRate: fd.get('taxRate') ? Number(fd.get('taxRate')) : null } });
    closeModal();
  };
}

async function launchPaymentsStep() {
  const g = await api("/admin/gateways");
  const html = `
    <div class="wizard-modal">
      <h2>Payment Gateways</h2>
      <p class="p-tag">Enable at least one gateway to accept payments</p>
      <div class="wizard-gateways">
        ${g.gateways.map(x => `
          <label class="gateway-card ${x.enabled ? 'enabled' : ''}">
            <input type="checkbox" name="gateway" value="${x.id}" ${x.enabled ? 'checked' : ''}>
            <span class="gw-emoji">${x.emoji}</span>
            <div class="gw-info">
              <strong>${esc(x.name)}</strong>
              <small>${esc(x.desc || '')}</small>
              <span class="p-tag">${esc((x.methods || []).join(', '))}</span>
            </div>
            <span class="gw-fee">${x.feePct}%${x.feeFixed ? ' + ' + money(x.feeFixed) : ''}</span>
          </label>
        `).join('')}
      </div>
      <div class="wizard-actions">
        <button class="p-btn primary" id="gwSave">Save & Continue</button>
      </div>
    </div>
  `;
  await modal(html);
  $("#gwSave").onclick = async () => {
    const enabled = $$("#modal input[name=gateway]:checked").map(cb => cb.value);
    const cfg = g.gateways.filter(x => enabled.includes(x.id)).map(x => ({ provider_id: x.id, enabled: true }));
    await api("/admin/gateways", "PUT", { gateways: cfg });
    closeModal();
  };
}

async function launchShippingStep() {
  const { settings: st } = await api("/admin/settings");
  const carriers = await api("/admin/shipping/carriers").catch(() => ({ carriers: [] }));
  const html = `
    <div class="wizard-modal">
      <h2>Shipping & Delivery</h2>
      <form class="p-form" id="wizardShipping">
        <div class="row3">
          <label><span>Free Shipping Over</span><input name="freeShipThreshold" type="number" step="0.01" value="${esc(st.commerce.freeShipThreshold)}" placeholder="0"></label>
          <label><span>Default Shipping Fee</span><input name="shipFee" type="number" step="0.01" value="${esc(st.commerce.shipFee)}"></label>
          <label><span>Priority (days)</span><input name="daysPriority" type="number" value="${esc(st.commerce.daysPriority)}"></label>
          <label><span>Standard (days)</span><input name="daysStandard" type="number" value="${esc(st.commerce.daysStandard)}"></label>
        </div>
        <h3>Carriers</h3>
        <div class="carrier-list">
          ${carriers.carriers.map(c => `
            <label><input type="checkbox" name="carrier" value="${c.id}" ${c.enabled ? 'checked' : ''}> ${c.emoji} ${esc(c.name)} &mdash; ${c.eta[0]}&ndash;${c.eta[1]} days ${c.baseFee ? 'from ' + money(c.baseFee) : ''}</label>
          `).join('')}
        </div>
        <button class="p-btn primary" type="submit">Save & Continue</button>
      </form>
    </div>
  `;
  await modal(html);
  $("#wizardShipping").onsubmit = async e => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const carriers = fd.getAll("carrier");
    await api("/admin/settings", "PUT", {
      commerce: {
        freeShipThreshold: Number(fd.get("freeShipThreshold")),
        shipFee: Number(fd.get("shipFee")),
        daysPriority: Number(fd.get("daysPriority")),
        daysStandard: Number(fd.get("daysStandard"))
      },
      shipping: { carriers }
    });
    closeModal();
  };
}

async function launchCatalogueStep() {
  const html = `
    <div class="wizard-modal">
      <h2>Add Your First Products</h2>
      <p class="p-tag">Start with 3&ndash;5 products to see your store come alive</p>
      <form class="p-form" id="wizardProduct">
        <label><span>Product Name</span><input name="title" required></label>
        <label><span>Brand</span><input name="brand" required></label>
        <label><span>Department</span><select name="dept"><option value="">Select...</option>${(await api("/admin/departments").catch(() => ({ departments: [] }))).departments.map(d => `<option value="${d.key}">${esc(d.label)}</option>`).join('')}</select></label>
        <label><span>Price</span><input name="price" type="number" step="0.01" required></label>
        <label><span>Type</span><select name="type"><option value="physical">Physical</option><option value="digital">Digital</option><option value="service">Service</option><option value="subscription">Subscription</option></select></label>
        <label><span>Stock</span><input name="stock" type="number" value="100"></label>
        <button class="p-btn primary" type="submit">Add Product</button>
      </form>
      <div style="margin-top:16px;text-align:center"><button class="p-btn" id="skipCatalogue">Skip for now</button></div>
    </div>
  `;
  await modal(html);
  $("#wizardProduct").onsubmit = async e => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api("/admin/products", "POST", Object.fromEntries(fd));
    toast("Product added!");
    e.target.reset();
  };
  $("#skipCatalogue").onclick = closeModal;
}

async function launchFeaturesStep() {
  const { settings: { features } } = await api("/admin/settings");
  const caps = await api("/capabilities");
  const atoms = (caps.catalog || []).filter(c => c.settings_atom);
  const html = `
    <div class="wizard-modal">
      <h2>Shopper Features</h2>
      <p class="p-tag">Enable features that make shopping delightful</p>
      <div class="feature-grid">
        ${atoms.map(c => `
          <label class="feature-card ${features[c.key] ? 'enabled' : ''}">
            <input type="checkbox" name="feature" value="${c.key}" ${features[c.key] ? 'checked' : ''}>
            <span class="feature-icon">${c.icon || '&check;'}</span>
            <strong>${esc(c.label)}</strong>
            <small>${esc(c.description)}</small>
          </label>
        `).join('')}
      </div>
      <button class="p-btn primary" id="featSave">Save & Continue</button>
    </div>
  `;
  await modal(html);
  $("#featSave").onclick = async () => {
    const enabled = $$("#modal input[name=feature]:checked").map(cb => cb.value);
    const feats = Object.fromEntries(enabled.map(k => [k, true]));
    await api("/admin/settings", "PUT", { features: { ...features, ...feats } });
    closeModal();
  };
}

async function launchCapabilitiesStep() {
  const caps = await api("/capabilities");
  const domains = [...new Set((caps.catalog || []).map(c => c.domain))];
  const html = `
    <div class="wizard-modal" style="max-width:800px">
      <h2>Capabilities</h2>
      <p class="p-tag">Fine-tune what your store can do</p>
      <div class="capabilities-tabs">
        <div class="tab-buttons">
          ${domains.map((d, i) => `<button class="p-btn sm ${i === 0 ? 'active' : ''}" data-tab="${d}">${esc(d)}</button>`).join('')}
        </div>
        <div class="tab-panels">
          ${domains.map((d, i) => `
            <div class="tab-panel ${i === 0 ? '' : 'hidden'}" data-domain="${d}">
              ${(caps.catalog || []).filter(c => c.domain === d).map(c => `
                <label class="cap-row ${c.enabled ? 'on' : ''}">
                  <input type="checkbox" name="cap" value="${c.key}" ${c.enabled ? 'checked' : ''}>
                  <span>${c.icon || ''} ${esc(c.label)}</span>
                  <small>${esc(c.description)}</small>
                </label>
              `).join('')}
            </div>
          `).join('')}
        </div>
      </div>
      <button class="p-btn primary" id="capSave">Save & Continue</button>
    </div>
  `;
  await modal(html);
  $$("#modal [data-tab]").forEach(btn => btn.onclick = () => {
    $$("#modal [data-tab]").forEach(b => b.classList.remove("active"));
    $$("#modal .tab-panel").forEach(p => p.classList.add("hidden"));
    btn.classList.add("active");
    $("#modal .tab-panel[data-domain=" + btn.dataset.tab + "]").classList.remove("hidden");
  });
  $("#capSave").onclick = async () => {
    const enabled = $$("#modal input[name=cap]:checked").map(cb => cb.value);
    for (const key of enabled) {
      const cap = (caps.catalog || []).find(c => c.key === key);
      if (cap && !cap.enabled) await api("/capabilities/enable", "POST", { capability: key });
    }
    closeModal();
  };
}

async function launchPlanStep() {
  const plans = await api("/platform/plans").catch(() => ({ plans: [] }));
  const sub = await api("/admin/subscription").catch(() => ({}));
  const html = `
    <div class="wizard-modal">
      <h2>Subscription Plan</h2>
      <p class="p-tag">Choose a plan that fits your business</p>
      ${sub.plan ? `<p class="p-tag">Current: ${esc(sub.plan.name)}</p>` : ''}
      <div class="plan-grid">
        ${(plans.plans || []).map(p => `
          <label class="plan-card ${sub.plan && sub.plan.id === p.id ? 'selected' : ''}">
            <input type="radio" name="plan" value="${p.id}" ${sub.plan && sub.plan.id === p.id ? 'checked' : ''}>
            <h4>${esc(p.name)}</h4>
            <div class="plan-price">${money(p.price_month)}/${p.currency ? esc(p.currency) : 'mo'}</div>
            <ul>${[p.max_products ? `Products: ${p.max_products}` : '', p.max_orders_month ? `Orders/mo: ${p.max_orders_month}` : ''].filter(Boolean).map(x => `<li>${x}</li>`).join('')}</ul>
          </label>
        `).join('')}
      </div>
      <button class="p-btn primary" id="planSave">Save & Continue</button>
    </div>
  `;
  await modal(html);
  $("#planSave").onclick = async () => {
    const planId = $$("#modal input[name=plan]:checked")[0]?.value;
    if (planId) {
      await api("/admin/subscription", "POST", { plan_id: Number(planId) });
      toast("Plan updated");
    }
    closeModal();
  };
}

function closeModal() {
  const m = document.getElementById("modal");
  m.classList.add("hidden");
  if (window._modalResolve) { window._modalResolve(); window._modalResolve = null; }
}

screen("setup", { group: "Overview", label: "🧭 Setup Wizard", render: vSetup, wire: wireSetup });
