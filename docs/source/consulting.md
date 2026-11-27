# Consultancy — the parts only a person can write

## Flows

**A project and how it is billed.** A project is done for a company in the CRM and is billed one of
three ways: by **time and materials** (each approved hour at a rate, plus expenses), at a **fixed
fee** billed in instalments that never add up to more than the fee, or **not at all** (internal work).
An hour is billed at the person's own rate on that project if one is set, otherwise at the project's
rate, otherwise at the person's rate.

**A timesheet a week.** Each person has one timesheet per week, which starts on Monday. They log time
against projects and, if they like, their tasks; a day holds at most 24 hours, and time on a project
that is not billed cannot be marked billable. A draft is changed freely, then submitted. Someone
other than whoever submitted it approves it or sends it back with a reason. A week sent back is
reopened, corrected and submitted again. On approval each billable hour is priced at the person's
rate, every hour at their cost, the tasks' logged hours and the project's spend go up, and the week
no longer changes.

**Expense claims.** A person claims what they spent: the date, category, description, amount and
receipt number, optionally against a project and to be billed on to the client. A claim is
submitted, approved by someone else (the books then owe it to the person) and recorded as paid back
(the books clear it from the bank). A claim sent back is reopened and corrected.

**Invoices to clients.** An invoice is drafted from a project: its approved, billable time not yet
invoiced, up to a day you choose, one line per person and rate; its billable expenses in the
project's currency; or a fixed-fee instalment. Each entry belongs to one invoice only, so two people
drafting at once cannot bill the same time twice. Issuing it makes it owed by the client, due after
the store's payment terms, and can email it. When the client pays it is recorded as paid. Voiding an
issued invoice needs a reason, undoes its entry in the books, and makes its time and expenses ready
to bill again.

**Proposals.** A proposal is drafted, usually from a deal: its company, contact, title and currency
come with it. It has lines of time, fixed fees or expenses, and a tax rate. Sending it gives it a
private link for the client, valid for the store's number of days unless a date is set; it is
emailed to the deal's contact and the deal moves to the proposal stage. The client opens the link,
reads the proposal and accepts it by typing their name, or declines it. Staff can also record an
answer given on a call. Once accepted, the project starts for that company, billed the proposal's
way with its value as the budget, and the deal is won at that value. A proposal past its date
expires and can no longer be accepted. A declined, expired or withdrawn proposal can be made a draft
again, and its old link stops working.

**The resource plan.** People are booked onto projects by the hour, week by week, against their
weekly capacity (40 hours unless set). Anyone booked past capacity is shown as over. Utilisation
shows, for a span of weeks, each person's capacity against what was planned, what was logged and how
much of it was billable.

**The books.** Invoices to clients post to *Owed by clients*, *Fees for services*, *Expenses billed
to clients* and *Tax collected*; payments move what is owed to the bank. Expense claims post to
*Staff expenses* and *Expenses owed to staff*, cleared from the bank when paid back.

## Manual: store_admin

Open **Business Operations → ⏱️ Consulting**. Your role needs the consulting section; the Delivery
and Finance roles have it.

- **Projects**: each project with how it is billed, what is ready to bill, invoiced and paid. Open
  one to set its billing, client, currency, rate an hour, tax and fixed fee, and a person's own rate
  on it. **Draft an invoice** from what is ready, or bill a fixed-fee instalment. Projects
  themselves are added under **Business Operations → Projects**, or start when a proposal is
  accepted.
- **People and rates**: what each person is billed at, what they cost and their hours a week.
- **Timesheets**: choose a person and any day of the week, then **Open**. Add time, **Save the
  week**, and **submit** it.
- **Approvals**: weeks and expense claims waiting for you. **approve** or **reject** each one, giving
  a reason. You cannot approve your own.
- **Expenses**: claim an expense, then **submit** it; once approved, **reimburse** it when it is paid
  back.
- **Invoices**: open one to **issue** it (with an email address to send it to), record it **paid**,
  **void** it, or print it.
- **Proposals**: draft one from a deal, one line each as `kind | what | quantity | rate`, then
  **send** it. You get the client's link to copy. Record an answer given another way with **accept**
  or **decline**.
- **Plan** and **Utilisation**: book people onto projects week by week, and see how they are used.

## Manual: store_staff

Your timesheet and expense claims are under **Business Operations → ⏱️ Consulting**, if your role
has the consulting section. Open your week, log your time, save it and submit it by the end of the
week. Someone else approves it. If it is sent back, the reason is shown: reopen it, correct it and
submit it again.

## Manual: guest

A store may send you a proposal with a private link. Open it to read what is offered, for how much
and until when. To accept, type your full name and press **Accept this proposal**. To decline,
press **Decline**, giving a reason if you like. You can answer once, before the date shown.
