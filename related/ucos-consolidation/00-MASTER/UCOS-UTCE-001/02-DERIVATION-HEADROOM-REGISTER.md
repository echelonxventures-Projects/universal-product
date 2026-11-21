# UCOS-UTCE-001 · Derivation Headroom

How many lane entries the edges ALREADY in the certified corpus would support, and
how many of those the generator already wrote. `derivable, not written` is headroom
that requires no new evidence — only that the located generator write what its own
vocabulary already declares. **This programme writes none of it.** Every row cites
located edge identifiers so the count is auditable against the corpus.

| Rule | Located type | Read | Lane | Artifacts supported | Already written | Derivable, not written | Cited edges |
|---|---|---|---|---|---|---|---|
| `UTCE-DR-01` | `Parent` | from | `architecture` | 1688 | 1688 | 0 | `UEDGE-000000002`, `UEDGE-000000005`, `UEDGE-000000919` |
| `UTCE-DR-02` | `Depends-On` | from | `architecture` | 298 | 298 | 0 | `UEDGE-000000001`, `UEDGE-000000004`, `UEDGE-000000007` |
| `UTCE-DR-03` | `Authorized-By` | from | `requirement` | 38 | 38 | 0 | `UEDGE-000004443`, `UEDGE-000004445`, `UEDGE-000004449` |
| `UTCE-DR-04` | `Implements` | from | `architecture` | 36 | 36 | 0 | `UEDGE-000003907`, `UEDGE-000003975`, `UEDGE-000004045` |
| `UTCE-DR-05` | `Implemented-By` | from | `implementation` | 17 | 17 | 0 | `UEDGE-000003908`, `UEDGE-000003910`, `UEDGE-000003976` |
| `UTCE-DR-06` | `Consumes` | from | `architecture` | 24 | 24 | 0 | `UEDGE-000003587`, `UEDGE-000003629`, `UEDGE-000003649` |
| `UTCE-DR-07` | `Traces-To` | from | `requirement` | 5 | 5 | 0 | `UEDGE-000003957`, `UEDGE-000004029`, `UEDGE-000004095` |

## Basis of each rule

| Rule | Basis |
|---|---|
| `UTCE-DR-01` | The located vocabulary declares this type's subject lane to be the architecture lane; the structural edges already exist in the certified corpus but the generator writes no lane entry for them. |
| `UTCE-DR-02` | Declared subject lane in the located vocabulary. |
| `UTCE-DR-03` | Declared subject lane in the located vocabulary. |
| `UTCE-DR-04` | Declared subject lane in the located vocabulary. |
| `UTCE-DR-05` | Declared object lane of the located Implements type. The object of a forward Implements edge is its target, and the target is the FROM endpoint of the materialized inverse, so the object lane is measured there. Reading the inverse edge's TO endpoint selected the DECLARER instead of the object — measured 4/36 populated against 17/17 for the object — which counted as headroom a lane entry no located edge supports. Corrected to the endpoint this basis names; the located vocabulary at 00-BOOK/tools/config.py governs the attribution (CMG-000001 XXXIV.5). |
| `UTCE-DR-06` | Declared subject lane in the located vocabulary. |
| `UTCE-DR-07` | Declared subject lane in the located vocabulary. |
