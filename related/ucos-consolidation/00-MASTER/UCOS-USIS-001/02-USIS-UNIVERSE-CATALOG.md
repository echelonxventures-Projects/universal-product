# USIS-002 — Universe Catalog

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-002 (Universe Catalog — seed registration) |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| STATUS | PROPOSED · AWAITING RATIFICATION · PRE-WAVE-0 |
| DEPENDS-ON | USIS-GOV-000 · USIS-001 · MIP universe catalog (U16/U24/U25/U26/U28) |
| NATURE | **Open, recursively extensible registry.** The 21 universes are the initial registered members of an unbounded, self-similar set (LAW USIS-09). New universes register without redesign. |

> **Purpose.** Enumerate the constitutional universes of USIS as registry members, each mapped to its realizing MIP universe/part, each a canonical owner of a science/intelligence concern. A universe MAY contain universes (recursive).

---

## 1 — The 21 constitutional universes (seed)

| # | USIS Universe | id | Realizes (MIP anchor) | Canonical concern |
|---|---------------|-----|-----------------------|-------------------|
| 1 | Universal Science | USIS-U-SCI | Part 19 (Knowledge) + LAW USIS-00 | ownership of all scientific disciplines |
| 2 | Universal Intelligence | USIS-U-INT | U25 / Part 20 | reasoning & intelligence paradigms (subsumes UIP) |
| 3 | Universal Human Intelligence | USIS-U-HUM | U25 / Part 20 | human mind, cognition, experience |
| 4 | Universal Cognitive Sciences | USIS-U-COG | U25 / Part 20 | cognition, perception, attention, memory |
| 5 | Universal Behavioral Sciences | USIS-U-BEH | U25 | behavior, motivation, decision behavior |
| 6 | Universal Psychological Sciences | USIS-U-PSY | U25 | psychology, personality, mental models |
| 7 | Universal Learning | USIS-U-LRN | Part 21 | all learning paradigms |
| 8 | Universal Self-Evolution | USIS-U-EVO | U28 / Part 22/32 | self-* capabilities; governed self-change |
| 9 | Universal Data | USIS-U-DAT | 10-DATA / U07 | data science/engineering/governance/fabric/mesh |
| 10 | Universal Analytics | USIS-U-ANL | U16 / Part 20 | descriptive→prescriptive analytics |
| 11 | Universal Algorithm | USIS-U-ALG | U25 | algorithm catalogs (dynamic) |
| 12 | Universal Model | USIS-U-MDL | Part 20 (Model Registry) | agnostic model catalog |
| 13 | Universal Decision | USIS-U-DEC | U25 | decision intelligence & science |
| 14 | Universal Reasoning | USIS-U-RSN | U25 / Part 20 | inference & reasoning |
| 15 | Universal Prediction | USIS-U-PRD | U16 | forecasting & predictive science |
| 16 | Universal Simulation | USIS-U-SIM | U26 / Part 25 | modeled execution |
| 17 | Universal Knowledge | USIS-U-KNW | U24 / Part 19 | structured meaning & knowledge science |
| 18 | Universal Autonomous Systems | USIS-U-AUT | U25 | governed autonomy |
| 19 | Universal Multi-Agent | USIS-U-MAS | U25 | multi-agent & swarm systems |
| 20 | Universal Future Sciences | USIS-U-FUT | Part 49 (future constructs) | reserved slot for emerging sciences |
| 21 | Universal Unknown Sciences | USIS-U-UNK | Directive D9 + LAW USIS-09 | reserved slot for currently-unknown domains |

## 2 — Universe registry model

Each universe is a registry row: `{ id, home: 06-DOMAINS/<UNIVERSE>/ , realizes: <MIP anchor>, owner, status, parent-universe? }`.
- Every universe inherits the cross-cutting capability contract (USIS-001 Part E) and the 7 prime properties.
- **Recursion (LAW USIS-09):** any universe may register child universes/disciplines/domains; `parent-universe` records containment; the substrate is self-similar.
- **Openness:** U-FUT and U-UNK are permanent reserved slots; `USIS-U-*` growth is append-only, uncapped (Directives D3/D8/D9).

## 3 — Non-duplication mapping (Reuse-First, LAW USIS-02)

Where a universe realizes an existing MIP universe/program, it **references** it and does not fork it:

| USIS universe | Reuses (does not duplicate) |
|---------------|-----------------------------|
| Universal Data | `10-DATA/` program + U07 (Data) |
| Universal Simulation | U26 + Part 25 |
| Universal Knowledge | U24 + Part 19 knowledge registries |
| Universal Analytics/Intelligence/Reasoning/Prediction | U16/U25 + Part 20 engines/registries |
| Universal Self-Evolution | U28 + Part 22/32 evolution model |
| Security/Governance/Runtime intelligence (as domains) | `14-SECURITY/`, U03 Governance, `08-RUNTIME/` / RIE |

## 4 — UIP subsumption

The former UIP domains (`UIP-DOM-*`) are re-homed under the relevant USIS universes (Intelligence → U-INT; Human → U-HUM; Analytics → U-ANL; Learning → U-LRN; etc.). No UIP concept is lost; none is duplicated.
