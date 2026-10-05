/* Branding System - Platform & Store Hierarchy */
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d || {}; } };

// Get global platform branding
function getGlobalBranding() {
  return db().get('SELECT * FROM platform_branding WHERE id=1') || {};
}

// Get store permissions
function getStorePermissions(tenantId) {
  return db().get('SELECT * FROM store_branding_perms WHERE tenant_id=?', tenantId) || {
    can_change_name: 0,
    can_change_logo: 0,
    can_change_colors: 0,
    can_change_fonts: 0,
    can_change_footer: 0,
    can_change_nav: 0
  };
}

// Get store branding
function getStoreBranding(tenantId) {
  return db().get('SELECT * FROM store_branding WHERE tenant_id=?', tenantId) || {};
}

// Set global branding (Platform Admin only)
function setGlobalBranding(branding) {
  const { name, logo, tagline, colors, fonts } = branding;
  /* colors/fonts arrive as objects from the console or as JSON strings from a GET
     round-trip — accept either so a save/restore cycle never double-encodes. */
  db().run(
    `INSERT INTO platform_branding(id, name, logo, tagline, colors, fonts, updated_at)
     VALUES(1, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET name=excluded.name, logo=excluded.logo, tagline=excluded.tagline,
       colors=excluded.colors, fonts=excluded.fonts, updated_at=excluded.updated_at`,
    name || null, logo || null, tagline || null, JSON.stringify(J(colors, {})), JSON.stringify(J(fonts, {})), new Date().toISOString()
  );
  return getGlobalBranding();
}

// Set store permissions (Platform Admin only)
function setStorePermissions(tenantId, perms) {
  const { can_change_name, can_change_logo, can_change_colors, can_change_fonts, can_change_footer, can_change_nav } = perms;
  db().run(
    'INSERT INTO store_branding_perms(tenant_id, can_change_name, can_change_logo, can_change_colors, can_change_fonts, can_change_footer, can_change_nav) VALUES(?,?,?,?,?,?,?) ON CONFLICT(tenant_id) DO UPDATE SET can_change_name=excluded.can_change_name, can_change_logo=excluded.can_change_logo, can_change_colors=excluded.can_change_colors, can_change_fonts=excluded.can_change_fonts, can_change_footer=excluded.can_change_footer, can_change_nav=excluded.can_change_nav',
    tenantId, Number(can_change_name || 0), Number(can_change_logo || 0), Number(can_change_colors || 0), Number(can_change_fonts || 0), Number(can_change_footer || 0), Number(can_change_nav || 0)
  );
  return getStorePermissions(tenantId);
}

// Set store branding (checked against permissions)
function setStoreBranding(tenantId, perms, branding) {
  const storePerms = getStorePermissions(tenantId);
  const { name, logo, colors, fonts } = branding;
  const updates = [];
  
  if (name && storePerms.can_change_name) updates.push({ field: 'name', value: name });
  if (logo && storePerms.can_change_logo) updates.push({ field: 'logo', value: logo });
  if (colors && storePerms.can_change_colors) updates.push({ field: 'colors', value: JSON.stringify(colors) });
  if (fonts && storePerms.can_change_fonts) updates.push({ field: 'fonts', value: JSON.stringify(fonts) });
  
  if (!updates.length) return { error: 'No permitted fields to update', code: 403 };
  
  let sql = 'INSERT INTO store_branding(tenant_id, name, logo, colors, fonts, updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(tenant_id) DO UPDATE SET ';
  const params = [tenantId];
  updates.forEach((u, i) => {
    if (i === 0) sql += u.field + '=?';
    else sql += ', ' + u.field + '=?';
    params.push(u.value);
  });
  sql += ', updated_at=?';
  params.push(new Date().toISOString());
  
  db().run(sql, ...params);
  return getStoreBranding(tenantId);
}

// Get effective branding (inherits from global + overrides)
function getEffectiveBranding(tenantId) {
  const global = getGlobalBranding();
  const gColors = J(global.colors, {});
  const gFonts = J(global.fonts, {});
  const perms = getStorePermissions(tenantId);
  const store = getStoreBranding(tenantId);
  const storeColors = J(store.colors, {});
  const storeFonts = J(store.fonts, {});
  
  return {
    name: store.name || (perms.can_change_name ? null : (global.name || 'Store')),
    logo: store.logo || (perms.can_change_logo ? null : (global.logo || '')),
    tagline: store.tagline || (perms.can_change_footer ? null : (global.tagline || '')),
    colors: {
      accent: storeColors.accent || (perms.can_change_colors ? null : (gColors.accent || '#C6A15B')),
      header: storeColors.header || (perms.can_change_colors ? null : (gColors.header || '#0C0E13'))
    },
    fonts: {
      display: storeFonts.display || (perms.can_change_fonts ? null : (gFonts.display || 'Didot')),
      body: storeFonts.body || (perms.can_change_fonts ? null : (gFonts.body || 'Inter'))
    },
    permissions: {
      can_change_name: !!perms.can_change_name,
      can_change_logo: !!perms.can_change_logo,
      can_change_colors: !!perms.can_change_colors,
      can_change_fonts: !!perms.can_change_fonts,
      can_change_footer: !!perms.can_change_footer
    }
  };
}

module.exports = {
  getGlobalBranding, setGlobalBranding,
  getStorePermissions, setStorePermissions,
  getStoreBranding, setStoreBranding,
  getEffectiveBranding
};
