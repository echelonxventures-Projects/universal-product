"""
UCOS Ω∞ Universal Master Knowledge Book (UKB) — Generator Configuration.

This module is DATA ONLY. It declares:

  * VOLUMES        — the root volumes (append-only; never renumbered). The list
                     grows by append (VOL-000…VOL-022 today after the VOL-021
                     Digital-Twin and VOL-022 Master-Book additions); the emitted
                     count is always derived from this list, never a fixed literal
                     (UMB-REMED-002 F-5 documentation-drift closure).
  * CLASSIFY_RULES — ordered (regex, program, category, volume) rules that map
                     every repository file to a program, an identifier namespace
                     (category), and a thematic volume. First match wins.
  * CHAINS         — the real dependency chains of each program family, expressed
                     as ordered lists of filename substrings. Consecutive members
                     form Parent/Child + Depends-On edges in the knowledge graph.
  * CROSS_PROGRAM  — the downstream ordering between program roots.
  * EXCLUDE_*      — paths the generator must not register (its own machinery and
                     generated outputs) so the registry never lists itself.

The Universal Identifier and Universal Page allocations are NOT configured here;
they are allocated append-only at runtime and persisted in DATA/id-ledger.json so
that no identifier or page number is ever reused or renumbered.
"""

BOOK_ROOT_ID = "UCOS-BOOK-000000"
BOOK_ROOT_PATH = "00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md"
BOOK_NAME = "UCOS Ω∞ Universal Master Knowledge Book"
GENERATOR_VERSION = "1.0.0"

# Approximate lines-of-content per Universal Page (used only at first registration;
# an artifact's page range is fixed forever once allocated).
LINES_PER_PAGE = 60
BYTES_PER_PAGE = 2400  # for binary (.docx) source artifacts

# ---------------------------------------------------------------------------
# VOLUMES — permanent, append-only. Serial == numeric suffix.
# ---------------------------------------------------------------------------
VOLUMES = [
    ("VOL-000", 0,  "MASTER INDEX",   "IDX", "Root navigation, master index, and book infrastructure."),
    ("VOL-001", 1,  "VISION",         "VSN", "Canonical vision and North Star source material."),
    ("VOL-002", 2,  "CONSTITUTION",   "CON", "Constitutional corpus, consolidation program, freeze, and registers."),
    ("VOL-003", 3,  "ARCHITECTURE",   "ARCH","Universal architecture constitutions, catalogs, and engineering foundation."),
    ("VOL-004", 4,  "IMPLEMENTATION", "IMP", "Implementation governance, plans, trackers, and technology constitution."),
    ("VOL-005", 5,  "RUNTIME",        "RUN", "Runtime constitution, architecture, and canonical runtime catalogs."),
    ("VOL-006", 6,  "PLATFORM",       "PLT", "Implementation platforms and engines."),
    ("VOL-007", 7,  "DATA",           "DAT", "Data architecture, catalog, reference, and generation."),
    ("VOL-008", 8,  "SERVICE",        "SVC", "Service architecture, catalog, reference, and generation."),
    ("VOL-009", 9,  "APPLICATION",    "APP", "Application architecture, catalog, reference, and generation."),
    ("VOL-010", 10, "INFRASTRUCTURE", "INF", "Infrastructure architecture."),
    ("VOL-011", 11, "SECURITY",       "SEC", "Security architecture and controls."),
    ("VOL-012", 12, "TESTING",        "TST", "Testing and quality-assurance architecture."),
    ("VOL-013", 13, "QUALITY",        "QA",  "Quality architecture (reserved; shares testing lineage)."),
    ("VOL-014", 14, "DEPLOYMENT",     "DEP", "Deployment architecture (reserved)."),
    ("VOL-015", 15, "OPERATIONS",     "OPS", "Operations and observability architecture."),
    ("VOL-016", 16, "PRODUCTS",       "PRD", "Production platform and product lines."),
    ("VOL-017", 17, "FACTORY",        "FAC", "Application factory and generation frameworks."),
    ("VOL-018", 18, "REGISTRIES",     "REG", "Universal registries, manifests, and schemas."),
    ("VOL-019", 19, "CERTIFICATION",  "CRT", "Certification architecture and readiness."),
    ("VOL-020", 20, "CONTROL TOWER",  "CTL", "Program control tower and external-execution support."),
    # --- Appended by the UKB Advancement Program (Digital Twin). Append-only; no
    #     existing volume above is renumbered or modified (UKB-INV-01/03). --------
    ("VOL-021", 21, "DIGITAL TWIN",   "ADV", "UKB Advancement Program: living Digital-Twin architecture — connectors, repository/implementation/testing/security/deployment/production intelligence, UI-UX twin, publication, navigation portal, enterprise search, control-tower automation, AI knowledge layer, and twin certification."),
    # --- Appended by the Universal Master Book Architecture Program (UMB). Append-only;
    #     no existing volume above is renumbered or modified (UKB-INV-01/03; AUTH-INF-001
    #     CR-INF-002/005). Holds the consolidated complete future-state architecture of the
    #     UCOS Ω∞ Master Book as a Universal Digital-Twin Knowledge Operating System. ------
    ("VOL-022", 22, "MASTER BOOK ARCHITECTURE", "UMB", "Universal Master Book Architecture Program: the complete future-state architecture of the UCOS Ω∞ Master Book as a continuously synchronized, infinitely scalable, infinitely extensible, infinitely traceable, self-evolving Universal Digital-Twin Knowledge Operating System — Master Book, Digital Twin, Identity, Nomenclature, Registry, Knowledge Graph, Traceability, Change, Version, Lineage, Publication, Synchronization, Search, AI Knowledge, Security, Control Tower, Certification, Runtime, and Operational architectures."),
    # --- Appended by Wave 0 (UCOS-USIS-001 / EIP-018 — authorized; Phase 0.3).
    #     Append-only; no existing volume above is renumbered or modified
    #     (USIS-009 §1; UKB-INV-01/03). Thematic home for the Universal Science &
    #     Intelligence substrate corpus (15-UNIVERSAL-SCIENCE-INTELLIGENCE/). -----
    ("VOL-024", 24, "UNIVERSAL SCIENCE & INTELLIGENCE", "USIS", "Universal Science & Intelligence Substrate (USIS): the constitutional substrate beneath every scientific discipline and intelligence paradigm — 21 universes, Universal Science, Human Intelligence, Self-Evolution, and Data/Analytics/Algorithm/Model universes, the 24-tier Universal Capability Meta-Model, reasoning/learning/analytics/simulation runtime, grounding/explanation validation, and explainability/bounded-autonomy/reproducibility certification."),
]

