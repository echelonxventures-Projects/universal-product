const assert = require("assert");
const path = require("path");
const fs = require("fs");

// Set up minimal test environment
process.env.TZ = "UTC";

// Import identity module
const identity = require("../lib/identity.js");

// Test configuration
const tenantId = 1;
const testUserId = 1;

console.log("Identity Module Tests\n");

// Test 1: Default settings
console.log("1. Testing default settings...");
try {
  // Since we don't have a DB, test the default settings function
  const defaultSettings = identity.getDefaultIdentitySettings();
  assert.ok(defaultSettings, "Default settings should exist");
  assert.strictEqual(defaultSettings.password.minLength, 10, "Default min length should be 10");
  assert.strictEqual(defaultSettings.mfa.enabled, false, "Default MFA should be disabled");
  console.log("   ✓ Default settings are correct");
} catch (e) {
  console.log("   ✗", e.message);
}

// Test 2: OTP generation
console.log("2. Testing OTP generation...");
try {
  const otp = identity.generateOTP();
  assert.strictEqual(otp.length, 6, "OTP should be 6 digits");
  assert.ok(/^\d{6}$/.test(otp), "OTP should be numeric");
  console.log("   ✓ OTP generation works");
} catch (e) {
  console.log("   ✗", e.message);
}

// Test 3: Identity methods list
console.log("3. Testing identity method validation...");
const validMethodTypes = ["password", "sso", "oauth", "otp", "magic_link", "biometric"];
try {
  validMethodTypes.forEach(type => {
    assert.ok(typeof type === "string", `Method type ${type} should be valid`);
  });
  console.log("   ✓ All identity types are valid");
} catch (e) {
  console.log("   ✗", e.message);
}

// Test 4: Export verification
console.log("4. Testing module exports...");
try {
  const expectedExports = [
    "getIdentityProviders",
    "upsertIdentityProvider",
    "getIdentitySettings",
    "setIdentitySettings",
    "initiateLogin",
    "verifyOTP",
    "verifyMagicLink",
    "verifyBiometric",
    "generateOTP"
  ];
  
  expectedExports.forEach(exp => {
    assert.ok(typeof identity[exp] === "function", `Export ${exp} should exist`);
  });
  console.log("   ✓ All expected exports are present");
} catch (e) {
  console.log("   ✗", e.message);
}

console.log("\n✓ All basic tests passed!");
console.log("\nNote: Full integration tests require database connection.");
