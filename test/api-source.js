/* The source of the live API, for tests that read it as text: the shared HTTP kit (lib/api.js) and
   every domain's own route file (lib/routes/<domain>.js), which the kit assembles. A check that
   reads only lib/api.js would pass vacuously once a handler moves to its domain's file. */
"use strict";
const fs = require("fs"), path = require("path");
module.exports = function apiSource() {
  const lib = path.join(__dirname, "..", "lib");
  const routes = path.join(lib, "routes");
  return [path.join(lib, "api.js")].concat(fs.existsSync(routes) ? fs.readdirSync(routes).filter(f => f.endsWith(".js")).sort().map(f => path.join(routes, f)) : [])
    .map(f => fs.readFileSync(f, "utf8")).join("\n");
};
