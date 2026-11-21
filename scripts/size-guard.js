/* Size guard: no file of LX_MAX_FILE_MB (default 50) MB or more enters the repository.
   GitHub refuses files over 100 MB and warns above 50 MB; one oversized blob stays in the
   history for ever, so it is stopped before it is committed.

     node scripts/size-guard.js            every tracked file (npm test, CI)
     node scripts/size-guard.js --staged   the files staged for the next commit (pre-commit hook)

   Exit 1 names every file over the limit. Keep large data, databases, media and archives
   outside git (data/ and the project folder's archive/ are never committed). */
"use strict";
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const LIMIT_MB = Number(process.env.LX_MAX_FILE_MB) || 50;
const LIMIT = LIMIT_MB * 1024 * 1024;
const staged = process.argv.includes("--staged");
const root = execFileSync("git", ["rev-parse", "--show-toplevel"], { encoding: "utf8" }).trim();

const git = args => execFileSync("git", args, { cwd: root, encoding: "utf8", maxBuffer: 256 * 1024 * 1024 });
const over = [];
if (staged) {
  /* the staged blob's size, not the working file's: what is about to be committed */
  const files = git(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"]).split("\0").filter(Boolean);
  for (const f of files) {
    const size = Number(git(["cat-file", "-s", ":" + f]).trim());
    if (size >= LIMIT) over.push([f, size]);
  }
} else {
  for (const f of git(["ls-files", "-z"]).split("\0").filter(Boolean)) {
    let size = 0;
    try { size = fs.statSync(path.join(root, f)).size; } catch (e) { continue; }
    if (size >= LIMIT) over.push([f, size]);
  }
}

if (over.length) {
  console.error(`✗ size guard: ${over.length} file(s) of ${LIMIT_MB} MB or more ${staged ? "staged" : "tracked"}:`);
  for (const [f, s] of over) console.error(`    ${(s / 1048576).toFixed(1)} MB  ${f}`);
  console.error("  Keep large data, databases, media and archives outside git, or split the file.");
  process.exit(1);
}
console.log(`✓ size guard: no ${staged ? "staged" : "tracked"} file is ${LIMIT_MB} MB or more`);