# ---------------------------------------------------------------------------
# CLASSIFY_RULES — ordered. Each: (regex_on_relpath, program, category, volume)
# The regex is matched with re.search against the POSIX repo-relative path.
# ---------------------------------------------------------------------------
CLASSIFY_RULES = [
    # --- UKB root + registered machinery -----------------------------------
    (r"^00-BOOK/UCOS-BOOK-000000", "UKB", "BOOK", "VOL-000"),
    (r"^00-BOOK/SCHEMAS/",          "UKB", "REG",  "VOL-018"),

    # --- UKB Advancement Program (Digital Twin) — append-only extension --------
    #     Advancement architecture/planning artifacts live under 00-BOOK/ADVANCEMENT/.
    #     None of the existing rules above match this prefix, so this rule adds new
    #     coverage only; it changes no prior classification (UKB-INV-02/03/07).
    (r"^00-BOOK/ADVANCEMENT/",      "ADV", "ADV",  "VOL-021"),

    # --- Universal Master Book Architecture Program (UMB) — append-only extension ---
    #     Consolidated complete future-state architecture set lives under
    #     00-BOOK/MASTER-BOOK/. No prior rule matches this prefix, so this adds new
    #     coverage only and changes no existing classification (REG-AUTO-001 §12;
    #     UKB-INV-02/03/07; AUTH-INF-001 CR-INF-007). Placed high so the path-prefix
    #     match wins ahead of any substring rule (first match wins).
    (r"^00-BOOK/MASTER-BOOK/",      "UMB", "UMB",  "VOL-022"),

    # --- Frozen source corpus ----------------------------------------------
    (r"^00-SOURCE/VISION/",         "SOURCE", "VSN", "VOL-001"),
    (r"^00-SOURCE/CONSTITUTIONS/",  "SOURCE", "CON", "VOL-002"),
    (r"^00-SOURCE/ARCHITECTURE/",   "SOURCE", "ARCH","VOL-003"),
    (r"^00-SOURCE/PHASES/",         "SOURCE", "CON", "VOL-002"),
    (r"^00-SOURCE-MANIFEST/",       "SOURCE", "SRC", "VOL-018"),
    (r"^99-FREEZE/",                "CONSOLIDATION", "FRZ", "VOL-002"),
    (r"^01-WORKING/",               "CONSOLIDATION", "CON", "VOL-002"),

    # --- 02-MASTER: External Execution Support -----------------------------
    (r"EXTERNAL-ACTOR|EXTERNAL-EXECUTION", "EES", "EES", "VOL-020"),

    # --- 02-MASTER: Implementation governance package (IMP-000) ------------
    (r"TECHNOLOGY-CONSTITUTION",            "IMP", "IMP", "VOL-004"),
    (r"IMPLEMENTATION-GOVERNANCE-BASELINE", "IMP", "IMP", "VOL-004"),
    (r"IMPLEMENTATION-MASTER-PLAN",         "IMP", "IMP", "VOL-004"),
    (r"IMPLEMENTATION-PROGRAM-TRACKER",     "IMP", "IMP", "VOL-004"),

    # --- 02-MASTER: Consolidation program ----------------------------------
    (r"CONSOLIDATION-PROGRAM-MASTER-INDEX", "CONSOLIDATION", "IDX", "VOL-000"),
    (r"CONSTITUTIONAL-|CONSTITUENT-|STAKEHOLDER-HANDOFF", "CONSOLIDATION", "CON", "VOL-002"),

    # --- 02-MASTER: ARCH catalogs (ARCH-001..004) --------------------------
    (r"UNIVERSAL-UNIVERSE-CATALOG|UNIVERSAL-DOMAIN-CATALOG|UNIVERSAL-CAPABILITY-CATALOG|UNIVERSAL-COMPONENT-CATALOG",
        "ARCH", "ARCH", "VOL-003"),

    # --- 02-MASTER: ARCH constitutions (thematic volumes) ------------------
    (r"AGENT-CONSTRUCTION-CONSTITUTION|IMPLEMENTATION-MODEL-CONSTITUTION", "ARCH", "ARCH", "VOL-003"),
    (r"UNIVERSAL-DATA-ARCHITECTURE-CONSTITUTION",          "ARCH", "ARCH", "VOL-007"),
    (r"UNIVERSAL-SERVICE-ARCHITECTURE-CONSTITUTION",       "ARCH", "ARCH", "VOL-008"),
    (r"UNIVERSAL-APPLICATION-ARCHITECTURE-CONSTITUTION",   "ARCH", "ARCH", "VOL-009"),
    (r"UNIVERSAL-INFRASTRUCTURE-ARCHITECTURE-CONSTITUTION","ARCH", "ARCH", "VOL-010"),
    (r"UNIVERSAL-SECURITY-ARCHITECTURE-CONSTITUTION",      "ARCH", "ARCH", "VOL-011"),
    (r"UNIVERSAL-TESTING-QUALITY-ARCHITECTURE-CONSTITUTION","ARCH","ARCH", "VOL-012"),
    (r"UNIVERSAL-OPERATIONS-ARCHITECTURE-CONSTITUTION",    "ARCH", "ARCH", "VOL-015"),
    (r"UNIVERSAL-OBSERVABILITY-ARCHITECTURE-CONSTITUTION", "ARCH", "ARCH", "VOL-015"),
    (r"UNIVERSAL-CERTIFICATION-ARCHITECTURE-CONSTITUTION", "ARCH", "ARCH", "VOL-019"),
    (r"-ARCHITECTURE-CONSTITUTION",                        "ARCH", "ARCH", "VOL-003"),

    # --- 03-CATALOGS: Canonical Runtime Catalogs ---------------------------
    (r"^03-CATALOGS/.*CANONICAL-DATA-CATALOG",        "CAT", "CAT", "VOL-007"),
    (r"^03-CATALOGS/.*CANONICAL-SERVICE-CATALOG",     "CAT", "CAT", "VOL-008"),
    (r"^03-CATALOGS/.*CANONICAL-APPLICATION-CATALOG", "CAT", "CAT", "VOL-009"),
    (r"^03-CATALOGS/",                                "CAT", "CAT", "VOL-005"),

    # --- 04-REFERENCE: Reference Architectures -----------------------------
    (r"^04-REFERENCE/.*REFERENCE-DATA-ARCHITECTURE",        "REF", "REF", "VOL-007"),
    (r"^04-REFERENCE/.*REFERENCE-SERVICE-ARCHITECTURE",     "REF", "REF", "VOL-008"),
    (r"^04-REFERENCE/.*REFERENCE-APPLICATION-ARCHITECTURE", "REF", "REF", "VOL-009"),
    (r"^04-REFERENCE/",                                     "REF", "REF", "VOL-003"),

    # --- 05-GENERATION: Generation Frameworks ------------------------------
    (r"^05-GENERATION/.*DATA-GENERATION",        "GEN", "GEN", "VOL-007"),
    (r"^05-GENERATION/.*SERVICE-GENERATION",     "GEN", "GEN", "VOL-008"),
    (r"^05-GENERATION/.*APPLICATION-GENERATION", "GEN", "GEN", "VOL-009"),
    (r"^05-GENERATION/",                         "GEN", "GEN", "VOL-017"),

    # --- 06-IMPLEMENTATION: Platforms --------------------------------------
    (r"^06-IMPLEMENTATION/.*APPLICATION-FACTORY",  "IMP", "IMP", "VOL-017"),
    (r"^06-IMPLEMENTATION/.*PRODUCTION-PLATFORM",  "IMP", "IMP", "VOL-016"),
    (r"^06-IMPLEMENTATION/",                       "IMP", "IMP", "VOL-006"),

    # --- 07-ENGINEERING: Engineering Program -------------------------------
    (r"^07-ENGINEERING/.*ENGINEERING-PROGRAM-MASTER-INDEX", "ENG", "ENG", "VOL-000"),
    (r"^07-ENGINEERING/",                                   "ENG", "ENG", "VOL-003"),

    # --- 08-RUNTIME: Runtime Program ---------------------------------------
    (r"^08-RUNTIME/", "RUN", "RUN", "VOL-005"),

    # --- 09-PLATFORM: Platform Architecture Program (PHASE-003) -------------
    #     Append-only coverage for the platform foundation program. No prior rule
    #     matches the ^09-PLATFORM/ prefix, so this adds new classification only
    #     and changes no existing mapping (REG-AUTO-001 / UKB-INV-02/03/07).
    #     Routed to the existing PLATFORM volume (VOL-006, category PLT); nothing
    #     is renumbered.
    (r"^09-PLATFORM/", "PLATFORM", "PLT", "VOL-006"),

    # --- 10-DATA: Data Architecture Program (PHASE-004) ---------------------
    #     Append-only coverage for the data foundation program. No prior rule
    #     matches the ^10-DATA/ prefix, so this adds new classification only and
    #     changes no existing mapping (REG-AUTO-001 / UCI-001). Routed to the
    #     existing DATA volume (VOL-007, category DAT); nothing is renumbered.
    (r"^10-DATA/", "DATA", "DAT", "VOL-007"),

    # --- 11-SERVICE: Service Architecture Program (PHASE-005) ---------------
    #     Append-only coverage for the service foundation program. No prior rule
    #     matches the ^11-SERVICE/ prefix, so this adds new classification only and
    #     changes no existing mapping (REG-AUTO-001 / UCI-001). Routed to the
    #     existing SERVICE volume (VOL-008, category SVC); nothing is renumbered.
    (r"^11-SERVICE/", "SERVICE", "SVC", "VOL-008"),

    # --- UMB-REMED-002 (F-6 CLASSIFICATION HYGIENE CLOSURE) — append-only. -------
    #     These rules resolve the advisory-unclassified artifacts identified by
    #     UMB-CERT-001 F-6. They add NEW coverage only (no prior CLASSIFY_RULES
    #     rule matches these prefixes/names), so no existing classification is
    #     changed and no Universal ID is renumbered (allocate() is keyed by path;
    #     an already-allocated UID is returned verbatim regardless of category —
    #     the append-only Identity invariant is preserved). Each maps to a volume
    #     that ALREADY EXISTS; nothing is renumbered. They mirror the established
    #     ^09-PLATFORM/ · ^10-DATA/ · ^11-SERVICE/ pattern for the next two
    #     numbered program families whose rule was never appended.

    # Application Architecture Program (PHASE-006) → existing APPLICATION volume
    # (VOL-009, category APP). 22 artifacts (APPLICATION-001…018 + GOV-*).
    (r"^12-APPLICATION/", "APPLICATION", "APP", "VOL-009"),

    # Infrastructure Architecture Program (PHASE-007) → existing INFRASTRUCTURE
    # volume (VOL-010, category INF). 20 artifacts (INFRASTRUCTURE-001…018 + GOV/EXEC).
    (r"^13-INFRASTRUCTURE/", "INFRASTRUCTURE", "INF", "VOL-010"),

    # Architectural-quality constitution (02-MASTER) — an ARCHITECTURE constitution
    # whose name (…-ARCHITECTURAL-QUALITY-CONSTITUTION) is not caught by the
    # `-ARCHITECTURE-CONSTITUTION` rule above. Routed to VOL-003 (ARCHITECTURE),
    # consistent with its sibling 02-MASTER architecture constitutions. 1 artifact.
    (r"ARCHITECTURAL-QUALITY-CONSTITUTION", "ARCH", "ARCH", "VOL-003"),

    # Root-level planning binaries (repo-root *.docx: the master end-to-end program
    # and consolidation plan) → CONSOLIDATION program (VOL-002). The negative
    # lookahead deliberately EXCLUDES Microsoft Office owner/lock temp files
    # (basename beginning "~$"), which are transient non-artifacts left
    # intentionally undefined (UMB-REMED-002 F-6 determination) and recommended for
    # exclusion rather than classification. Matched with re.search on the relpath.
    (r"^(?!~\$)[^/]*\.docx$", "CONSOLIDATION", "CON", "VOL-002"),

    # --- UCOS-GOV-006 (REPOSITORY GOVERNANCE CORRECTION) — first-class family
    #     rules. Append-only; each adds NEW coverage only (no prior rule matches
    #     these prefixes — the families were the genuine unclassified artifacts
    #     isolated by GOV-005 CLASS-RC-1). No existing classification changes; no
    #     Universal ID is renumbered (allocate() is path-keyed). Every category is
    #     enumerated as a first-class artifact family (see ARTIFACT_FAMILIES) and
    #     routed to a volume that ALREADY EXISTS — nothing is renumbered. These are
    #     the intended stable namespaces; the deterministic path-derived catch-all
    #     in ukb.py::classify() guarantees totality for every OTHER present/future
    #     tree without a per-tree rule. -----------------------------------------

    # Architecture Decision Records → ARCHITECTURE volume (VOL-003). ADRs are
    # governed decision records (ADR-0001 is a CI prerequisite per GOV-003).
    (r"^adr/", "ADR", "ADR", "VOL-003"),

    # Governance determinations (02-MASTER/UCOS-GOV-NNN) → CONTROL TOWER volume
    # (VOL-020). The highest-authority program-governance documents in the repo.
    (r"^02-MASTER/UCOS-GOV-", "GOV", "GOV", "VOL-020"),

    # Execution determinations (02-MASTER/UCOS-EXEC-NNN) → CONTROL TOWER volume
    # (VOL-020). Execution determinations authorize implementation. The EXEC
    # category shares the ONE append-only identity authority (id-ledger
    # category_seq) with EXEC-REG-001 execution instances by design — the shared
    # counter guarantees no Universal ID is ever duplicated across the two.
    (r"^02-MASTER/UCOS-EXEC-", "EXEC", "EXEC", "VOL-020"),

    # Application-foundation determinations (02-MASTER/APP-NNN) → APPLICATION
    # volume (VOL-009), the single APP program spanning both 02-MASTER and
    # 12-APPLICATION (category APP already exists for VOL-009).
    (r"^02-MASTER/APP-", "APP", "APP", "VOL-009"),

    # Engineering implementation documents (engine/**: epic completion reports +
    # source fixtures/blueprints) → ARCHITECTURE/engineering volume (VOL-003),
    # consistent with the 07-ENGINEERING program (category ENG). Broad prefix so
    # the whole tree is total (completion reports AND blueprints/*.json).
    (r"^engine/", "ENG", "ENG", "VOL-003"),

    # Platform implementation documents (platform/**: EC2 epic completion reports)
    # → PLATFORM volume (VOL-006, category PLT), consistent with the 09-PLATFORM
    # program. Broad prefix so the whole tree is total.
    (r"^platform/", "PLATFORM", "PLT", "VOL-006"),

    # --- Universal Science & Intelligence Substrate (USIS / PHASE-EIP-018) —
    #     append-only Wave-0 (Phase 0.3) coverage. No prior rule matches the
    #     ^15-UNIVERSAL-SCIENCE-INTELLIGENCE/ prefix, so this adds NEW coverage
    #     only and changes no existing classification (USIS-009 §1; REG-AUTO-001;
    #     UKB-INV-02/03/07). Routed to the new thematic volume VOL-024 (category
    #     USIS); nothing is renumbered. VOL-023 was already claimed by the
    #     auto-discovered SECURITY-GOVERNANCE volume (14-SECURITY), so USIS takes
    #     the next genuinely-free identifier VOL-024 (B1 collision correction).
    #     Mirrors the ^09-PLATFORM/ … ^13-INFRASTRUCTURE/ first-class-family
    #     pattern for the next numbered program tree.
    (r"^15-UNIVERSAL-SCIENCE-INTELLIGENCE/", "USIS", "USIS", "VOL-024"),

    # --- CRAP-001 CLASSIFICATION HYGIENE — append-only. --------------------------
    #     These rules close the path-derived catch-all gap for the lower-case
    #     implementation directories (service/, application/, infrastructure/) and
    #     the root-level evolution/IAC artifacts whose derived categories exceeded
    #     the {2,6} schema constraint. They add NEW coverage only (no prior rule
    #     matches these prefixes), change no existing classification (allocate() is
    #     path-keyed; existing UIDs remain verbatim — append-only identity invariant
    #     preserved). Each routes to a volume that ALREADY EXISTS.

    # service/ implementation tree → SERVICE volume (VOL-008, category SVC).
    (r"^service/", "SERVICE", "SVC", "VOL-008"),

    # application/ implementation tree → APPLICATION volume (VOL-009, category APP).
    (r"^application/", "APPLICATION", "APP", "VOL-009"),

    # infrastructure/ implementation tree → INFRASTRUCTURE volume (VOL-010, category INF).
    (r"^infrastructure/", "INFRASTRUCTURE", "INF", "VOL-010"),

    # EVO-USIS-NNN evolution packages → USIS volume (VOL-024, category USIS).
    (r"^EVO-USIS-", "USIS", "USIS", "VOL-024"),

    # IAC-001x Implementation Authority Confirmation packages → EXEC volume (VOL-020).
    (r"^IAC-001", "EXEC", "EXEC", "VOL-020"),

    # intelligence/ implementation tree → ENGINEERING volume (VOL-003, category ENG).
    (r"^intelligence/", "INTELLIGENCE", "ENG", "VOL-003"),

    # knowledge/ declarations → ENGINEERING volume (VOL-003, category ENG).
    (r"^knowledge/", "KNOWLEDGE", "ENG", "VOL-003"),

    # data/ directory → DATA volume (VOL-007, category DAT).
    (r"^data/", "DATA", "DAT", "VOL-007"),

    # 14-SECURITY → SECURITY volume (VOL-011, category SEC).
    (r"^14-SECURITY/", "SECURITY", "SEC", "VOL-011"),

    # 00-MASTER/ (standing programmes, closures, phases) → CONTROL TOWER (VOL-020).
    (r"^00-MASTER/", "MASTER", "MASTER", "VOL-020"),

    # 00-CEP/ constitutional engineering → CONSTITUTION volume (VOL-002, category CEP).
    (r"^00-CEP/", "CEP", "CEP", "VOL-002"),

    # 00-CMG/ meta-governance → CONSTITUTION volume (VOL-002, category CMG).
    (r"^00-CMG/", "CMG", "CMG", "VOL-002"),

    # --- W3-3 CONSOLIDATE (C-03): truncation-variant category reconciliation --------
    #     Root-level EXECUTION*/ARCHITECTURAL*/IMPLEMENTATION* files were falling through
    #     to the path-derived catch-all, which truncated their stems to DERIVED_CATEGORY_MAXLEN
    #     (6 chars) yielding EXECUT/ARCHIT/IMPLEM. These rules map them to their canonical
    #     categories before the catch-all. Append-only: no existing classification changes
    #     (allocate() is path-keyed; existing UIDs remain verbatim). The 9 affected artifacts
    #     (5 EXECUT → EXEC, 4 ARCHIT → ARCH, 12 IMPLEM → IMP) reclassify to their canonical
    #     volumes. Pattern: matches root-level files whose stem begins with the specified
    #     prefix (after stripping leading NN- ordinal).

    # Root-level EXECUTION-* and EXECUTIVE-* files → EXEC (CONTROL TOWER, VOL-020).
    # Matches: 01-EXECUTION-CONTROLLER-ARCHITECTURE.md, 02-EXECUTION-LIFECYCLE.md,
    #          04-EXECUTION-QUEUE-MODEL.md, 09-EXECUTION-GOVERNANCE.md, 08-EXECUTIVE-SUMMARY.md
    (r"^(?:\d+[-_.])?EXECUT", "EXEC", "EXEC", "VOL-020"),

    # Root-level ARCHITECTURAL-* and ARCHITECTURE-* files → ARCH (ARCHITECTURE, VOL-003).
    # Matches: 03-ARCHITECTURAL-COMPLETENESS.md, 02-ARCHITECTURAL-STABILITY-CERTIFICATION.md,
    #          07-ARCHITECTURE-FREEZE-EVIDENCE.md, 03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md
    (r"^(?:\d+[-_.])?ARCHIT", "ARCH", "ARCH", "VOL-003"),

    # Root-level IMPLEMENTATION-* files → IMP (IMPLEMENTATION, VOL-004).
    # Matches: 04-IMPLEMENTATION-BACKLOG.md (+ 11 other IMPLEMENTATION-* root files)
    (r"^(?:\d+[-_.])?IMPLEMENT", "IMP", "IMP", "VOL-004"),

    # --- Root-level constitutional determination & evidence documents --------------
    #     UMB-004 §5: "When a new entity class appears it receives a category namespace
    #     (append-only) AND a classification rule. A namespace minted without a declared
    #     rule is a namespace no authority governs." Six root-level determination and
    #     evidence documents were minting ONE namespace EACH through the path-derived
    #     catch-all — P0FINA, P0FREE, R1REPO, RTBD00, STAGE0, W34CUN — each landing in
    #     VOL-000 with its own name as its own program, i.e. governed by nothing. That
    #     carried live ungoverned namespaces from 74 to 80 and closed the UIS-001 gate on
    #     the blocking UIS-V-14 ratchet (`namespaces_ungoverned <= 74`).
    #
    #     The remedy is the one UMB-004 §5 names: declare the rule. It is NOT a widening
    #     of the ratchet — the bound is untouched and the count returns to 74.
    #
    #     TWO parts, because the six namespaces are already minted and identity is
    #     immutable (allocate() is path-keyed: an existing by_path entry returns its
    #     universal_id verbatim, so no rule can renumber or retire one):
    #
    #       (a) DECLARE the six. Each exact-path rule carries the category its artifact
    #           already bears, so the declared rule agrees with the immutable identity
    #           rather than contradicting it, and gives each document the CONTROL TOWER
    #           home (VOL-020) that its VOL-000 orphan state denied it. Nothing is
    #           renumbered; only volume and program change, both of them derived fields.
    #
    #       (b) PREVENT recurrence. The trailing family rules below route every FUTURE
    #           document of these same identifier families to the governed DET category,
    #           so the next P0-*, RTBD-*, STAGE-*, R-N-* or W3-* determination reuses one
    #           declared namespace instead of minting a seventh, an eighth, a ninth.
    #           Without (b) this defect returns on the next determination committed.
    #
    #     Ordered before (b) so the six keep the identity they were minted with.
    (r"^P0-FINAL-ASSIMILATION-AUDIT\.md$", "DET", "P0FINA", "VOL-020"),
    (r"^P0-FREEZE-CERTIFICATION-001-", "DET", "P0FREE", "VOL-020"),
    (r"^R-1-REPOSITORY-REPLAY-SYNCHRONIZATION-EVIDENCE\.md$", "DET", "R1REPO", "VOL-020"),
    (r"^RTBD-001-REPOSITORY-TRUTH-BOUNDARY-DETERMINATION\.md$", "DET", "RTBD00", "VOL-020"),
    (r"^STAGE-0-IMPLEMENTATION-COMPLETION-PLAN\.md$", "DET", "STAGE0", "VOL-020"),
    (r"^W3-4c-UNIVERSAL-ASSURANCE-VALIDATION-CLUSTER-COVERAGE-EVIDENCE\.md$",
     "DET", "W34CUN", "VOL-020"),

    # (b) Future root-level determination & evidence documents of the same families →
    #     the single governed DET namespace (CONTROL TOWER, VOL-020). Root-level only:
    #     each alternative is anchored and carries its family's own separator, so these
    #     cannot reach into a subdirectory or collide with the curated rules above.
    (r"^(?:P0-|RTBD-|STAGE-\d|R-\d+-|W\d+-\d)[A-Za-z0-9]", "DET", "DET", "VOL-020"),
]

