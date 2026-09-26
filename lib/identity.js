const db = require("./db.js");
const sec = require("./security.js");
const { get, run, all } = db;

/* =================== Identity Provider Management =================== */

function getIdentityProviders(tenantId) {
  return all("SELECT * FROM identity_providers WHERE tenant_id=? ORDER BY enabled DESC, provider_type, display_order", tenantId);
}

function getIdentityProvider(tenantId, id) {
  return get("SELECT * FROM identity_providers WHERE tenant_id=? AND id=?", tenantId, id);
}

function upsertIdentityProvider(tenantId, body) {
  const { id, provider_type, name, enabled, config, display_order } = body;
  
  if (id) {
    run(`UPDATE identity_providers 
         SET provider_type=?, name=?, enabled=?, config=?, display_order=?, updated_at=datetime('now') 
         WHERE tenant_id=? AND id=?`,
      provider_type, name, enabled ? 1 : 0, JSON.stringify(config || {}), display_order || 0, tenantId, id);
    return { ok: true, id };
  }
  
  const newId = "idp_" + Math.random().toString(36).slice(2, 10);
  run(`INSERT INTO identity_providers 
       (id, tenant_id, provider_type, name, enabled, config, display_order, created_at, updated_at) 
       VALUES(?,?,?,?,?,?,?,?,?)`,
    newId, tenantId, provider_type, name, enabled ? 1 : 0, JSON.stringify(config || {}), display_order || 0, 'now', 'now');
  return { ok: true, id: newId };
}

function deleteIdentityProvider(tenantId, id) {
  run("DELETE FROM identity_providers WHERE tenant_id=? AND id=?", tenantId, id);
  return { ok: true };
}

/* =================== Identity Methods (User-level) =================== */

function getUserIdentityMethods(userId) {
  return all("SELECT * FROM user_identity_methods WHERE user_id=? ORDER BY is_primary DESC, created_at", userId);
}

function getUserIdentityMethod(userId, methodId) {
  return get("SELECT * FROM user_identity_methods WHERE user_id=? AND method_id=?", userId, methodId);
}

function linkIdentityMethod(userId, method_type, identifier, metadata, isPrimary) {
  const methodId = "idm_" + Math.random().toString(36).slice(2, 10);
  
  if (isPrimary) {
    run("UPDATE user_identity_methods SET is_primary=0 WHERE user_id=?", userId);
  }
  
  run(`INSERT INTO user_identity_methods 
       (user_id, method_id, method_type, identifier, metadata, is_primary, created_at, updated_at) 
       VALUES(?,?,?,?,?,?,datetime('now'),datetime('now'))`,
    userId, methodId, method_type, identifier, JSON.stringify(metadata || {}), isPrimary ? 1 : 0);
  
  return { ok: true, method_id: methodId };
}

function unlinkIdentityMethod(userId, methodId) {
  const existing = get("SELECT * FROM user_identity_methods WHERE user_id=? AND method_id=?", userId, methodId);
  if (!existing) return { ok: false, error: "Method not found" };
  
  // Cannot unlink last method
  const otherMethods = all("SELECT COUNT(*) as cnt FROM user_identity_methods WHERE user_id=? AND method_id!=?", userId, methodId);
  if (otherMethods[0].cnt == 0) {
    return { ok: false, error: "Cannot unlink last identity method" };
  }
  
  run("DELETE FROM user_identity_methods WHERE user_id=? AND method_id=?", userId, methodId);
  return { ok: true };
}

function setPrimaryMethod(userId, methodId) {
  run("UPDATE user_identity_methods SET is_primary=0 WHERE user_id=?", userId);
  run("UPDATE user_identity_methods SET is_primary=1 WHERE user_id=? AND method_id=?", userId, methodId);
  return { ok: true };
}

/* =================== Authentication Flow =================== */

