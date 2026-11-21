# U46 — Workforce & HRMS Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U46-workforce` |
| Layer | L5 Business Capability |
| Domain | 05 Operations |
| Steward | `ucos:org:ops-workforce` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P4 |
| Depends on | U11 Party (people), U10 Org (positions, departments, legal employers), U13 Temporal (shifts, rosters, leave, holiday calendars, payroll periods, attendance), U17 Resource (people as schedulable resources), U30 Ledger (payroll postings), U29 Payment (salary payouts), U31 Tax (TDS/withholding), U66 Privacy (employee data), U89 Contract (employment contracts), U56 Learning (training), U09 Identity (joiner–mover–leaver provisioning) |
| Depended on by | U109 Contact Centre (WFM), U82 Field Service (technicians), U105 Workplace, U106 T&E, U32 (sales incentives), U103 (board/management roles), U98 (social metrics) |
| Master references | §6.2 U46 |

> Workforce owns **people employed or engaged by an organisation**: employment records, positions and org charts, hiring (requisitions, candidates, offers), onboarding/offboarding (JML with Identity), time and attendance, shifts and rosters, leave, performance and goals, compensation, and payroll calculation with statutory deductions per jurisdiction (payroll engines as regional packs/adapters).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| WRK-L1 | Employee data is confidential and purpose-bound; managers see only their reports; sensitive data (health, biometrics, bank) is restricted. | Cedar relationship policies + classification. |
| WRK-L2 | Working time, leave and rest rules follow the jurisdiction and contract (India Shops & Establishments/labour codes, UAE Labour Law, EU WTD). | Rule packs per jurisdiction in U53; roster validation. |
| WRK-L3 | Payroll results are reproducible from inputs (attendance, components, rules version) and posted to Ledger; payslips are documents (U42). | Payroll run immutability + postings. |
| WRK-L4 | Leavers lose access at the termination TimePoint (JML automation). | U09 deprovisioning trigger. |

## 2. Objects
`Employee { party, employer (legal entity), position, manager, employment {type, start: LocalDate, end?: LocalDate}, workLocation, calendar (U13), compensation, bank, statutory ids }` · `Position { department, grade, cost centre, headcount }` · `JobRequisition`, `Candidate`, `Offer` · `Shift { pattern, roster, slot: TimeRange }` · `AttendanceRecord { employee, in/out: TimePoint, source (biometric/mobile/geo-fence) }` · `LeaveRequest { type, range: TimeRange, status, balance impact }` · `Goal`/`Review` · `PayrollRun { entity, period (payroll calendar), inputs hash, results, status }` · `Payslip`.

## 3. Commands, Events, APIs
Commands: `Hire`, `Onboard`, `Transfer`, `Terminate`, `PublishRoster`, `ClockIn|Out`, `RequestLeave`, `ApproveLeave`, `RunPayroll`, `ApprovePayroll`, `IssuePayslips`, `SetGoals`, `SubmitReview`.
Events: `workforce.employee.hired|transferred|terminated`, `workforce.leave.approved`, `workforce.payroll.approved`.
```text
POST /v1/workforce/employees   POST /v1/workforce/rosters   POST /v1/workforce/attendance   POST /v1/workforce/leave
POST /v1/workforce/payroll-runs
```

## 4. Gaps, UI
```prolog
gap(payroll_rules_missing, T, J) :- tenant(T), employer_in(T, J), capability(T, workforce.payroll), not payroll_pack(J).
```
AI: rostering optimisation, resume screening (with fairness constraints and human decision), HR helpdesk agent. Views: employee self-service (payslips, leave, attendance), manager team view, org chart, roster planner, payroll cockpit, recruiting pipeline. T2.

## Appendix
- **C.** 0.1.0.