DEFAULT_CLASS = ("OTHER", "MISC", "VOL-000")

# ===========================================================================
# UCOS-GOV-006 — REPOSITORY GOVERNANCE MODEL COMPLETION (GOV-005 §5.3 / Part 4).
#
# DATA ONLY. Completes the governance taxonomy so that (a) every artifact family
# is a FIRST-CLASS category, and (b) environment/generated outputs are FORMALLY
# modelled as non-artifacts whose authoritative boundary is version control.
# It hard-codes NO artifact name and NO manual registration/whitelist; it
# documents the rule-based model the eligibility + classification engines
# implement. Adding a future family is append-only.
# ===========================================================================

# --- Constitutional definition (GOV-005 §5.3) -------------------------------
# A REPOSITORY ARTIFACT is a version-controlled (carried by version control:
# tracked or staged), human-authored corpus file of an included type. A GENERATED
# ARTIFACT is a deterministically re-derivable output (registries, twin,
# control-tower, portal, evidence) — regenerated, never hand-registered. An
# ENVIRONMENT ARTIFACT is a build/cache/dependency/tooling output (venv,
# *.egg-info, __pycache__, .pytest_cache, .ruff_cache, coverage). Only
# REPOSITORY ARTIFACTS are eligible for registration; the other two classes are
# bounded — and thereby excluded — by the ignore authority (.gitignore), NOT by
# any hand-maintained path list.
#
# B-01c RECONCILIATION. This definition previously also admitted "newly-authored
# and un-ignored" (i.e. UNTRACKED) files, which CONTRADICTED REGISTRATION_SCOPE
# below ("version-controlled repository artifacts") and made eligibility a
# function of the local working tree instead of the commit: a CI checkout, which
# by construction contains only what version control carries, computed a SMALLER
# universe than the authoring clone and therefore reached DIFFERENT registration
# decisions over the same commit. The two declarations are now one: eligibility is
# the version-controlled corpus (`git ls-files --cached --exclude-standard`), which
# is identical in every environment at a given commit. Enforcement is unchanged in
# strength and merely applied at the correct boundary — an artifact enters the
# corpus by entering version control (`git add`), at which instant it becomes
# eligible and the pre/post enforcement gates plus the --guard drift gate must pass
# before it can be committed. Files awaiting that binding are never silent: the
# enforcement gate and `ukb.py eligibility` report each one by path.
REPOSITORY_ARTIFACT_DEFINITION = (
    "A repository artifact is a version-controlled (carried by version control: "
    "git-tracked or staged), human-authored corpus file whose extension is in "
    "INCLUDE_EXTENSIONS and which is not part of the generator's own machinery or "
    "generated output (EXCLUDE_DIR_PREFIXES). Generated and environment outputs "
    "are non-artifacts, bounded by version control (.gitignore). A file that is "
    "not yet carried by version control is a CANDIDATE artifact: reported, never "
    "registered, until it is bound by `git add`.")

# Registration scope: what the engines register (eligible == this set).
REGISTRATION_SCOPE = (
    "version-controlled repository artifacts of an included type, minus the "
    "generator's own machinery and generated outputs (corpus-internal excludes)")

# Non-artifact scope: formally modelled classes that are NEVER registered. Each
# is excluded automatically by the ignore authority (or the corpus-internal
# excludes for generated corpus outputs) — no per-file exception, no whitelist.
NON_ARTIFACT_SCOPE = {
    "environment": "virtual-environments, dependency metadata, byte-code and test/"
                   "lint caches, coverage (.ec1-venv/, *.egg-info/, __pycache__/, "
                   ".pytest_cache/, .ruff_cache/, .coverage, coverage.xml) — ignored",
    "generated":   "deterministically re-derivable outputs: the emitted registries, "
                   "DATA/, CONTROL-TOWER/, PORTAL/, generated evidence "
                   "(determinism-evidence/), and derived intelligence emitted "
                   "outside 00-BOOK by a located producer (the UCOS-RIE-001 output "
                   "family) — corpus-internal excludes / ignored",
    "transient":   "editor/office lock & owner files (~$*) and the registration "
                   "re-entrancy lock — ignored",
}

# First-class artifact families (GOV-005 Part 4). Each maps a family to its
# identifier-namespace CATEGORY and its thematic VOLUME (an EXISTING volume;
# nothing is renumbered). This enumerates the taxonomy; the executable mapping
# lives in CLASSIFY_RULES (curated families) + the deterministic path-derived
# catch-all in ukb.py::classify() (totality for every other tree). Append-only:
# a future family is a new entry, never a rewrite.
ARTIFACT_FAMILIES = {
    "APP":  {"category": "APP",  "volume": "VOL-009", "kind": "application-foundation",
             "sources": ("^02-MASTER/APP-", "^12-APPLICATION/")},
    "GOV":  {"category": "GOV",  "volume": "VOL-020", "kind": "governance-determination",
             "sources": ("^02-MASTER/UCOS-GOV-",)},
    "EXEC": {"category": "EXEC", "volume": "VOL-020", "kind": "execution-determination",
             "sources": ("^02-MASTER/UCOS-EXEC-",)},
    "ADR":  {"category": "ADR",  "volume": "VOL-003", "kind": "architecture-decision-record",
             "sources": ("^adr/",)},
    "ENG":  {"category": "ENG",  "volume": "VOL-003", "kind": "engineering-document/completion-report",
             "sources": ("^engine/", "^07-ENGINEERING/")},
    "PLT":  {"category": "PLT",  "volume": "VOL-006", "kind": "platform-document/completion-report",
             "sources": ("^platform/", "^09-PLATFORM/")},
    # Root-level constitutional determination & evidence documents. Enumerated here as a
    # first-class family (GOV-005 Part 4) because the taxonomy had no entry for the class
    # at all: every such document fell to the path-derived catch-all and minted a private
    # single-use namespace, which is the incompleteness GOV-005 §5.3 names as the root of
    # structurally guaranteed drift. The executable mapping is the trailing DET rules in
    # CLASSIFY_RULES; this entry is the taxonomy that authorizes them.
    "DET":  {"category": "DET",  "volume": "VOL-020", "kind": "constitutional-determination/evidence",
             "sources": (r"^P0-", r"^RTBD-", r"^STAGE-\d", r"^R-\d+-", r"^W\d+-\d")},
}

# --- Deterministic path-derived catch-all (GOV-005 §5.2) --------------------
# Parameters for ukb.py::_derive_class_from_path. The catch-all removes the
# OTHER/MISC dead-end: any tracked artifact unmatched by a curated rule and by
# metadata is classified by its top-level directory / identifier prefix into a
# REAL category, guaranteeing unclassified == 0 for every present and future tree
# with no per-tree config. These are shape parameters only — no artifact, no tree.
DERIVED_CATEGORY_MAXLEN = 6       # schema-compliant category code width (2–6 preferred)
DERIVED_DEFAULT_CATEGORY = "REPO" # used only for a token that reduces to empty
DERIVED_DEFAULT_VOLUME = "VOL-000"  # thematic home when no volume matches the code


