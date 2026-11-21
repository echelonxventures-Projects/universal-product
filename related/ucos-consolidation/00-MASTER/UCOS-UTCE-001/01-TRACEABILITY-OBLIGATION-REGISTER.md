# UCOS-UTCE-001 · Lane Obligation and Collection-Mechanism Register

One row per lane of the located lane vocabulary. `labels` are the front-matter row
labels the located relationship vocabulary maps to that lane — the mechanism by which
an artifact can lawfully declare the evidence. A lane with no label cannot be
populated by any means the repository currently provides, and its obligation is
therefore undischargeable until the vocabulary owner adds one.

| Lane | Populated | Unevidenced | Collection labels (located) | Obligation class |
|---|---|---|---|---|
| `requirement` | 95 | 1594 | `AUTHORITY`, `AUTHORITIES`, `AUTHORIZED-BY`, `GOVERNED-BY`, `TRACES-TO`, `TRACES TO` | DISCHARGEABLE |
| `architecture` | 1688 | 1 | `PARENT`, `DEPENDS-ON`, `DEPENDS ON`, `IMPLEMENTS`, `REALIZES`, `CONSUMES`, `USES`, `READS` | DISCHARGEABLE |
| `design` | 0 | 1689 | — none | MECHANISM-ABSENT |
| `implementation` | 17 | 1672 | `IMPLEMENTS`, `REALIZES` | DISCHARGEABLE |
| `source_code` | 0 | 1689 | — none | MECHANISM-ABSENT |
| `unit_test` | 0 | 1689 | `TESTS` | DISCHARGEABLE |
| `integration_test` | 0 | 1689 | — none | MECHANISM-ABSENT |
| `functional_test` | 0 | 1689 | — none | MECHANISM-ABSENT |
| `security_test` | 0 | 1689 | `SECURES` | DISCHARGEABLE |
| `certification` | 0 | 1689 | `CERTIFIES` | DISCHARGEABLE |
| `deployment` | 0 | 1689 | `DEPLOYS` | DISCHARGEABLE |
| `production` | 0 | 1689 | `PRODUCES`, `EMITS`, `WRITES`, `PUBLISHES` | DISCHARGEABLE |
| `operations` | 0 | 1689 | — none | MECHANISM-ABSENT |

## Obligation classes

| Class | Definition |
|---|---|
| `DISCHARGEABLE` | a located label produces this lane; the obligation is met by declaring the row and regenerating |
| `MECHANISM-ABSENT` | no located label produces this lane; the obligation is undischargeable until the vocabulary owner adds one |

## Located vocabularies

Lane vocabulary read from `engine/registry/models.py` — 13 lanes.

Relationship vocabulary read from `00-BOOK/tools/config.py` — 44 declared types.

