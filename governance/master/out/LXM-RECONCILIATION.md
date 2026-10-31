# LXM reconciliation evidence: the 128 reconciled rows (Stages 0–10, header and directive)

Generated from `reqs.txt`; requirement text is in LXM-MASTER Part D and is not repeated here. Classes: FP fully preserved, ST strengthened, MO mandate-only, PP partially preserved, OM omitted, CF conflicting or superseded.

| Requirement | Title | SRC-0002 | SRC-0003 | Appendix A | Class | Disposition | Decision | Resolution | Stages |
|---|---|---|---|---|---|---|---|---|---|
| LXM-REQ-000001 | Document identity and release posture | S4-7, S9-10 | L5-9 | A376-382 | FP | Retained | LXM-DEC-000016 | — | STG-00 |
| LXM-REQ-000002 | Primary execution environment outside iCloud | S8 | L35, L261 | A601 | PP | Repaired | LXM-DEC-000016 | The workspace path survived; the explicit "outside iCloud" constraint is restored. | STG-00 |
| LXM-REQ-000003 | Scope is the whole owner mandate | S16-18 | L13 | — | FP | Retained | — | — | STG-00 |
| LXM-REQ-000004 | Execution, not proposal | S20 | L13 | A392 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000005 | Continuous implementation loop | S22 | L13 | A390, A396 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000006 | Expected result | S24 | L22, L365 | A406 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000007 | Sequential execution in the owner session | S28 | L17, L357 | — | FP | Retained | — | — | STG-00 |
| LXM-REQ-000008 | No routine confirmations | S29 | L18, L361 | — | FP | Retained | — | — | STG-00 |
| LXM-REQ-000009 | No premature stopping points | S30 | L79, L359 | — | PP | Repaired | — | "One successful test suite" restored as a named non-stopping point. | STG-00, STG-03 |
| LXM-REQ-000010 | Independent work is never held by an external dependency | S31 | L18, L20 | — | FP | Retained | — | — | STG-00 |
| LXM-REQ-000011 | Blocked-item protocol | S32 | L20, L363 | A921 | FP | Retained | — | — | STG-00, STG-08 |
| LXM-REQ-000012 | Durable checkpoints | S33 | L21 | — | FP | Retained | — | — | STG-00 |
| LXM-REQ-000013 | No false completion | S34 | L184, L251 | A406 | FP | Retained | — | — | STG-00, STG-12 |
| LXM-REQ-000014 | Single writer | S35 | L17, L287 | — | FP | Retained | — | — | STG-00 |
| LXM-REQ-000015 | No repetitive progress messages | S36 | L314 | — | OM | Restored | OMR-1 | Restored from SRC-0002; the closing consolidated report was retained in the combined text, the prohibition was not. | STG-00 |
| LXM-REQ-000016 | Owner-escalation conditions | S37, S39 | L20, L363 | A1082 | OM | Restored | OMR-2 | Restored and made precise per SRC-0007 §2: a closed set of escalation triggers, one consolidated packet, no routine approvals. | STG-00, STG-01, STG-05 |
| LXM-REQ-000017 | Meaning of "without interruption" | S39 | L19, L23, L37, L119 | A404-408 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000018 | Establish repository truth before any change | S45 | L27 | A580 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000019 | Physical working directory | S49 | L29 | A582 | ST | Strengthened | — | — | STG-00 |
| LXM-REQ-000020 | Branch, HEAD and remote heads | S50-51 | L29 | A583 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000021 | Working-tree state | S52 | L30 | A583 | ST | Strengthened | — | — | STG-00 |
| LXM-REQ-000022 | Inspect preservation artifacts | S53 | L30, L37 | A407 | PP | Repaired | — | Inspection (not only preservation) of preservation artifacts restored to Stage 0. | STG-00 |
| LXM-REQ-000023 | Active processes | S54 | L31 | — | FP | Retained | — | — | STG-00 |
| LXM-REQ-000024 | All open pull requests and CI runs | S55 | L32 | A584 | PP | Repaired | — | Scope widened back from PR #6 alone to every open pull request. | STG-00 |
| LXM-REQ-000025 | Release register | S56 | L33 | A585 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000026 | Decision records, registries and test procedures | S57 | L33 | A586, A587, A590, A592, A594 | MO | Expanded-from-mandate | — | Decision records (with MD-1–MD-5 meanings), feature and capability registries and test procedures restored from Appendix A §3. | STG-00 |
| LXM-REQ-000027 | Historical remote state | S61-63, S66 | L35 | A611 | FP+CF | Historical | — | Retained as historical evidence only; superseded by the PR-053 candidate `39ed4d6` and run 40990327443 (LXM-CHG register). | STG-00 |
| LXM-REQ-000028 | Owner session identity | S64 | L3 | — | FP | Retained | — | — | STG-00 |
| LXM-REQ-000029 | Never infer a reported change is committed | S68 | L57 | A597 | PP+CF | Repaired | — | The instruction is retained; the reported fact "ten version changes, jsdom/dom-selector 9→10" is superseded by commit `39ed4d6` (integrity-only, 0 version changes) and moved to the LXM-CHG register. | STG-00 |
| LXM-REQ-000030 | Forbidden Git operations | S72 | L37 | A619-628 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000031 | Preserve unrelated and uncommitted work | S73 | L37 | A617, A627-628 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000032 | Preserve original and preservation workspaces | S74 | L37, L277 | A407, A626 | FP | Retained | — | — | STG-00, STG-15 |
| LXM-REQ-000033 | No production or protected data modification | S75 | L23, L37, L131 | A632, A638 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000034 | Generated artifacts | S76 | L37 | A636 | FP | Retained | — | — | STG-00, STG-13 |
| LXM-REQ-000035 | No secrets committed | S77 | L119, L234 | A566, A923 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000036 | No merge or deploy | S78 | L23, L243 | A638 | FP | Retained | — | — | STG-00 |
| LXM-REQ-000037 | Unsafe or unexpected state | S80 | L39 | A613 | ST | Strengthened | — | — | STG-00 |
| LXM-REQ-000038 | Record the baseline before modifying | S82 | L27 | A1070 | PP | Repaired | LXM-DEC-000005 | The record destination is restored; per K5 the baseline is recorded before modification without waiting for confirmation. | STG-00 |
| LXM-REQ-000039 | Index-lock protection | — | L37 | A630 | ST | Strengthened | — | — | STG-00 |
| LXM-REQ-000040 | Expected workspace as historical fact | — | L35 | A601 | ST | Strengthened | — | — | STG-00 |
| LXM-REQ-000041 | Finish technology governance first | S86 | L43 | — | FP | Retained | — | — | STG-01 |
| LXM-REQ-000042 | Technology governance review scope | S88 | L43 | — | ST | Strengthened | — | — | STG-01 |
| LXM-REQ-000043 | Technology governance capabilities | S92-98, S100, S102-103 | L47-53 | — | FP | Retained | — | — | STG-01 |
| LXM-REQ-000044 | Technology-assumption and hardcoding detection | S99 | L52 | A704-729 | PP | Repaired | — | Unjustified-hardcoding detection restored as a technology-governance check (it had moved to the business-policy audit only). | STG-01 |
| LXM-REQ-000045 | Independent approval of production-affecting changes | S101 | L50 | — | PP | Repaired | — | The weakening qualifier "where required" is removed; the unconditional source requirement is restored. | STG-01 |
| LXM-REQ-000046 | Authorized re-resolution | S107 | L55-57 | — | FP | Historical | — | Completed in commit `39ed4d6` (integrity-only re-resolution); verify, do not redo. | STG-01 |
| LXM-REQ-000047 | Lockfile integrity verification | S109 | L57 | — | ST | Strengthened | — | — | STG-01 |
| LXM-REQ-000048 | No forced incompatible versions | S111 | L57 | — | PP | Repaired | LXM-DEC-000011 | "Do not force incompatible versions" restored. | STG-01 |
| LXM-REQ-000049 | PR-053 verification chain | S113 | L59 | — | ST | Strengthened | — | — | STG-01 |
| LXM-REQ-000050 | Per-finding classification of technology assumptions | S115 | L59 | A717-725 | OM | Restored | OMR-3 | Restored from SRC-0002; Appendix A's seven-way classification covers business policy only. | STG-01 |
| LXM-REQ-000051 | Record PR-053 evidence | S119 | L61 | — | FP | Retained | — | — | STG-01 |
| LXM-REQ-000052 | Commit gate | S121 | L61, L239 | A1128 | PP | Repaired | LXM-DEC-000002 | "Commit only after required local checks pass" restored to Stage 1; CI acceptance follows K2. | STG-01, STG-14 |
| LXM-REQ-000053 | No earlier-commit CI evidence | S123 | L59, L249 | A1226 | FP | Retained | — | — | STG-01 |
| LXM-REQ-000054 | Candidate freeze during CI | S125 | L17 | — | OM | Restored | OMR-4; LXM-DEC-000004 | Restored and reconciled with LXM-REQ-000010 by K4: the candidate is frozen; only non-mutating, pre-scoped analysis may proceed. | STG-01 |
| LXM-REQ-000055 | PR-053 is not mandate compliance | S127 | L63 | — | FP | Retained | — | — | STG-01 |
| LXM-REQ-000056 | Mandate as parent contract | S131, S135 | L65-67 | A370 | FP | Retained | — | — | STG-02 |
| LXM-REQ-000057 | Verify the mandate's identity and governance | S133 | L67 | — | PP | Repaired | — | "Status and governance relationships" restored. | STG-02 |
| LXM-REQ-000058 | Inspect what the mandate references | S137 | L33, L75 | A580-595 | FP | Retained | — | — | STG-02 |
| LXM-REQ-000059 | Conformance matrix | S139, S143-145, S147-149 | L71 | A941-962 | FP | Retained | — | — | STG-02 |
| LXM-REQ-000060 | Matrix field: dependencies | S146 | — | A955 | OM | Restored | OMR-5 | Restored from SRC-0002 to the conformance matrix (Appendix A has it for the feature matrix only). | STG-02 |
| LXM-REQ-000061 | Matrix field: remaining work and consequence | S150 | L71 | A962 | PP | Repaired | — | "Remaining work" and "consequence" restored beside the closure condition. | STG-02 |
| LXM-REQ-000062 | No competing registers | S152 | L71 | A642-648 | FP | Retained | — | — | STG-02 |
| LXM-REQ-000063 | What is not proof | S154 | L22 | A406, A444 | FP | Retained | — | — | STG-02 |
| LXM-REQ-000064 | Reconcile owner decisions | — | L69 | A646, A1076-1080 | ST | Strengthened | — | — | STG-02 |
| LXM-REQ-000065 | Gap-inventory scope (core) | S160-162, S164-169, S171 | L75, L93 | A1088 | FP | Retained | — | — | STG-03 |
| LXM-REQ-000066 | Gap-inventory scope: financial exceptions | S163 | — | A523-535, A1088 | MO | Expanded-from-mandate | — | — | STG-03 |
| LXM-REQ-000067 | Gap-inventory scope: security, operations and compliance | S170, S171, S172-174 | L75 | A1088 | PP | Repaired | — | Areas only verified later are restored to the inventory scope. | STG-03 |
| LXM-REQ-000068 | Inventory from source | S176 | L75 | A683 | FP | Retained | — | — | STG-03 |
| LXM-REQ-000069 | What the inventory identifies | S178 | L77 | A1092 | MO | Expanded-from-mandate | — | — | STG-03 |
| LXM-REQ-000070 | Classify every finding | S180 | — | A838, A1013 | OM | Restored | OMR-6 | Restored from SRC-0002; Appendix A classifies only monetary and security findings. | STG-03 |
| LXM-REQ-000071 | Do not stop at the inventory | S182 | L79 | A1084 | FP | Retained | — | — | STG-03 |
| LXM-REQ-000072 | Observation states | — | L77 | A1090 | ST | Strengthened | — | — | STG-03 |
| LXM-REQ-000073 | Reuse the configuration foundation | S186 | L83 | A403, A658 | ST | Strengthened | — | — | STG-04 |
| LXM-REQ-000074 | Configuration definition properties | S190-194, S196-200 | L85, L87 | A660-679 | FP/ST | Strengthened | — | — | STG-04 |
| LXM-REQ-000075 | Dependency compatibility | S195 | L85 | A667 | MO | Expanded-from-mandate | — | — | STG-04 |
| LXM-REQ-000076 | Definition links | S201 | — | A671, A685-694 | MO | Expanded-from-mandate | — | — | STG-04 |
| LXM-REQ-000077 | Administration APIs and UI | S203 | L85 | A677 | FP | Retained | — | — | STG-04 |
| LXM-REQ-000078 | Usable in the running platform | S205 | — | A422, A476 | MO | Expanded-from-mandate | — | — | STG-04 |
| LXM-REQ-000079 | Seed lifecycle | S207 | L87 | A446, A698 | FP | Retained | — | — | STG-04 |
| LXM-REQ-000080 | Configuration cannot bypass invariants | S209 | — | A405, A535, A1110, A1148, A1188 | MO | Expanded-from-mandate | — | — | STG-04 |
| LXM-REQ-000081 | Test runtime behavior | S211 | L87 | A444 | FP | Retained | — | — | STG-04 |
| LXM-REQ-000082 | Configuration states and policy hardcoding audit | — | L87, L89 | A673, A704-729 | ST | Strengthened | — | — | STG-04 |
| LXM-REQ-000083 | Monetary inspection scope | S215 | L93, L99 | A588, A836 | MO | Expanded-from-mandate | — | — | STG-05 |
| LXM-REQ-000084 | One money model | S217 | L93 | A792 | FP | Retained | — | — | STG-05 |
| LXM-REQ-000085 | Exact monetary model | S221-223, S225-228, S232 | L95, L97 | A794-811 | FP/ST | Strengthened | — | — | STG-05 |
| LXM-REQ-000086 | Conversion provenance | S224 | L95 | A435 | MO | Expanded-from-mandate | — | — | STG-05 |
| LXM-REQ-000087 | Exception resolution with rationale | S229 | L95 | A533 | MO | Expanded-from-mandate | — | — | STG-05 |
| LXM-REQ-000088 | Financial allocation | S230 | L93 | A429-432, A847-848 | MO | Expanded-from-mandate | — | — | STG-05 |
| LXM-REQ-000089 | Reconciliation and discrepancy workflows | S231 | L93 | A436, A527, A533, A858 | MO | Expanded-from-mandate | — | — | STG-05 |
| LXM-REQ-000090 | Every monetary path | S234 | L93, L97 | A834 | FP | Retained | — | — | STG-05 |
| LXM-REQ-000091 | Configurable means applied | S236 | L75, L87 | A420, A442, A444 | MO | Expanded-from-mandate | — | — | STG-05 |
| LXM-REQ-000092 | Policy-version traceability | S238 | L97 | A446, A804 | FP | Retained | — | — | STG-05 |
| LXM-REQ-000093 | MD-1–MD-5 handling | S242, S246-248, S250, S252 | L99 | A586, A866 | FP | Retained | LXM-DEC-000012 | — | STG-05 |
| LXM-REQ-000094 | Decision packets | S249 | L99 | A1082 | MO | Expanded-from-mandate | — | — | STG-05 |
| LXM-REQ-000095 | Business-rule domains | S258-266 | L103 | A499 | FP | Retained | — | — | STG-06 |
| LXM-REQ-000096 | Promotion stacking | S260 | L103 | A430 | MO | Expanded-from-mandate | — | — | STG-06 |
| LXM-REQ-000097 | Exception-handling rules | S266 | L103 | A436 | PP | Repaired | — | Non-financial exception-handling rules restored. | STG-06 |
| LXM-REQ-000098 | Business-specific and future rules | S267 | L103 | A438, A515 | MO | Expanded-from-mandate | — | — | STG-06 |
| LXM-REQ-000099 | Rule engines and extension | S269, S273, S275, S277 | L103, L105 | A450, A519, A521 | FP | Retained | — | — | STG-06 |
| LXM-REQ-000100 | Rule governance behavior | S271 | L105 | A508 | MO | Expanded-from-mandate | — | — | STG-06 |
| LXM-REQ-000101 | Profile mechanism | S281 | L109, L113 | A474 | FP | Retained | — | — | STG-07 |
| LXM-REQ-000102 | Reuse platform foundations | S283 | L109 | A741, A749, A751, A757 | MO | Expanded-from-mandate | — | — | STG-07 |
| LXM-REQ-000103 | Composition concerns (core) | S287-289, S291-295 | L109 | A742-753 | FP | Retained | — | — | STG-07 |
| LXM-REQ-000104 | Composition concerns (restored) | S287, S290, S291, S294, S296 | L109 | A742, A745, A746, A752, A754-755 | MO | Expanded-from-mandate | — | — | STG-07 |
| LXM-REQ-000105 | No closed list of business models | S298 | L69, L109 | A472, A493, A759 | MO | Expanded-from-mandate | LXM-DEC-000007 | — | STG-07 |
| LXM-REQ-000106 | Representative profiles | S302-309, S311 | L111, L113 | A765-778 | FP | Retained | LXM-DEC-000007 | — | STG-07 |
| LXM-REQ-000107 | Templates are not solutions | S313 | L113 | A478, A780 | FP | Retained | — | — | STG-07 |
| LXM-REQ-000108 | Marketplace first, foundation universal | S315 | L113 | A493, A784 | ST | Strengthened | — | — | STG-07 |
| LXM-REQ-000109 | Provider-neutral orchestration | S319 | — | A572, A874 | MO | Expanded-from-mandate | — | — | STG-08 |
| LXM-REQ-000110 | Provider adapters and operations | S321, S325, S327-335, S337, S340, S342, S344 | L117, L119 | A539-572, A878-923 | FP | Retained | LXM-DEC-000007 | — | STG-08 |
| LXM-REQ-000111 | Payment-method capability discovery | S326 | L117 | A549, A559 | MO | Expanded-from-mandate | — | — | STG-08 |
| LXM-REQ-000112 | Provider routing and operational controls | S336 | L117 | A561, A562 | MO | Expanded-from-mandate | — | — | STG-08 |
| LXM-REQ-000113 | Provider audit and conformance | S338 | L117 | A562, A933 | MO | Expanded-from-mandate | — | — | STG-08 |
| LXM-REQ-000114 | Feature-to-test mapping | S348 | L123 | A947-962 | ST | Strengthened | — | — | STG-09 |
| LXM-REQ-000115 | Role journeys | S350, S355-363 | L125 | A970-984 | FP | Retained | — | — | STG-09 |
| LXM-REQ-000116 | Registration and session lifecycle | S354 | L125 | A974 | MO | Expanded-from-mandate | — | — | STG-09 |
| LXM-REQ-000117 | Notification journeys | S364 | L125 | — | PP | Repaired | — | Notification journeys restored beside operational failure paths. | STG-09 |
| LXM-REQ-000118 | Test states and truthful status | S366 | L125 | A986, A988 | MO | Expanded-from-mandate | — | — | STG-09 |
| LXM-REQ-000119 | Responsive, accessible, supported browsers | S368 | L125 | A988, A990 | MO | Expanded-from-mandate | — | — | STG-09 |
| LXM-REQ-000120 | Coverage honesty | S370, S372 | L123, L125 | A966, A990 | FP | Retained | — | — | STG-09 |
| LXM-REQ-000121 | Security and data verification | S376, S380-382, S388, S390-392 | L127, L129 | A996-1011 | FP | Retained | — | — | STG-10 |
| LXM-REQ-000122 | Secret rotation | S383 | L129 | A1001 | MO | Expanded-from-mandate | — | — | STG-10 |
| LXM-REQ-000123 | Webhook idempotency | S384 | L129 | A1002-1003 | MO | Expanded-from-mandate | — | — | STG-10 |
| LXM-REQ-000124 | Configuration authorization | S385 | L129 | A1007 | MO | Expanded-from-mandate | — | — | STG-10 |
| LXM-REQ-000125 | Sensitive data | S386 | L129 | A1006, A1008 | MO | Expanded-from-mandate | — | — | STG-10 |
| LXM-REQ-000126 | Resource exhaustion | S387 | L129 | A1005 | MO | Expanded-from-mandate | — | — | STG-10 |
| LXM-REQ-000127 | Migration upgrade compatibility | S389 | L129 | A1027 | MO | Expanded-from-mandate | — | — | STG-10 |
| LXM-REQ-000128 | Isolated and per-profile testing | S394, S396, S398 | L131 | A1013, A1025, A1031 | ST | Strengthened | — | — | STG-10 |