# ---------------------------------------------------------------------------
# CHAINS — real dependency chains, as ordered filename substrings.
# Consecutive members: child Depends-On predecessor; predecessor is Parent.
# The first member's parent is the BOOK root and it Depends-On the upstream
# program terminal (see CROSS_PROGRAM). Program key used for cross-program wiring.
# ---------------------------------------------------------------------------
CHAINS = {
    "CONSOLIDATION": [
        "CONSOLIDATION-PROGRAM-MASTER-INDEX",
        "CONSTITUTIONAL-RATIFICATION-REPORT",
        "CONSTITUTIONAL-ADJUDICATION-RECORD",
        "CONSTITUTIONAL-DECISION-REGISTER",
        "CONSTITUTIONAL-GOVERNANCE-GAP-REPORT",
        "CONSTITUTIONAL-REMEDIATION-PACKAGE",
        "CONSTITUENT-AUTHORITY-DETERMINATION-REPORT",
        "CONSTITUTIONAL-READINESS-CERTIFICATION",
        "CONSTITUTIONAL-CONSOLIDATION-CLOSURE-REPORT",
        "STAKEHOLDER-HANDOFF-BRIEF",
    ],
    "EES": [
        "EXTERNAL-EXECUTION-SUPPORT-PROGRAM-CHARTER",
        "EXTERNAL-ACTOR-QUALIFICATION-FRAMEWORK",
    ],
    "IMP_GOV": [
        "IMPLEMENTATION-MASTER-PLAN",
        "TECHNOLOGY-CONSTITUTION",
        "IMPLEMENTATION-PROGRAM-TRACKER",
        "IMPLEMENTATION-GOVERNANCE-BASELINE",
    ],
    "ARCH_CATALOG": [
        "UNIVERSAL-UNIVERSE-CATALOG",
        "UNIVERSAL-DOMAIN-CATALOG",
        "UNIVERSAL-CAPABILITY-CATALOG",
        "UNIVERSAL-COMPONENT-CATALOG",
    ],
    "ARCH": [
        "AGENT-CONSTRUCTION-CONSTITUTION",
        "IMPLEMENTATION-MODEL-CONSTITUTION",
        "UNIVERSAL-DATA-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-EVENT-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-API-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-WORKFLOW-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-SERVICE-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-APPLICATION-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-INTEGRATION-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-SECURITY-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-INFRASTRUCTURE-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-OBSERVABILITY-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-OPERATIONS-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-BCDR-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-TESTING-QUALITY-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-CERTIFICATION-ARCHITECTURE-CONSTITUTION",
        "UNIVERSAL-AI-ARCHITECTURE-CONSTITUTION",
    ],
    "CAT": [
        "CANONICAL-RUNTIME-CATALOG-CONSTITUTION",
        "CANONICAL-DATA-CATALOG",
        "CANONICAL-EVENT-CATALOG",
        "CANONICAL-API-CATALOG",
        "CANONICAL-WORKFLOW-CATALOG",
        "CANONICAL-SERVICE-CATALOG",
        "CANONICAL-APPLICATION-CATALOG",
    ],
    "REF": [
        "REFERENCE-ARCHITECTURE-CONSTITUTION",
        "REFERENCE-DATA-ARCHITECTURE",
        "REFERENCE-EVENT-ARCHITECTURE",
        "REFERENCE-API-ARCHITECTURE",
        "REFERENCE-WORKFLOW-ARCHITECTURE",
        "REFERENCE-SERVICE-ARCHITECTURE",
        "REFERENCE-APPLICATION-ARCHITECTURE",
    ],
    "GEN": [
        "GENERATION-FRAMEWORK-CONSTITUTION",
        "DATA-GENERATION-FRAMEWORK",
        "EVENT-GENERATION-FRAMEWORK",
        "API-GENERATION-FRAMEWORK",
        "WORKFLOW-GENERATION-FRAMEWORK",
        "SERVICE-GENERATION-FRAMEWORK",
        "APPLICATION-GENERATION-FRAMEWORK",
    ],
    "IMP": [
        "FOUNDATION-ARCHITECTURE",
        "REPOSITORY-ARCHITECTURE",
        "ONTOLOGY-PLATFORM",
        "REGISTRY-PLATFORM",
        "IDENTITY-PLATFORM",
        "KNOWLEDGE-GRAPH-ENGINE",
        "UNIVERSAL-COMPILER",
        "RUNTIME-PLATFORM",
        "API-PLATFORM",
        "WORKFLOW-PLATFORM",
        "AI-PLATFORM",
        "APPLICATION-FACTORY",
        "ECOSYSTEM-PLATFORM",
        "PRODUCTION-PLATFORM",
    ],
    # ENG chain order is FIXED BY REPOSITORY TRUTH, not by filename or by the
    # UCOS-ENG-NNNNNN allocation order. The authoritative EL-1 Existence-Primitive
    # sequence is ENG-GOV-001 (07-ENGINEERING/UCOS-Ω∞-ENGINEERING-ROADMAP-
    # RECONCILIATION-DETERMINATION.md) Output 11, OPTION B (SELECTED):
    #
    #   ENG-000 Index → ENG-001 Identity → ENG-002 Object → ENG-003 Value
    #                 → ENG-004 Type     → ENG-005 Relationship & Reference
    #
    # Type MUST precede Relationship & Reference: relationship kinds, cardinalities
    # and reference classes are themselves typed, so ENG-005 Depends-On ENG-004
    # (ENG-004 §"Sequencing Note"; ENG-GOV-001 Output 11 / F-05; ENG-000 ENG-L-05/06
    # downward-only + acyclic). Emitting the chain in any other order manufactures a
    # structural:chain Depends-On edge that contradicts the artifacts' own declared
    # metadata and creates a prohibited lineage cycle (CEP-009 Art XV.2).
    # Corrective change under CEP-009 Article IV.3 (UCCEP-000005 / WP-UCCEP-003 T-1);
    # DATA ONLY — no identifier is allocated, renumbered or released here.
    "ENG": [
        "ENGINEERING-PROGRAM-MASTER-INDEX",
        "UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE",
        "UNIVERSAL-OBJECT-SYSTEM-MASTER-ARCHITECTURE",
        "UNIVERSAL-VALUE-SYSTEM-MASTER-ARCHITECTURE",
        "UNIVERSAL-TYPE-SYSTEM-MASTER-ARCHITECTURE",
        "UNIVERSAL-RELATIONSHIP-REFERENCE-SYSTEM-MASTER-ARCHITECTURE",
    ],
    "RUN": [
        "RUNTIME-001-UNIVERSAL-RUNTIME-CONSTITUTION",
        "RUNTIME-002-UNIVERSAL-RUNTIME-THEORY",
        "RUNTIME-003-UNIVERSAL-RUNTIME-ONTOLOGY",
        "RUNTIME-004-UNIVERSAL-RUNTIME-TAXONOMY",
        "RUNTIME-005-UNIVERSAL-RUNTIME-META-MODEL",
        "RUNTIME-006-UNIVERSAL-EXECUTION-ARCHITECTURE",
        "RUNTIME-007-UNIVERSAL-STATE-ARCHITECTURE",
        "RUNTIME-008-UNIVERSAL-EVENT-ARCHITECTURE",
        "RUNTIME-009-UNIVERSAL-WORKFLOW-ARCHITECTURE",
        "RUNTIME-010-UNIVERSAL-POLICY-ARCHITECTURE",
        "RUNTIME-011-UNIVERSAL-AGENT-ARCHITECTURE",
        "RUNTIME-012-UNIVERSAL-CONTEXT-ARCHITECTURE",
        "RUNTIME-013-UNIVERSAL-ORCHESTRATION-ARCHITECTURE",
        "RUNTIME-014-UNIVERSAL-RUNTIME-INTEGRATION-ARCHITECTURE",
    ],
    # --- Platform Architecture Program (PHASE-003) dependency chain. Append-only.
    #     Ordered by governance-then-foundation sequence: the program-establishment
    #     determination (PLATFORM-GOV-000) is the chain head and program root; the
    #     five foundation artifacts (Constitution→Theory→Ontology→Taxonomy→Meta-Model)
    #     follow the RUNTIME-001..005 pattern; the package determination closes it.
    #     Substrings are unique basenames so find_uid resolves each unambiguously.
    #     First member Depends-On the RUN terminal via CROSS_PROGRAM below.
    "PLATFORM": [
        "PLATFORM-GOV-000",
        "PLATFORM-001-UNIVERSAL-PLATFORM-CONSTITUTION",
        "PLATFORM-002-UNIVERSAL-PLATFORM-THEORY",
        "PLATFORM-003-UNIVERSAL-PLATFORM-ONTOLOGY",
        "PLATFORM-004-UNIVERSAL-PLATFORM-TAXONOMY",
        "PLATFORM-005-UNIVERSAL-PLATFORM-META-MODEL",
        "PLATFORM-FOUNDATION-PACKAGE-DETERMINATION",
        # --- Remaining Platform Foundation sequence (PLATFORM-006…018). Append-only;
        #     approved chain 005 → PACKAGE-DETERMINATION → 006 → … → 018. Each
        #     substring is a unique basename so find_uid resolves each unambiguously.
        "PLATFORM-006-UNIVERSAL-PLATFORM-CAPABILITY-ARCHITECTURE",
        "PLATFORM-007-UNIVERSAL-PLATFORM-COMPONENT-ARCHITECTURE",
        "PLATFORM-008-UNIVERSAL-PLATFORM-SERVICE-ARCHITECTURE",
        "PLATFORM-009-UNIVERSAL-PLATFORM-EXPERIENCE-ARCHITECTURE",
        "PLATFORM-010-UNIVERSAL-PLATFORM-COMPOSITION-ARCHITECTURE",
        "PLATFORM-011-UNIVERSAL-PLATFORM-INTEGRATION-ARCHITECTURE",
        "PLATFORM-012-UNIVERSAL-PLATFORM-RUNTIME-ARCHITECTURE",
        "PLATFORM-013-UNIVERSAL-PLATFORM-DEPLOYMENT-ARCHITECTURE",
        "PLATFORM-014-UNIVERSAL-PLATFORM-REFERENCE-ARCHITECTURE",
        "PLATFORM-015-PLATFORM-FOUNDATION-FREEZE-DETERMINATION",
        "PLATFORM-016-PLATFORM-READINESS-DETERMINATION",
        "PLATFORM-017-PLATFORM-COMPLETION-DETERMINATION",
        "PLATFORM-018-PLATFORM-MASTER-REGISTRY",
    ],
    # --- Data Architecture Program (PHASE-004) dependency chain. Append-only.
    #     Founded downward-only on the frozen PL-F2 platform program: the chain
    #     head (DATA-GOV-000) Depends-On the PLATFORM terminal via CROSS_PROGRAM.
    #     Only the establishment determination exists today; DATA-001…018 append
    #     here as they are authored (UCI-001; no renumber).
    "DATA": [
        "DATA-GOV-000",
        # --- Data Foundation sequence (DATA-001…018). Append-only; approved chain
        #     GOV-000 → 001 → … → 018. Each substring is a unique basename so
        #     find_uid resolves each unambiguously (REG-AUTO-001 §12; UCI-001).
        "DATA-001-UNIVERSAL-DATA-CONSTITUTION",
        "DATA-002-UNIVERSAL-DATA-THEORY",
        "DATA-003-UNIVERSAL-DATA-ONTOLOGY",
        "DATA-004-UNIVERSAL-DATA-TAXONOMY",
        "DATA-005-UNIVERSAL-DATA-META-MODEL",
        "DATA-006-UNIVERSAL-DATA-ENTITY-ARCHITECTURE",
        "DATA-007-UNIVERSAL-DATA-ATTRIBUTE-ARCHITECTURE",
        "DATA-008-UNIVERSAL-DATA-RELATIONSHIP-ARCHITECTURE",
        "DATA-009-UNIVERSAL-DATA-SCHEMA-ARCHITECTURE",
        "DATA-010-UNIVERSAL-DATA-STORAGE-ARCHITECTURE",
        "DATA-011-UNIVERSAL-DATA-LIFECYCLE-ARCHITECTURE",
        "DATA-012-UNIVERSAL-DATA-GOVERNANCE-ARCHITECTURE",
        "DATA-013-UNIVERSAL-DATA-QUALITY-ARCHITECTURE",
        "DATA-014-UNIVERSAL-DATA-SECURITY-ARCHITECTURE",
        "DATA-015-DATA-FOUNDATION-FREEZE-DETERMINATION",
        "DATA-016-DATA-READINESS-DETERMINATION",
        "DATA-017-DATA-COMPLETION-DETERMINATION",
        "DATA-018-DATA-MASTER-REGISTRY",
    ],
    # --- Service Architecture Program (PHASE-005) dependency chain. Append-only.
    #     Founded downward-only on the frozen DF-2 data program: the chain head
    #     (SERVICE-GOV-000) Depends-On the DATA terminal via CROSS_PROGRAM. The
    #     establishment determination plus SERVICE-001…018 append here in numeric
    #     order; each substring is a unique basename so find_uid resolves each
    #     unambiguously (REG-AUTO-001 §12; UCI-001; no renumber).
    "SERVICE": [
        "SERVICE-GOV-000",
        "SERVICE-001-UNIVERSAL-SERVICE-CONSTITUTION",
        "SERVICE-002-UNIVERSAL-SERVICE-THEORY",
        "SERVICE-003-UNIVERSAL-SERVICE-ONTOLOGY",
        "SERVICE-004-UNIVERSAL-SERVICE-TAXONOMY",
        "SERVICE-005-UNIVERSAL-SERVICE-META-MODEL",
        "SERVICE-006-UNIVERSAL-SERVICE-CAPABILITY-ARCHITECTURE",
        "SERVICE-007-UNIVERSAL-SERVICE-CONTRACT-ARCHITECTURE",
        "SERVICE-008-UNIVERSAL-SERVICE-INTERFACE-ARCHITECTURE",
        "SERVICE-009-UNIVERSAL-SERVICE-OPERATION-ARCHITECTURE",
        "SERVICE-010-UNIVERSAL-SERVICE-COMPOSITION-ARCHITECTURE",
        "SERVICE-011-UNIVERSAL-SERVICE-ORCHESTRATION-ARCHITECTURE",
        "SERVICE-012-UNIVERSAL-SERVICE-EXECUTION-ARCHITECTURE",
        "SERVICE-013-UNIVERSAL-SERVICE-POLICY-ARCHITECTURE",
        "SERVICE-014-UNIVERSAL-SERVICE-SECURITY-ARCHITECTURE",
        "SERVICE-015-SERVICE-FOUNDATION-FREEZE-DETERMINATION",
        "SERVICE-016-SERVICE-READINESS-DETERMINATION",
        "SERVICE-017-SERVICE-COMPLETION-DETERMINATION",
        "SERVICE-018-SERVICE-MASTER-REGISTRY",
    ],
    # --- UKB Advancement Program (Digital Twin) dependency chain. Append-only.
    #     Ordered by filename substring; consecutive members form Parent/Child +
    #     Depends-On edges. First member (the master index) parents to the BOOK
    #     root and Depends-On the existing UKB via CROSS_PROGRAM below. ----------
    "ADV": [
        "UKB-ADV-000-ADVANCEMENT-PROGRAM-MASTER-INDEX",
        "UKB-ADV-001-REAL-TIME-CONNECTOR-ARCHITECTURE",
        "UKB-ADV-002-REPOSITORY-INTELLIGENCE-ARCHITECTURE",
        "UKB-ADV-003-IMPLEMENTATION-TRACEABILITY-ARCHITECTURE",
        "UKB-ADV-004-TESTING-INTELLIGENCE-ARCHITECTURE",
        "UKB-ADV-005-SECURITY-INTELLIGENCE-ARCHITECTURE",
        "UKB-ADV-006-DEPLOYMENT-INTELLIGENCE-ARCHITECTURE",
        "UKB-ADV-007-PRODUCTION-INTELLIGENCE-ARCHITECTURE",
        "UKB-ADV-008-UI-UX-DIGITAL-TWIN-ARCHITECTURE",
        "UKB-ADV-009-UNIVERSAL-PUBLICATION-ENGINE-ARCHITECTURE",
        "UKB-ADV-010-NAVIGATION-PORTAL-ARCHITECTURE",
        "UKB-ADV-011-ENTERPRISE-SEARCH-ARCHITECTURE",
        "UKB-ADV-012-CONTROL-TOWER-AUTOMATION-ARCHITECTURE",
        "UKB-ADV-013-AI-KNOWLEDGE-LAYER-ARCHITECTURE",
        "UKB-ADV-014-DIGITAL-TWIN-CERTIFICATION-ARCHITECTURE",
        "UKB-ADV-015-COMPLETE-REPOSITORY-STRUCTURE",
        "UKB-ADV-016-IMPLEMENTATION-ROADMAP",
        "UKB-ADV-017-DEPENDENCY-GRAPH",
        "UKB-ADV-018-MIGRATION-PLAN",
        "UKB-ADV-019-FINAL-READINESS-DETERMINATION",
    ],
    # --- Universal Master Book Architecture Program (UMB) dependency chain.
    #     Append-only. Consecutive members form Parent/Child + Depends-On edges.
    #     The head (UMB-000 master index) parents to the BOOK root and Depends-On
    #     the ADV terminal (UKB-ADV-019) via CROSS_PROGRAM below — the Master Book
    #     Architecture consolidates and builds upon the Advancement (Digital-Twin)
    #     architecture. Each substring is a unique basename so find_uid resolves
    #     each unambiguously (REG-AUTO-001 §12; UCI-001; no renumber).
    "UMB": [
        "UMB-000-MASTER-BOOK-ARCHITECTURE-MASTER-INDEX",
        "UMB-001-MASTER-BOOK-ARCHITECTURE",
        "UMB-002-DIGITAL-TWIN-ARCHITECTURE",
        "UMB-003-IDENTITY-ARCHITECTURE",
        "UMB-004-NOMENCLATURE-ARCHITECTURE",
        "UMB-005-REGISTRY-ARCHITECTURE",
        "UMB-006-KNOWLEDGE-GRAPH-ARCHITECTURE",
        "UMB-007-TRACEABILITY-ARCHITECTURE",
        "UMB-008-CHANGE-ARCHITECTURE",
        "UMB-009-VERSION-ARCHITECTURE",
        "UMB-010-LINEAGE-ARCHITECTURE",
        "UMB-011-PUBLICATION-ARCHITECTURE",
        "UMB-012-SYNCHRONIZATION-ARCHITECTURE",
        "UMB-013-SEARCH-ARCHITECTURE",
        "UMB-014-AI-KNOWLEDGE-ARCHITECTURE",
        "UMB-015-SECURITY-ARCHITECTURE",
        "UMB-016-CONTROL-TOWER-ARCHITECTURE",
        "UMB-017-CERTIFICATION-ARCHITECTURE",
        "UMB-018-RUNTIME-ARCHITECTURE",
        "UMB-019-OPERATIONAL-ARCHITECTURE",
        "UMB-020-SUCCESS-CRITERIA-AND-UNIVERSAL-PARTICIPATION-DEMONSTRATION",
    ],
    # --- Universal Science & Intelligence Substrate (USIS) dependency chain.
    #     Appended by Wave 0 (Phase 0.3). Founded downward-only on the prior
    #     program: the chain head USIS-GOV-000 Depends-On the SERVICE terminal via
    #     CROSS_PROGRAM below (SERVICE is the last program with a defined CHAINS
    #     terminal; the 12/13/14 trees are metadata-classified, not chained). The
    #     USIS-GOV-000 corpus artifact additionally self-declares a DEPENDS-ON edge
    #     to the SECURITY terminal per the USIS-012 founding position (metadata
    #     self-declaration — the mechanism used by the 12/13/14 programs). Only the
    #     establishment determination exists in Wave 0; USIS-001…021 append here in
    #     numeric order as authored in Wave 1+ (no renumber). Each substring is a
    #     unique basename so find_uid resolves it unambiguously.
    "USIS": [
        "USIS-GOV-000-UNIVERSAL-SCIENCE-INTELLIGENCE-PROGRAM-ESTABLISHMENT-DETERMINATION",
    ],
}

