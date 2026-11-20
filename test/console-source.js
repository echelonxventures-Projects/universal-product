/* The store console's source, for tests that read it as text: the console shell
   (public/js/admin.js) and every domain's own console file (public/js/admin/<domain>.js), which
   the bundle runs in the same scope (lib/bundle.js). A check that reads only admin.js would pass
   vacuously once a screen moves to its domain's file. */
"use strict";
const fs = require("fs"), path = require("path");
module.exports = function consoleSource() {
  const js = path.join(__dirname, "..", "public", "js");
  const dir = path.join(js, "admin");
  return [path.join(js, "admin.js")].concat(fs.existsSync(dir) ? fs.readdirSync(dir).filter(f => f.endsWith(".js")).sort().map(f => path.join(dir, f)) : [])
    .map(f => fs.readFileSync(f, "utf8")).join("\n");
};
