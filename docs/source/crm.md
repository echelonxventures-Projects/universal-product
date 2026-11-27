# Customer relationships — the parts only a person can write

## Flows

**Companies and people.** A store adds the companies it sells to and the people there. A contact
whose email is also a shopper's account is linked to it, so their orders and their deals meet in one
place. Who a contact is — name, email, phone — stays in the store's records, where erasure removes it;
the master knows the contact existed, their job title and their company.

**A deal.** A deal is opened for a company or a contact — or from a shopper's enquiry, whose opener
becomes the contact. It starts in the first stage of the store's pipeline and moves through the stages;
each stage carries the chance a deal there is won. Won and lost are its state: a lost deal says why and
may be reopened; a won one stays won. Every stage a deal went through is kept.

**The pipeline.** Every store starts from a standard pipeline and may set its own stages and chances.
A stage that still has open deals cannot be removed.

**The forecast.** The open deals of each month and currency, their total, the same weighted by each
stage's chance, and what was won — what a sales team plans against.

**Activities.** Calls, meetings, emails, tasks and notes are recorded against a deal, a contact or a
company. What is still to do has a due date and appears first, on the timeline and in the agenda,
until it is marked done with its outcome.

**One view of a customer.** For any shopper: their orders, what they spent, their returns, support
cases, wallet balances, segments, and their contacts, deals and activities.

**Erasure.** Erasing a person removes their account, addresses, reviews, questions, support cases,
contact record and the activities about them, as `lib/seed/erasure.json` lists; orders, payments,
deals and the other records the law obliges the store to keep stay, no longer linked to the erased
person on the master. Anything erasure could not clear is reported.

## Manual: store_admin

Open **Customer Care → 🤝 CRM**. Your role needs the crm section: the Growth role can change it,
Support can read it.

- **Pipeline**: open a deal, move it between stages with the stage list on its card, and mark it
  **Won** or **Lost** (with the reason). **Open** shows its timeline.
- **Companies** and **Contacts**: add them; open a company to see its people, deals and timeline,
  and record an activity. A contact with a shopper account has **Customer view**.
- **Agenda**: what is still to do, by due date. **Forecast**: the pipeline by month.
- To set your own stages, use `PUT /api/admin/crm/stages`; your CRM or sales tools can use every
  `/api/admin/crm/…` route with a store API key — see `docs/api/README.md`.