# Program roots that additionally parent all non-chained members found in that
# program (e.g. RUNTIME-GOV-*, RUNTIME-REG-*, engineering determinations).
PROGRAM_ROOTS = {
    "CONSOLIDATION": "CONSOLIDATION-PROGRAM-MASTER-INDEX",
    "EES": "EXTERNAL-EXECUTION-SUPPORT-PROGRAM-CHARTER",
    "IMP": "FOUNDATION-ARCHITECTURE",
    "ARCH": "AGENT-CONSTRUCTION-CONSTITUTION",
    "CAT": "CANONICAL-RUNTIME-CATALOG-CONSTITUTION",
    "REF": "REFERENCE-ARCHITECTURE-CONSTITUTION",
    "GEN": "GENERATION-FRAMEWORK-CONSTITUTION",
    "ENG": "ENGINEERING-PROGRAM-MASTER-INDEX",
    "RUN": "RUNTIME-001-UNIVERSAL-RUNTIME-CONSTITUTION",
    # Platform Architecture Program root — append-only. Non-chained future
    # PLATFORM-* artifacts (e.g. PLATFORM-GOV-001/002/003, PLATFORM-REG-001)
    # parent to the program-establishment determination.
    "PLATFORM": "PLATFORM-GOV-000",
    # Data Architecture Program root — append-only. Non-chained future DATA-*
    # artifacts (e.g. DATA-015/016/017, DATA-018) parent to the establishment
    # determination.
    "DATA": "DATA-GOV-000",
    # Service Architecture Program root — append-only. Non-chained future
    # SERVICE-* artifacts parent to the program-establishment determination.
    "SERVICE": "SERVICE-GOV-000",
    # UKB Advancement Program (Digital Twin) root — append-only.
    "ADV": "UKB-ADV-000-ADVANCEMENT-PROGRAM-MASTER-INDEX",
    # Universal Master Book Architecture Program root — append-only. Non-chained
    # future UMB-* artifacts parent to the master index.
    "UMB": "UMB-000-MASTER-BOOK-ARCHITECTURE-MASTER-INDEX",
    # Universal Science & Intelligence Substrate root — appended by Wave 0
    # (Phase 0.3). Non-chained future USIS-* / USIS-U-* / USIS-SCI-* / USIS-DOM-*
    # / USIS-CAP-* artifacts parent to the program-establishment determination.
    "USIS": "USIS-GOV-000-UNIVERSAL-SCIENCE-INTELLIGENCE-PROGRAM-ESTABLISHMENT-DETERMINATION",
}

# Downstream ordering: each program root Depends-On the terminal of the prior.
# (program_key -> upstream chain key whose LAST element it depends on)
CROSS_PROGRAM = [
    ("CONSOLIDATION", None),
    ("EES", "CONSOLIDATION"),
    ("IMP_GOV", "CONSOLIDATION"),
    ("ARCH_CATALOG", "CONSOLIDATION"),
    ("ARCH", "ARCH_CATALOG"),
    ("CAT", "ARCH"),
    ("REF", "CAT"),
    ("GEN", "REF"),
    ("IMP", "IMP_GOV"),
    ("ENG", "ARCH"),
    ("RUN", "ARCH"),
    # Platform Architecture Program (PHASE-003) is founded downward-only upon the
    # frozen RL-F2 Runtime Program: its chain head Depends-On the RUN terminal.
    # Append-only.
    ("PLATFORM", "RUN"),
    # Data Architecture Program (PHASE-004) is founded downward-only upon the
    # frozen PL-F2 Platform Program: its chain head Depends-On the PLATFORM
    # terminal. Append-only.
    ("DATA", "PLATFORM"),
    # Service Architecture Program (PHASE-005) is founded downward-only upon the
    # frozen DF-2 Data Program: its chain head Depends-On the DATA terminal.
    # Append-only.
    ("SERVICE", "DATA"),
    # UKB Advancement Program roots at the BOOK (it advances the whole UKB); its
    # master index parents to UCOS-BOOK-000000. Append-only.
    ("ADV", None),
    # Universal Master Book Architecture Program (UMB) is founded on the ADV
    # (Digital-Twin) architecture it consolidates: its master index parents to the
    # BOOK root and Depends-On the ADV terminal (UKB-ADV-019). Append-only.
    ("UMB", "ADV"),
    # Universal Science & Intelligence Substrate (USIS / EIP-018) is founded
    # downward-only on the prior program: its chain head (USIS-GOV-000) Depends-On
    # the SERVICE terminal (the last program with a defined CHAINS terminal in this
    # config; the 12/13/14 trees are metadata-classified, not chained). The
    # semantic founding edge to the SECURITY terminal (USIS-012 founding position)
    # is carried by the USIS-GOV-000 artifact's own DEPENDS-ON metadata row. Both
    # edges are downward and acyclic. Appended by Wave 0 (Phase 0.3).
    ("USIS", "SERVICE"),
]

