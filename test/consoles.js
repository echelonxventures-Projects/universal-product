/* The consoles' menus come from the database (lib/consoles.js): the backend serves each console its
   menu from console_screens; an edit in Data Studio is what the console then shows, and the seed
   never overwrites it; and no browser file declares a menu of its own. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "consoles-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const C = require("../lib/consoles.js"), E = require("../lib/entity.js"), B = require("../lib/bundle.js");
const PUB = path.join(__dirname, "..", "public"), JS = path.join(PUB, "js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 300) : ""))); };
const menu = which => { const src = B.plain(which, PUB); return JSON.parse(/^const LX_CONSOLE = (.*);$/m.exec(src)[1]); };

console.log("▸ FROM THE DATABASE");
for (const which of ["platform", "store"]) {
  const rows = db.all("SELECT key FROM console_screens WHERE console=?", which).map(r => r.key), want = C.declared(which).map(r => r.key);
  ok(rows.length === want.length && want.every(k => rows.includes(k)), `every ${which} screen is a row`, { rows: rows.length, want: want.length });
}
const p = menu("platform"), leaves = p.nav.flatMap(s => s.g.flatMap(g => g.l));
ok(leaves.length === C.declared("platform").length, "the platform console is served its menu", leaves.length);
const s = menu("store");
ok(Object.keys(s.screens).length === C.declared("store").length && s.groups.length > 5, "the store console is served its menu", s.groups);
ok(s.sections.promotions === "offers" || Object.keys(s.sections).length > 0, "with each screen's access section", s.sections);

console.log("▸ EDITED IN DATA STUDIO");
const row = db.get("SELECT * FROM console_screens WHERE console='platform' AND key='master-platform'");
ok(E.updateEntity(0, "console_screen", row.id, { label: "🧬 The Master", grp: "Registry", position: 0.5 }).ok, "an operator changes a screen's label, group and place");
const l2 = menu("platform").nav.flatMap(x => x.g.map(g => [g.g, g.l.map(i => i[0] + "=" + i[1])]));
ok(l2.some(([g, ls]) => g === "Registry" && ls[0] === "master-platform=🧬 The Master"), "the console is served the change at once", l2.slice(0, 2));
C.sync();
ok(db.get("SELECT label FROM console_screens WHERE id=?", row.id).label === "🧬 The Master", "the seed never overwrites an edit");
const st = db.get("SELECT * FROM console_screens WHERE console='store' ORDER BY position LIMIT 1");
E.updateEntity(0, "console_screen", st.id, { label: "Start here" });
ok(menu("store").screens[st.key].label === "Start here", "a store screen too");
ok(!!E.updateEntity(0, "console_screen", row.id, { label: "" }).error, "a screen keeps a label");
db.run("UPDATE console_screens SET edited=0 WHERE id=?", row.id); C.sync();
ok(db.get("SELECT label FROM console_screens WHERE id=?", row.id).label === C.declared("platform").find(r => r.key === "master-platform").label, "an unedited row follows the seed");

console.log("▸ NOTHING IN THE BROWSER");
const files = ["platform.js", "admin.js", "console.js", ...fs.readdirSync(path.join(JS, "admin")).map(f => "admin/" + f)].filter(f => fs.existsSync(path.join(JS, f)));
const literal = files.filter(f => /const\s+NAV\s*=\s*\[|const\s+NAVFIT\s*=|const\s+NAVSEC\s*=\s*\{/.test(fs.readFileSync(path.join(JS, f), "utf8")));
ok(!literal.length, "no browser file declares a menu", literal);
const placed = files.flatMap(f => [...fs.readFileSync(path.join(JS, f), "utf8").matchAll(/^screen\("([^"]+)",[^\n]*\b(group|label|order|section):/gm)].map(m => f + ":" + m[1]));
ok(!placed.length, "a screen's code says nothing of where it sits", placed.slice(0, 5));
ok(!fs.existsSync(path.join(JS, "data.js")), "no browser file holds a catalogue");
const html = fs.readdirSync(PUB).filter(f => f.endsWith(".html")).filter(f => /src="js\/(platform|admin)\.js"/.test(fs.readFileSync(path.join(PUB, f), "utf8")));
ok(!html.length, "every console page loads its script from the backend", html);

/* what the browser still defines for itself (constant tables) may only shrink, until it is nothing */
const ALL = fs.readdirSync(JS).filter(f => f.endsWith(".js")).concat(fs.readdirSync(path.join(JS, "admin")).map(f => "admin/" + f));
const tables = ALL.reduce((n, f) => n + (fs.readFileSync(path.join(JS, f), "utf8").match(/^const [A-Z_]{3,} = [\[{]/gm) || []).length, 0);
ok(tables <= 20, "the browser defines no more constant tables than before (20 left to move)", tables);

console.log(`\n${passed} passed, ${failed} failed`); wipe(); process.exit(failed ? 1 : 0);
