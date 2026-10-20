/* LUXORA Platform — telling a shopper something: an in-app notification, and an email when
   the shopper has an account with an address. The notification kind must be a row of the
   shopNotifKinds registry (an engine names the kind its capability or registry row declares);
   an unknown kind still emails but leaves no in-app note. Owners are "t<tenant>:u:<user>" for
   a signed-in shopper and "t<tenant>:s:<session>" for a guest, who has no address. */
"use strict";
const db = () => require("./db.js");
const reg = () => require("./parity-registries.js");

function tell(tid, owner, kind, title, body, link, opts) {
  const o = opts || {};
  const D = db();
  const known = reg().list("shopNotifKinds").map(x => (typeof x === "string" ? x : x.key));
  if (known.includes(String(kind || "")))
    D.run("INSERT INTO notifications(tenant_id,owner,kind,title,body,link,read,meta) VALUES(?,?,?,?,?,?,0,?)",
      Number(tid), String(owner), String(kind), String(title || "").slice(0, 200), String(body || "").slice(0, 1000), String(link || ""), JSON.stringify(o.meta || {}));
  if (o.email === false) return;
  const m = /:u:(\d+)$/.exec(String(owner));
  const u = m ? D.get("SELECT email FROM users WHERE id=? AND tenant_id=?", Number(m[1]), Number(tid)) : null;
  if (u && u.email) require("./mailer.js").deliver({ tenantId: Number(tid), channel: "email", to: u.email, kind: String(kind), subject: String(title || ""), text: String(body || "") + (link ? "\n\n" + link : "") });
}
/* the display name of an owner key, for a counterpart's eyes */
function nameOf(tid, owner) {
  const m = /:u:(\d+)$/.exec(String(owner || ""));
  const u = m ? db().get("SELECT name FROM users WHERE id=? AND tenant_id=?", Number(m[1]), Number(tid)) : null;
  return u ? String(u.name || "").split(" ")[0] : "";
}
module.exports = { tell, nameOf };