# ---------------------------------------------------------------------------
# EXCLUSIONS — paths the generator must not register. Three distinct classes:
#   (1) the generator's OWN machinery,
#   (2) its GENERATED outputs (the registry must not list itself),
#   (3) OPERATIONAL MEMORY — execution/coordination state, NOT repository corpus.
# Repository Corpus is knowledge state; Operational Memory is execution state;
# Generated Projections are derived state. Only Repository Corpus is registered
# (UCOS-RECON-C1). Excluding a path is append-only-safe: any identifier already
# allocated to a now-excluded path is RETAINED-BUT-RETIRED in the id-ledger
# (never renumbered, never reused, never emitted) — see ukb.allocate() /
# derive_change_events() (UMB-017 C-05).
# ---------------------------------------------------------------------------
EXCLUDE_DIR_PREFIXES = (
    ".git/",
    ".github/",
    ".kiro/",
    "00-BOOK/tools/",
    "00-BOOK/DATA/",
    "00-BOOK/REGISTRIES/",
    "00-BOOK/CONTROL-TOWER/",
    "00-BOOK/VOLUMES/",
    # Appended by the UKB Advancement Program — generated navigation portal.
    "00-BOOK/PORTAL/",
    # Operational Memory (UCOS-RECON-C1) — the Master Context System is execution
    # state, not corpus: it must never consume permanent corpus identities, never
    # appear in generated books, and never enter the portal unless explicitly
    # projected. Covers the 00-MASTER/ subsystem and the root redirect pointer
    # (a startswith() prefix that matches exactly that one operational-memory file).
    "00-MASTER/",
    "MCP-001-MASTER-CONTEXT-AND-EXECUTION-SYSTEM.md",
    # Generated Projections (class 2) emitted OUTSIDE 00-BOOK — the UCOS-RIE-001
    # Repository Intelligence Engine output family. Closes the same defect
    # UCOS-RECON-C1 closed for Operational Memory, on the leg that was still open:
    # this list enumerated the generator's generated outputs only where they live
    # under 00-BOOK/, so a generated family emitted anywhere else was admitted into
    # the Repository Corpus. `intelligence/` did not exist when the list was
    # authored — verbatim the RECON-C1 root cause.
    #
    # These files are DERIVED STATE, not knowledge state: every one declares
    # "authority": "NONE (derived truth)" in its own envelope, and the baseline
    # declares itself "a GENERATED OUTPUT of UCOS-RIE-001". Under GOV-005 §5.3 a
    # GENERATED ARTIFACT is "regenerated, never hand-registered", so it is not an
    # eligible repository artifact.
    #
    # Registering them is not merely a mis-classification, it is UNSATISFIABLE.
    # Registration must record an artifact's content_hash, but every RIE output
    # embeds (a) HEAD's own commit id and committer date and (b) the sha256 of the
    # 00-BOOK/DATA projections that registration itself regenerates. So the bytes
    # that must be registered are a function of the commit that will contain them
    # and of the register that records them: committing changes HEAD, which changes
    # the required bytes, which changes the register — a self-referential relation
    # with no fixpoint (reaching one would require a commit whose hash appears in
    # its own tree). CK-REG-DRIFT could therefore never hold across a regeneration,
    # which is why "regenerate at the committed anchor" has recurred without ever
    # converging. RIE also derives from gitignored coverage.xml, so its content is
    # not even a function of the repository alone.
    #
    # Family prefixes, not artifact names: every present and FUTURE output of this
    # producer is covered, and nothing else is. Deliberately NOT the broader
    # "intelligence/UCOS-" — that would also capture
    # intelligence/UCOS-UPI-001/publication-formats.json, the authored format
    # descriptor the ignore authority explicitly re-admits as registerable.
    # Append-only-safe: the 11 identities already allocated to these paths are
    # RETAINED-BUT-RETIRED in the id-ledger per derive_change_events (UMB-017 C-05).
    "intelligence/UCOS-RIE-",
    "intelligence/UCOS-IMP-BASELINE-001.",
    # Generated Context Projections (UCOS-UCTX-001) — the canonical context root and
    # every agent-facing surface derived from it. Same class and same reason as the
    # PORTAL / REGISTRIES / CONTROL-TOWER entries above: these are GENERATED VIEWS of
    # instruments that already hold the knowledge, emitted by 00-BOOK/tools/ukctx.py
    # and declared in 00-BOOK/DATA/generated-artifact-registry.json. Under GOV-005
    # §5.3 a generated artifact is regenerated, never hand-registered, so it is not an
    # eligible repository artifact and must not consume a permanent corpus identity.
    #
    # Registering them would also be UNSATISFIABLE in the same way the RIE family is:
    # 00-BOOK/CONTEXT/MANIFEST.json records the content digest of every sibling
    # projection, and corpus registration would add a registry entry whose own hash is
    # an input to the manifest that registration just recorded — no fixpoint.
    #
    # These are NOT excluded from UCOS-UGA-001 object identity. Every one is still a
    # tracked object and still carries a by_object Universal ID; exclusion here is a
    # statement about which REGISTER lists them, never a licence to exist anonymously.
    "00-BOOK/CONTEXT/",
    ".claude/",
    ".cursor/",
    "AGENTS.md",
)

# Only these file extensions are registered as artifacts.
INCLUDE_EXTENSIONS = (".md", ".txt", ".docx", ".json")

