/* LUXORA Platform — console bundles, served pre-wrapped.
   The unified console (public/js/console.js) drives the store and platform consoles'
   views without letting either bundle's top-level globals reach window. It used to fetch
   the bundle's source and compile it with new Function — which needs CSP 'unsafe-eval',
   so a real browser refused it. The server now does the wrapping: the bundle is served as
   an ordinary same-origin script that registers one factory on window.__lxBundle; the
   console calls it with its capture object as `this`. */
"use strict";
const fs = require("fs");
const path = require("path");

const SOURCES = { store: "admin.js", platform: "platform.js" };
const SUFFIX = "" +

    /* re-chrome hook: a render the bundle fires from inside a view (form save, import,
       delete…) repaints its own single-scope shell; once it settles, the one console's
       chrome is put back through window.__lxRechrome (a no-op when the bundle runs
       standalone, so platform.html/admin.html are unaffected) */
    "\n ;(function () { if (typeof render !== 'function') return; var _r = render; render = function () {" +
    "  var out = _r.apply(this, arguments);" +
    "  var done = function () { try { (window.__lxRechrome || function () { })(); } catch (e) { } };" +
    "  return out && typeof out.then === 'function' ? out.then(function (v) { done(); return v; }, function (e) { done(); throw e; }) : (done(), out);" +
    "}; })();" +
    "\n; this.nav = NAV; this.canSee = canSee; this.render = render; this.shell = shell;"
    + " this.NAVFLAT = NAVFLAT; this.NAVKEY = typeof NAVKEY === 'undefined' ? null : NAVKEY;"
    + " this.NAVSEC = typeof NAVSEC === 'undefined' ? null : NAVSEC;"
    /* the bundle's render reads its OWN `view` global (it takes no argument) and its own
       canSee reads A.allowed / P.allowed — both set by the boot this shell suppressed. So
       the shell needs handles to set them: setView drives a leaf into the bundle, and A/P
       are the state objects its boot would have filled. */
    + " this.A = typeof A === 'undefined' ? null : A; this.P = typeof P === 'undefined' ? null : P;"
    + " this.setView = v => { view = v; }; this.getView = () => view;"
    + " this.setTT = typeof TT === 'undefined' ? null : (v => { TT = v; });"
    + " this.ready = true;";

function wrap(which, pubDir) {
  const file = SOURCES[which];
  if (!file) return null;
  const src = fs.readFileSync(path.join(pubDir, "js", file), "utf8");
  return "(window.__lxBundle = window.__lxBundle || {})[" + JSON.stringify(which) + "] = function (LX_GUEST) {\"use strict\";"
    + src + SUFFIX + "\n};\n";
}

module.exports = { wrap, SOURCES };