function initiateLogin(tenantId, email, methodType, config) {
  // Check if user exists
  const user = get("SELECT * FROM users WHERE tenant_id=? AND email=?", tenantId, email.toLowerCase());
  
  if (!user) {
    return { ok: false, error: "User not found", action: "register" };
  }
  
  // Check if provider is enabled for this method
  const provider = get(
    "SELECT * FROM identity_providers WHERE tenant_id=? AND provider_type=? AND enabled=1",
    tenantId, methodType
  );
  
  if (!provider) {
    return { ok: false, error: "Authentication method not enabled" };
  }
  
  switch (methodType) {
    case 'password':
      // Password login - handled by existing apiLogin
      return { ok: true, action: "password", user };
      
    case 'otp':
      // Generate OTP
      const otp = generateOTP();
      const expiresAt = Date.now() + (config?.expiryMinutes || 10) * 60000;
      
      run(`INSERT INTO identity_otps 
           (user_id, identifier, otp, expires_at, attempts, verified, created_at) 
           VALUES(?,?,?,?,0,0,datetime('now'))`,
        user.id, email, otp, expiresAt);
      
      return { ok: true, action: "otp_sent", identifier: email };
      
    case 'magic_link':
      // Generate magic link token
      const token = Math.random().toString(36).slice(2, 15);
      const tokenExpires = Date.now() + (config?.expiryMinutes || 15) * 60000;
      
      run(`INSERT INTO identity_magic_links 
           (user_id, identifier, token, expires_at, used_at) 
           VALUES(?,?,?,datetime('now'),NULL)`,
        user.id, email, token, tokenExpires);
      
      return { 
        ok: true, 
        action: "magic_link_sent", 
        identifier: email, 
        link: `${config?.baseUrl || ''}/auth/magic?token=${token}`
      };
      
    case 'biometric':
      // Challenge for biometric auth
      const challenge = Math.random().toString(36).slice(2, 15);
      run(`INSERT INTO identity_biometric_challenges 
           (user_id, challenge, expires_at, verified) 
           VALUES(?,?,datetime('now'),0)`,
        user.id, challenge, Date.now() + 300000); // 5 minutes
      
      return { ok: true, action: "biometric_challenge", challenge };
      
    case 'sso':
      // SSO is already handled - just return provider info
      return { 
        ok: true, 
        action: "sso_redirect", 
        provider: {
          id: provider.id,
          type: provider.provider_type,
          name: provider.name,
          config: JSON.parse(provider.config || '{}')
        }
      };
      
    case 'oauth':
      return { 
        ok: true, 
        action: "oauth_redirect", 
        provider: {
          id: provider.id,
          type: provider.provider_type,
          name: provider.name,
          config: JSON.parse(provider.config || '{}')
        }
      };
      
    default:
      return { ok: false, error: "Unknown authentication method" };
  }
}

function verifyOTP(userId, identifier, otp) {
  const record = get(
    "SELECT * FROM identity_otps WHERE user_id=? AND identifier=? AND verified=0 AND expires_at>? AND attempts<5",
    userId, identifier.toLowerCase(), Date.now()
  );
  
  if (!record) {
    return { ok: false, error: "Invalid or expired OTP" };
  }
  
  // Compare OTP (insecure for demo, use hmac in prod)
  if (record.otp !== otp) {
    run("UPDATE identity_otps SET attempts=attempts+1 WHERE id=?", record.id);
    return { ok: false, error: "Invalid OTP" };
  }
  
  run("UPDATE identity_otps SET verified=1 WHERE id=?", record.id);
  return { ok: true };
}

function verifyMagicLink(userId, token) {
  const record = get(
    "SELECT * FROM identity_magic_links WHERE user_id=? AND token=? AND used_at IS NULL AND expires_at>?",
    userId, token, Date.now()
  );
  
  if (!record) {
    return { ok: false, error: "Invalid or expired token" };
  }
  
  run("UPDATE identity_magic_links SET used_at=datetime('now') WHERE id=?", record.id);
  return { ok: true };
}

function verifyBiometric(userId, challenge, assertion) {
  const record = get(
    "SELECT * FROM identity_biometric_challenges WHERE user_id=? AND challenge=? AND verified=0 AND expires_at>?",
    userId, challenge, Date.now()
  );
  
  if (!record) {
    return { ok: false, error: "Invalid or expired challenge" };
  }
  
  // Verify biometric assertion (would use WebAuthn in real impl)
  const valid = validateBiometricAssertion(assertion);
  
  if (!valid) {
    return { ok: false, error: "Biometric verification failed" };
  }
  
  run("UPDATE identity_biometric_challenges SET verified=1 WHERE id=?", record.id);
  return { ok: true };
}

function generateOTP() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

function validateBiometricAssertion(assertion) {
  // Placeholder - real implementation would validate WebAuthn
  return assertion && assertion.clientDataJSON && assertion.authenticatorData;
}

/* =================== Settings =================== */

function getIdentitySettings(tenantId) {
  const row = get("SELECT value FROM settings WHERE tenant_id=? AND key='identity_settings'", tenantId);
  return row ? JSON.parse(row.value) : getDefaultIdentitySettings();
}

function setIdentitySettings(tenantId, settings) {
  run("INSERT OR REPLACE INTO settings (tenant_id,key,value) VALUES(?,?,?)", 
    tenantId, 'identity_settings', JSON.stringify(settings));
  return { ok: true };
}

function getDefaultIdentitySettings() {
  return {
    password: {
      minLength: 10,
      requireUppercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
      expiryDays: 0,
      maxHistory: 5
    },
    mfa: {
      enabled: false,
      requireForAdmin: true,
      requireForStaff: false,
      methods: ['totp', 'sms']
    },
    session: {
      timeoutMinutes: 120,
      maxConcurrent: 3,
      rememberMeDays: 30
    },
    login: {
      maxAttempts: 5,
      lockoutMinutes: 30,
      allowGuestCheckout: true
    }
  };
}

module.exports = {
  getIdentityProviders,
  getIdentityProvider,
  upsertIdentityProvider,
  deleteIdentityProvider,
  
  getUserIdentityMethods,
  getUserIdentityMethod,
  linkIdentityMethod,
  unlinkIdentityMethod,
  setPrimaryMethod,
  
  initiateLogin,
  verifyOTP,
  verifyMagicLink,
  verifyBiometric,
  
  getIdentitySettings,
  setIdentitySettings,
  
  generateOTP,
  validateBiometricAssertion,
  getDefaultIdentitySettings
};