# Status keywords searched (case-insensitive) near the top of a markdown artifact
# to infer lifecycle status. First match wins. These map raw labels to canonical.
STATUS_KEYWORDS = [
    ("PRODUCTION", "PRODUCTION"),
    ("DEPLOYED", "DEPLOYED"),
    ("CERTIFIED", "CERTIFIED"),
    ("FROZEN", "FROZEN"),
    ("SUPERSEDED", "SUPERSEDED"),
    ("RETIRED", "RETIRED"),
    ("COMPLETE", "COMPLETE"),
    ("ACTIVE", "ACTIVE"),
    ("FINAL", "FINAL"),
    ("APPROVED", "APPROVED"),
    ("UNDER_REVIEW", "UNDER_REVIEW"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("BLOCKED", "BLOCKED"),
    ("PLANNED", "PLANNED"),
    ("NOT STARTED", "NOT_STARTED"),
]

# Canonical-state mapping for aliases used by roll-up.
CANONICAL_ALIAS = {
    "ACTIVE": "APPROVED",
    "COMPLETE": "IMPLEMENTED",
    "FINAL": "FROZEN",
}


# ===========================================================================
# UMB-IMP-001 — AUTOMATIC REGISTRATION & ENFORCEMENT REALIZATION (append-only).
#
# The blocks below are DATA ONLY. They add metadata-driven discovery and the
# enforcement-gate configuration required to close the auto-registration gap
# identified by UMB-READINESS-001 §11 — WITHOUT hard-coding any program,
# artifact, volume, domain, or family list, and WITHOUT modifying any existing
# rule, chain, root, volume, or exclusion above (REG-AUTO-001 L4/L5; UCI-001
# CP-3/CP-6; AUTH-INF-001 infinite-expansion). Nothing here changes a prior
# classification: metadata is consulted only AFTER the ordered CLASSIFY_RULES
# and only to rescue an artifact that would otherwise fall to DEFAULT_CLASS.
# ===========================================================================

# ---------------------------------------------------------------------------
# METADATA-DRIVEN CLASSIFICATION — an artifact may self-declare its own
# classification in its front-matter table, e.g.:
#     | PROGRAM  | UMB      |
#     | CATEGORY | UMB      |
#     | VOLUME   | VOL-022  |
#     | FAMILY   | MASTER-BOOK |
# This makes discovery of NEW programs / categories / volumes / domains /
# families configuration-free (metadata-driven). Each entry maps a canonical
# field to the ordered list of front-matter labels that declare it (first row
# found wins). Adding a future field here is append-only and never renames an
# existing one.
# ---------------------------------------------------------------------------
METADATA_CLASSIFY_KEYS = {
    "program":  ("UCOS-PROGRAM", "PROGRAM"),
    "category": ("UCOS-CATEGORY", "CATEGORY", "ID NAMESPACE"),
    "volume":   ("UCOS-VOLUME", "VOLUME"),
    "family":   ("UCOS-FAMILY", "FAMILY"),
    "domain":   ("UCOS-DOMAIN", "STATUS DOMAIN"),
}

# When an artifact self-declares a program/category but no volume, its volume is
# resolved (in order): declared VOLUME row -> a volume whose category equals the
# declared category -> DEFAULT_CLASS volume. No volume list is hard-coded here;
# resolution is computed at runtime against VOLUMES + discovered volumes.
METADATA_DEFAULT_VOLUME = "VOL-000"

# ---------------------------------------------------------------------------
# ENFORCEMENT GATES — the minimum set of gates that make "Artifact Creation =
# Artifact Registration" unskippable (REG-AUTO-001 §16; UMB-IMP-001). Order is
# significant (fail-fast). Data-only; the mechanism lives in ukb.py::cmd_enforce.
#   * eligibility   — the file is in scope: carried by version control (tracked or
#                     staged), of an INCLUDE_EXTENSIONS type, and not EXCLUDE_*.
#   * validity      — the file is readable, non-empty, and carries a title/identity.
#   * classification — the file resolves to a real (program != OTHER) class, via a
#                      CLASSIFY_RULES match OR self-declared metadata.
#   * registration  — the file is present in every synchronized register.
# ---------------------------------------------------------------------------
ENFORCEMENT_GATES = ("eligibility", "validity", "classification", "registration")

# The enforcement-gate audit log is runtime telemetry, not a registry. Its NAME,
# LOCATION (.runtime/governance/), single writer, and sequence authority live in
# 00-BOOK/tools/governance_telemetry.py (EC3 Phase-3) — never under 00-BOOK/DATA.

# Minimum content bytes for an in-scope text artifact to pass the validity gate.
MIN_ARTIFACT_BYTES = 1



# ===========================================================================
# UMB-IMP-002 — TRACEABILITY SPINE & TYPED KNOWLEDGE GRAPH REALIZATION
#               (append-only).
#
# The blocks below are DATA ONLY. They declare the metadata-driven relationship
# vocabulary that turns the structural graph (Parent/Child/Depends-On) into a
# typed SEMANTIC graph and populates the (currently-empty) `traceability` spine —
# WITHOUT hard-coding any program, domain, volume, family, artifact, or a closed
# relationship-type list, and WITHOUT modifying any rule, chain, root, volume,
# exclusion, or metadata block above (REG-AUTO-001 L4/L5; UCI-001 CP-3/CP-6;
# AUTH-INF-001 CR-INF-007/008/010 infinite expansion).
#
# Zero hard coding: this registry declares RELATIONSHIP *TYPES* and the
# front-matter row LABELS that declare them — never the programs/artifacts that
# participate. Relationship discovery is therefore metadata-driven and
# relationship participation is configuration-driven, exactly as the mission
# requires. Adding a future relationship type here is append-only and never
# rewrites an existing one (CR-INF-007 "a new relationship type is a new value,
# never a rewrite").
#
# Infinite expansion: the vocabulary is OPEN. Any type declared here (or any
# well-formed type an artifact self-declares via a `RELATES <Type>` row) is
# emitted; there is no compiled-in ceiling on edge/relationship types.
# ===========================================================================

# ---------------------------------------------------------------------------
# RELATIONSHIP_TYPES — the typed-edge vocabulary. Ordered, append-only. Each:
#   type          canonical forward relationship type (graph edge `type`).
#   inverse       the materialized inverse type (bidirectional navigation).
#   labels        front-matter row labels whose cell VALUE declares outbound
#                 edges of this type (matched case-insensitively; a row label
#                 may carry a parenthetical qualifier, e.g. "CONSUMES (read-only)").
#                 A type with an empty label list is a REGISTERED-BUT-UNSOURCED
#                 vocabulary member (available for future/self-declared use) —
#                 its presence proves the vocabulary is open, not closed.
#   subject_lane  traceability spine lane populated ON THE DECLARING artifact
#                 (it points to the resolved/─external target). None ⇒ graph-only.
#   object_lane   traceability spine lane populated ON THE TARGET artifact
#                 (reverse hop back to the declarer). None ⇒ graph-only.
#
# The spine lanes are exactly the canonical `traceability` fields of
# artifact.schema.json (requirement → architecture → design → implementation →
# source_code → *_test → certification → deployment → production → operations).
# No new traceability store is created (UCI-001 Part XVII.4; UMB-007 §6): the
# spine is a derived composition of these edges + the `traceability` field.
# ---------------------------------------------------------------------------
RELATIONSHIP_TYPES = [
    # --- structural (already emitted from CHAINS/CROSS_PROGRAM; listed so the
    #     vocabulary is complete and the inverses are declared once). ----------
    {"type": "Parent",       "inverse": "Child",         "labels": ["PARENT"],
     "subject_lane": "architecture", "object_lane": None},
    {"type": "Depends-On",   "inverse": "Required-By",   "labels": ["DEPENDS-ON", "DEPENDS ON"],
     "subject_lane": "architecture", "object_lane": None},

    # --- authority / requirement origin -------------------------------------
    {"type": "Authorized-By", "inverse": "Authorizes",   "labels": ["AUTHORITY", "AUTHORITIES", "AUTHORIZED-BY", "GOVERNED-BY"],
     "subject_lane": "requirement", "object_lane": None},

    # --- implementation ------------------------------------------------------
    {"type": "Implements",   "inverse": "Implemented-By", "labels": ["IMPLEMENTS", "REALIZES"],
     "subject_lane": "architecture", "object_lane": "implementation"},

    # --- consumption / production (read/write coupling) ----------------------
    {"type": "Consumes",     "inverse": "Consumed-By",   "labels": ["CONSUMES", "USES", "READS"],
     "subject_lane": "architecture", "object_lane": None},
    {"type": "References",   "inverse": "Referenced-By", "labels": ["REFERENCES", "SEE-ALSO"],
     "subject_lane": None, "object_lane": None},
    {"type": "Produces",     "inverse": "Produced-By",   "labels": ["PRODUCES", "EMITS", "WRITES"],
     "subject_lane": "production", "object_lane": None},

    # --- certification / registration / publication / security --------------
    {"type": "Certifies",    "inverse": "Certified-By",  "labels": ["CERTIFIES"],
     "subject_lane": "certification", "object_lane": "certification"},
    {"type": "Registers",    "inverse": "Registered-By", "labels": ["REGISTERS"],
     "subject_lane": None, "object_lane": None},
    {"type": "Publishes",    "inverse": "Published-By",  "labels": ["PUBLISHES"],
     "subject_lane": "production", "object_lane": None},
    {"type": "Secures",      "inverse": "Secured-By",    "labels": ["SECURES"],
     "subject_lane": "security_test", "object_lane": None},

    # --- test / deployment lifecycle hops -----------------------------------
    {"type": "Tests",        "inverse": "Tested-By",     "labels": ["TESTS"],
     "subject_lane": "unit_test", "object_lane": "unit_test"},
    {"type": "Deploys",      "inverse": "Deployed-By",   "labels": ["DEPLOYS"],
     "subject_lane": "deployment", "object_lane": "deployment"},

    # --- lineage / evolution (graph-only; feeds UMB-010 lineage projection) --
    {"type": "Supersedes",   "inverse": "Superseded-By", "labels": ["SUPERSEDES"],
     "subject_lane": None, "object_lane": None},
    {"type": "Evolves-To",   "inverse": "Evolved-From",  "labels": ["EVOLVES-TO", "EVOLVES TO"],
     "subject_lane": None, "object_lane": None},

    # --- generic traceability hop (explicit spine linkage) ------------------
    {"type": "Traces-To",    "inverse": "Traced-From",   "labels": ["TRACES-TO", "TRACES TO"],
     "subject_lane": "requirement", "object_lane": None},
]

# Front-matter label used by an artifact to self-declare an edge of an arbitrary
# (possibly future / not-yet-registered) relationship type, proving the
# vocabulary is unbounded (AUTH-INF-001 CR-INF-007). Example row:
#     | RELATES Federates | UMB-012 |
# The token after the label word is taken verbatim as the edge `type` (and a
# "<Type>-Inverse" reverse edge is materialized) with no config edit required.
RELATIONSHIP_FREEFORM_LABEL = "RELATES"

# A relationship-declaring cell lists one or more artifact references separated by
# ';' or ','. Each reference is a native identifier that may be:
#   * plain            UMB-006 · UMB-IMP-001 · RUNTIME-001 · STATUS-001
#   * slash-compressed  UMB-005/006/007         → UMB-005, UMB-006, UMB-007
#   * ellipsis-range    UKB-ADV-003…007 (or -)  → UKB-ADV-003 … UKB-ADV-007
# Trailing parenthetical qualifiers ("(read-only targets)") and the literal token
# NONE are ignored. This parser hard-codes NO artifact — it recognises the
# UCOS native-ID SHAPE only, then resolves against the live registry.
RELATIONSHIP_REF_SEPARATORS = (";", ",", "·")
RELATIONSHIP_NULL_TOKENS = ("NONE", "N/A", "—", "-", "TBD", "")



# ===========================================================================
# UMB-IMP-003 — CHANGE, VERSION, AND LINEAGE INTELLIGENCE REALIZATION
#               (append-only).
#
# The blocks below are DATA ONLY. They declare the metadata-driven vocabulary
# that turns the append-only artifact ledger + typed knowledge graph into a
# CHANGE / VERSION / LINEAGE / EVOLUTION intelligence surface — WITHOUT
# hard-coding any program, domain, volume, family, artifact, version FORMAT, or
# a closed relationship-type list, and WITHOUT modifying any rule, chain, root,
# volume, exclusion, metadata, or relationship block above (REG-AUTO-001 L4/L5;
# UCI-001 CP-3/CP-6; AUTH-INF-001 CR-INF-007/008/010 infinite expansion).
#
# Zero hard coding: change events, version history, lineage chains, and the
# evolution timeline are DERIVED at build time from (a) the append-only ledger
# snapshot history (content_hash + version + status per Universal ID, preserved
# across builds — UMB-009 §2), (b) the existing lineage relationship edges, and
# (c) git history for causation — never from an enumerated artifact/format list.
# Creates NO new registry/store as a source of truth (UMB-008 §2/§3; UMB-009
# §1; UMB-010 §1; UCI-001 IP-3/IP-6): the derived views (change-ledger.json + the
# CHANGE-VERSION-LINEAGE registry markdown) are regenerated deterministically
# each transaction, exactly like control-tower.json / relationships.json.
# ===========================================================================

# ---------------------------------------------------------------------------
# VERSION_METADATA_KEYS — front-matter labels by which an artifact may
# self-declare its version. SCHEME-AGNOSTIC: the token is captured verbatim
# (semver 1.4.2, calendar 2026.07.16, revision REV-C, tag v3, or any future
# scheme). No version format is compiled in (UMB-009 §6; AUTH-INF-001 CR-INF-008).
# The semver-constrained artifact.schema.json `version` field keeps its default
# unless the declared token is itself a valid semver; the RAW declared token is
# always preserved in the ledger snapshot history so the version engine supports
# every existing and future scheme without schema change.
# ---------------------------------------------------------------------------
VERSION_METADATA_KEYS = ("UCOS-VERSION", "VERSION", "ARTIFACT VERSION")

# Semver shape used ONLY to decide whether a declared version may also populate
# the schema-constrained artifact `version` field. It is NOT a required format:
# a non-matching token is still captured verbatim in the snapshot history.
VERSION_SEMVER_SHAPE = r"^[0-9]+\.[0-9]+\.[0-9]+$"

# ---------------------------------------------------------------------------
# CHANGE_EVENT_TYPES — the OPEN, append-only change-event vocabulary. Each event
# is DERIVED (never stored as a first-class artifact/registry — UMB-008 §2/§3)
# by comparing consecutive append-only ledger snapshots of the SAME Universal ID.
# A change event is bound to its subject Universal ID (a real graph node), so it
# is graph-participating and bidirectionally navigable, WITHOUT introducing a
# dangling graph endpoint (UMB-017 C-05 referential integrity preserved).
#
# Adding a future event kind here is append-only and never rewrites an existing
# one (CR-INF-007). Kinds with a `status` trigger fire on a lifecycle transition
# INTO that status; the structural kinds (Created/Modified/Moved/Renamed) fire on
# first-observation / content-hash / path deltas between snapshots.
# ---------------------------------------------------------------------------
CHANGE_EVENT_TYPES = [
    {"kind": "Created",             "trigger": "first-snapshot"},
    {"kind": "Modified",            "trigger": "content-hash-delta"},
    {"kind": "Moved",               "trigger": "path-delta"},
    {"kind": "Renamed",             "trigger": "name-delta"},
    {"kind": "Version-Incremented", "trigger": "version-delta"},
    {"kind": "Deprecated",          "trigger": "status", "status": "DEPRECATED"},
    {"kind": "Superseded",          "trigger": "status", "status": "SUPERSEDED"},
    {"kind": "Retired",             "trigger": "status", "status": "RETIRED"},
    {"kind": "Restored",            "trigger": "restore"},     # terminal → active again
    {"kind": "Reactivated",         "trigger": "reactivate"},  # inactive → active status
    {"kind": "Deletion-Attempted",  "trigger": "disappeared"}, # was registered, now absent on disk
]

# Lifecycle statuses treated as "terminal / inactive" for Restored/Reactivated
# derivation. Data-only; no artifact is enumerated.
CHANGE_TERMINAL_STATUSES = ("SUPERSEDED", "RETIRED", "DEPRECATED")

# Deterministic identifier prefix for a DERIVED change event (bound to a subject
# Universal ID; not a registered artifact and never allocated in the id-ledger).
CHANGE_EVENT_ID_PREFIX = "UCHG"

# Derived-view output (regenerated deterministically every transaction; NOT an
# append-only source of truth — the source of truth is the ledger snapshot
# history + relationship edges + git). Lives under DATA/ (excluded from
# registration) exactly like control-tower.json / twin.json.
CHANGE_LEDGER_FILE = "change-ledger.json"

# ---------------------------------------------------------------------------
# LINEAGE relationship types — appended to the OPEN relationship vocabulary so
# lineage/evolution are a PROJECTION of the one typed graph (UMB-010 §2), not a
# separate store. These extend RELATIONSHIP_TYPES append-only; no existing entry
# is modified (CR-INF-007). Metadata declares them by label; each materializes a
# bidirectional inverse so lineage is navigable in both directions (UMB-010 §6).
# Types already present in RELATIONSHIP_TYPES (Supersedes/Superseded-By and
# Evolves-To/Evolved-From) are reused as-is and NOT redeclared here.
# ---------------------------------------------------------------------------
RELATIONSHIP_TYPES += [
    {"type": "Evolves-From", "inverse": "Evolves-From-Inverse",
     "labels": ["EVOLVES-FROM", "EVOLVES FROM"], "subject_lane": None, "object_lane": None},
    {"type": "Created-From", "inverse": "Created-Into",
     "labels": ["CREATED-FROM", "CREATED FROM"], "subject_lane": None, "object_lane": None},
    {"type": "Derived-From", "inverse": "Derived-Into",
     "labels": ["DERIVED-FROM", "DERIVED FROM"], "subject_lane": None, "object_lane": None},
    {"type": "Forked-From", "inverse": "Forked-Into",
     "labels": ["FORKED-FROM", "FORKED FROM"], "subject_lane": None, "object_lane": None},
    {"type": "Replaced-By", "inverse": "Replaces",
     "labels": ["REPLACED-BY", "REPLACED BY"], "subject_lane": None, "object_lane": None},
    {"type": "Merged-Into", "inverse": "Merged-From",
     "labels": ["MERGED-INTO", "MERGED INTO"], "subject_lane": None, "object_lane": None},
]

# Which edge TYPES constitute a lineage chain, and in which direction they point
# relative to the declaring node. Data-only; the lineage engine walks these over
# the materialized (bidirectional) edges, so every chain is traversable both ways
# regardless of which end declared it. Append-only; no artifact is enumerated.
#   ANCESTOR   — an outbound edge of this type points to a PREDECESSOR/origin.
#   DESCENDANT — an outbound edge of this type points to a SUCCESSOR/derivative.
LINEAGE_ANCESTOR_EDGE_TYPES = (
    "Supersedes", "Evolves-From", "Evolved-From", "Created-From",
    "Derived-From", "Forked-From",
)
LINEAGE_DESCENDANT_EDGE_TYPES = (
    "Superseded-By", "Evolves-To", "Evolves-From-Inverse", "Replaced-By",
    "Merged-Into", "Created-Into", "Derived-Into", "Forked-Into",
)



# ===========================================================================
# UMB-IMP-004 — LIVE CONNECTORS & AUTO-SYNCHRONIZATION REALIZATION
#               (append-only).
#
# DATA ONLY. Declares the synchronization-runtime configuration that turns the
# existing connector layer (connectors/*) + append-only Signal ledger into an
# audited, verifiable, recoverable, schedulable State-Synchronization runtime
# (UMB-012 §2 State surface). It hard-codes NO connector: connectors are
# discovered dynamically (connectors.discover()); this block declares only
# SCHEDULING CADENCE DEFAULTS, VERIFICATION gates, and AUDIT/output file names.
# Adding a connector never requires editing this block (AUTH-INF-001
# CR-INF-003/010 — no connector list, no ceiling). No new store, identifier, or
# lifecycle is introduced: the sync-audit log is an operational append-only log
# (like enforcement-audit.json), and roll-up remains the existing pure function.
# ===========================================================================

# The synchronization-run audit log is runtime telemetry, not a registry. Its
# NAME, LOCATION (.runtime/governance/), single writer, and sequence authority
# live in 00-BOOK/tools/governance_telemetry.py (EC3 Phase-3) — never in DATA/.

# The synchronization pipeline stages proven per run (UMB-012 §3). Data-only
# labels for the audit record; the mechanism lives in ukbx.py::cmd_sync.
SYNC_STAGES = ("discover", "monitor", "detect", "execute", "verify", "audit", "recover")

# Default polling cadence, in seconds, used by `ukbx sync --due` to decide whether
# a connector is DUE since its last successful run recorded in the sync-audit log.
# This is a DEFAULT only; a connector may override it by declaring `cadence_seconds`
# on its class. No connector is named here (scheduling is cadence-driven, not
# list-driven) so unlimited future connectors schedule with zero config edit.
SYNC_DEFAULT_CADENCE_SECONDS = 900  # 15 minutes

# Verification gates asserted after execution, before the run is sealed
# (Synchronization Verification, UMB-012 §3 Validate/Audit). Data-only names;
# the assertions live in ukbx.py::_verify_sync. A hard gate failing fails the run
# (fail-closed); an advisory gate is reported but non-blocking.
SYNC_VERIFY_HARD_GATES = (
    "subject_resolves",      # every appended signal binds to a registered subject
    "provenance_present",    # every appended signal carries source + as_of
    "secret_free",           # no signal evidence contains a secret (RR-07)
    "cursor_monotonic",      # no connector cursor regressed (no replay loss)
    "signal_ids_unique",     # append-only signal ids are unique + gapless
)
SYNC_VERIFY_ADVISORY_GATES = (
    "subject_resolved_nonfallback",  # signal bound to a real subject, not fallback
)


# ===========================================================================
# UMB-IMP-005 — AI KNOWLEDGE & DIGITAL-TWIN INTELLIGENCE REALIZATION
#               (append-only).
#
# DATA ONLY. Declares the canonical intelligence QUESTIONS the Digital-Twin
# Intelligence surface answers (Success Gate B) and the evidence store each
# reasoning engine reads. It hard-codes NO answer and NO rule: every answer is
# DERIVED on demand from the authoritative evidence base and CITED (UMB-014 §2/§3;
# UCI-001 IP-3/IP-4; no fabrication IL-15). No AI registry/model store/identifier
# is created (UMB-014 §1; UCI-001 Part XVIII.5). The mechanism lives in
# ukbx.py::cmd_intel; this block declares only the question vocabulary (open,
# append-only) and the reasoning-engine → evidence mapping.
# ===========================================================================

# The seven canonical questions of Success Gate B, each mapped to the reasoning
# engine that answers it and the authoritative evidence view it reads. Open and
# append-only: a future question is a new entry, never a rewrite (CR-INF-007).
#   key       → intel capability keyword (CLI + programmatic)
#   engine    → the reasoning engine (UMB-IMP-005 §)
#   evidence  → the authoritative store(s)/derived view(s) it reads (read-only)
INTEL_QUESTIONS = {
    "exists":         {"engine": "Knowledge Query Engine",
                       "evidence": ("artifacts.json", "id-ledger.json")},
    "changed":        {"engine": "Change Reasoning Engine",
                       "evidence": ("change-ledger.json",)},
    "why":            {"engine": "Change Reasoning Engine (causation)",
                       "evidence": ("change-ledger.json", "git")},
    "impact":         {"engine": "Impact Reasoning Engine",
                       "evidence": ("relationships.json", "artifacts.json")},
    "depends":        {"engine": "Dependency Reasoning Engine",
                       "evidence": ("relationships.json", "artifacts.json")},
    "certifications": {"engine": "Certification Reasoning Engine",
                       "evidence": ("relationships.json", "artifacts.json", "certification.json")},
    "sync":           {"engine": "Synchronization Intelligence Engine",
                       "evidence": ("signals.json", "twin.json", "sync-audit.json")},
}

# The inbound typed-edge types that constitute a change-impact surface (who is
# affected if the subject changes). Reused by the Impact + Certification engines.
# Append-only; extends the open relationship vocabulary, enumerates no artifact.
INTEL_IMPACT_INBOUND_EDGE_TYPES = (
    "Required-By", "Consumed-By", "Referenced-By", "Implemented-By",
    "Certified-By", "Tested-By", "Deployed-By", "Secured-By", "Published-By",
    "Produced-By", "Child",
)


# ===========================================================================
# UMB-IMP-006 — DIGITAL-TWIN CERTIFICATION RUNTIME REALIZATION
#               (append-only).
#
# DATA ONLY. Declares the certification INTEGRITY DOMAINS the runtime evaluates
# (UMB-017 §1 criteria, organized by the nine integrity domains the mission
# names), the append-only certification audit log, and the persisted evidence/
# report output names. It hard-codes NO limit and NO subject: every rule is a
# machine check over the authoritative evidence base, additive (a new criterion
# is a new domain/rule — no redesign; UMB-017 §5; AUTH-INF-001 CR-INF-008/010).
# Certification is NON-TERMINAL (CR-INF-011) and creates no engine/registry/
# identifier/lifecycle (reuses ukb/ukbx validators + derived views). The
# mechanism lives in ukbx.py::cmd_certify.
# ===========================================================================

# The nine integrity domains evaluated by the certification runtime, each mapped
# to the UMB-017 §1 criteria it attests. Open, append-only: a future domain is a
# new entry, never a rewrite (CR-INF-007). No subject/limit is enumerated.
CERT_INTEGRITY_DOMAINS = (
    "identity",             # no duplicate/reused IDs or pages; append-only ledger
    "registry",             # count parity; every registered path present + valid
    "traceability",         # bidirectional closure; no orphans; return paths
    "knowledge_graph",      # no dangling edges; Depends-On acyclic; inverses
    "change_intelligence",  # change events node-bound; deterministic; append-only
    "version",              # version records consistent with append-only history
    "lineage",              # lineage nodes resolve; chains acyclic; bidirectional
    "synchronization",      # signals resolve; provenance; secret-free; cursors
    "twin_intelligence",    # dimensions computed (not MANUAL); intel answerable
)

# The certification audit trail is runtime telemetry, not a registry. Its NAME,
# LOCATION (.runtime/governance/), single writer, and sequence authority live in
# 00-BOOK/tools/governance_telemetry.py (EC3 Phase-3) — never in DATA/.

# Persisted certification evidence (derived view, regenerated each run — NOT an
# authoritative store; like control-tower.json / change-ledger.json).
CERT_EVIDENCE_FILE = "certification.json"

# Human-navigable certification report (generated markdown under REGISTRIES/).
CERT_REPORT_FILE = "CERTIFICATION-REGISTRY.md"



# ===========================================================================
# EXEC-REG-001 — UCOS AUTONOMOUS EXECUTION REGISTER (RUNTIME EXTENSION)
#               (append-only).
#
# DATA ONLY. Realizes RUNTIME-006 (Universal Execution Architecture) as a
# record-only, append-only, evidence-derived, NON-CONSTITUTIVE runtime register
# of execution INSTANCES. It hard-codes NO execution, subject, or limit; it
# declares only the identity namespace, the store file name, the forward-only
# lifecycle model (RUNTIME-006 D7 / EXL-07/10), the orthogonal RUNTIME-006 D5
# facets, and the DOMAIN-C signal mapping. It modifies no rule/chain/root/volume/
# metadata/relationship/enforcement/sync/intel/cert block above (REG-AUTO-001
# L4/L5; UCI-001 CP-3/CP-6; AUTH-INF-001 infinite expansion). Execution identity
# is minted from the ONE Universal Identity ledger authority (id-ledger.json
# category_seq via ukb.py::allocate_execution) — NOT a second identity scheme
# (RUNTIME-006 EXL-02). The register is not a runtime engine (EXL-23; the
# authorized interpretation: deterministic repository machinery is permitted).
# ===========================================================================

# Identity namespace for execution INSTANCES (minted UCOS-EXEC-NNNNNN from the
# shared append-only category_seq counter; never a second authority; append-only).
EXECUTION_CATEGORY = "EXEC"

# Append-only execution register store (runtime overlay under the already-excluded
# DATA/; regenerated deterministically; never an artifact and never self-registered).
EXECUTION_STORE_FILE = "executions.json"

# RUNTIME-006 D7 lifecycle (forward-only). suspended/resumed cycle WITHIN the
# active phase (EXL-07); completed/terminated are terminal (EXL-10). No backward
# transition exists.
EXECUTION_LIFECYCLE = ("declared", "active", "suspended", "completed", "terminated")
EXECUTION_INITIAL_STATE = "declared"
EXECUTION_TERMINAL_STATES = ("completed", "terminated")

# Legal forward-only transitions (RUNTIME-006 D7 / EXL-07/10). Any transition
# outside this map is rejected (fail-closed); a self-transition to the current
# state is an idempotent no-op.
EXECUTION_TRANSITIONS = {
    "declared":   ("active", "terminated"),
    "active":     ("suspended", "completed", "terminated"),
    "suspended":  ("active", "terminated"),
    "completed":  (),
    "terminated": (),
}

# RUNTIME-006 D5 orthogonal facets (membership by ENG-004-style typing; RXL-01/03).
EXECUTION_TYPES = ("atomic", "composite", "recurring", "conditional")
EXECUTION_CATEGORIES = ("primitive-behavior", "workflow-step", "agent-driven", "orchestrated")
EXECUTION_DEFAULT_TYPE = "atomic"
EXECUTION_DEFAULT_CATEGORY = "primitive-behavior"

# The DOMAIN-C twin/control-tower dimension executions roll up to (STATUS-001 §1;
# NEVER projected onto DOMAIN-A/B/D/E — §2 non-projection law). Append-only.
EXECUTION_DIMENSION = "execution"

# Lifecycle -> signal-state mapping. Targets are members of
# connectors.base.STATE_ORDER so the blocking-view roll-up places them
# deterministically. `terminated` maps to BLOCKED so a non-successful terminal
# execution surfaces as risk (never hidden), mirroring the blocking-view semantics.
EXECUTION_STATE_TO_SIGNAL = {
    "declared":   "PLANNED",
    "active":     "IN_PROGRESS",
    "suspended":  "STALE",
    "completed":  "COMPLETE",
    "terminated": "BLOCKED",
}

# Append the execution integrity domain to the certification runtime (append-only;
# a new criterion is a new domain, never a rewrite — CR-INF-007). Registration/
# runtime certification only; artifact-level DOMAIN-D certification stays separate
# and evidence-based (STATUS-001).
CERT_INTEGRITY_DOMAINS = CERT_INTEGRITY_DOMAINS + ("execution",)



# ===========================================================================
# REG-AUTO-001 §21 — RECONCILED-SET DECLARATION (CMG-DLG-13 / CMG-OQ-06)
#               (append-only, DATA ONLY).
#
# The constitutional determination of the located registration/classification
# authority (REG-AUTO-001 §21, closing CMG-OQ-06 for the concern delegated at
# CMG-DLG-13) is that admission of a constitutional zone/namespace requires NO
# amendment of a classification instrument: recognition is already total by
# construction (an existing CLASSIFY_RULE, then self-declared metadata, then the
# deterministic path-derived catch-all). What the authority requires instead is
# this append-only RECORD of the reconciled set, and its enforcement by the
# EXISTING classification gate.
#
# What this block is NOT:
#   * NOT a classification rule — classify() never reads it; no CLASSIFY_RULES,
#     CHAINS, PROGRAM_ROOTS, CROSS_PROGRAM or VOLUMES entry is added, edited or
#     renumbered, and no new classification family is created (L4/L5).
#   * NOT a registry — it stores no artifact, allocates no identity, and is
#     never emitted into DATA/ (the id-ledger remains the one identity
#     authority; P4).
#   * NOT a new gate/validator — it is read ONLY by the classification gate of
#     ENFORCEMENT_GATES (ukb.py::cmd_enforce), which it strengthens: a file
#     inside a reconciled zone must resolve to a classification the
#     determination ADMITS, not merely to "not OTHER/MISC".
#
# Record fields (append-only; a future reconciliation is a new entry, never a
# rewrite — CR-INF-007):
#   set              stable set id (also the reconciled namespace's zone key)
#   zone             repo-relative path regex the determination reconciled
#   namespace        the identifier namespace admitted with the zone
#   namespace_owner  the located owner of that namespace (by reference only)
#   concern          the delegated concern under which the determination issued
#   determination    the clause of this standard that issued it
#   closes           the open question the determination closes
#   recognition      the recognition paths the determination found sufficient
#   admitted         (program, category) pairs the determination admits
#   admitted_volumes volumes the determination admits (existing volumes only)
#
# Identity integrity (§21.4): `set`, `namespace` and `zone` are unique across the
# declaration; a duplicate is a fail-closed abort, so a reconciled set can never
# introduce duplicate identity.
# ===========================================================================
RECONCILED_SETS = (
    {
        "set": "CMG",
        "zone": r"^00-CMG/",
        "namespace": "CMG",
        "namespace_owner": "CMG-000001",
        "concern": "CMG-DLG-13",
        "determination": "REG-AUTO-001 §21",
        "closes": "CMG-OQ-06",
        "recognition": ("classify_rule", "declared_metadata", "path_derived"),
        "admitted": (("CONSOLIDATION", "CON"), ("CMG", "CMG")),
        "admitted_volumes": ("VOL-000", "VOL-002"),
    },
)
