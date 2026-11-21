#!/usr/bin/env python3
"""Author 00-MASTER/URKE-000001/urke-declaration.json — the data this capability is made of.

The declaration is the artifact of record; this script is how it is written, kept beside it so a
reader can see the shape being asserted instead of reverse-engineering it. Running it is idempotent.

The shape is the final convergence: **two structural primitives** (a subject and a relationship),
**seven lifecycle states**, and everything else data. Forty-one states and twenty-six unknown classes
were drafted for this capability and collapsed; every condition they named survives as a row in the
condition catalogue, expressed as one state plus axis values plus qualifiers plus a domain. Nothing
lost, nothing hardcoded — and both halves of that sentence are measured rather than asserted, by
URKE-L-30 (every catalogued condition is realised on every run) and URKE-L-32 (the primitive count
has not drifted upward while the data grew).
"""

from __future__ import annotations

import collections
import json
import pathlib

OD = collections.OrderedDict
HERE = pathlib.Path(__file__).resolve().parent
U = "unresolved"


def gap(gid: str, finding: str, referred: str, remediation: str) -> OD:
    return OD([("gap_id", gid), ("finding", finding), ("referred_to", referred),
               ("remediation", remediation)])


# ═════════════════════════════════════════════════════════ the whole of the type system: two things
PRIMITIVES = [
    ("SUBJECT",
     "An identified thing under governed lifecycle. A fact, a context, a contradiction, a gap, a "
     "research programme, a discovery, a reality, a temporal system, a declared law and a construct "
     "nobody has named are all one of these. What differs between them is data.",
     "engine/recursive_knowledge/model.py", "GovernedEntity"),
    ("RELATIONSHIP",
     "A governed link between two subjects, carrying its own basis and evidence. The second and last "
     "structural primitive, because it is the only thing whose subject is a pair. Every taxonomy "
     "that would otherwise have become a type hierarchy is expressed with these instead.",
     "engine/recursive_knowledge/ledger.py", "relate"),
]

# Expressive devices that are deliberately NOT primitives. Declared so the distinction is measurable:
# a device that quietly became a class would show up as a primitive-count refusal under URKE-L-32.
SUPPORTING = [
    ("ATTRIBUTE", "A named value on a subject. Where a taxonomy would otherwise grow.",
     "engine/recursive_knowledge/model.py", "ATTRIBUTE_READERS"),
    ("QUALIFIER", "A declared attribute vocabulary. Where a state would otherwise multiply.",
     "engine/recursive_knowledge/composition.py", "qualify"),
    ("CONTEXT", "A subject that situates other subjects. Not a special case: a subject with the "
                "context profile, which may contain and reference other contexts.",
     "engine/recursive_knowledge/composition.py", "situate"),
    ("EVIDENCE", "A recorded observation offered for or against a claim.",
     "engine/recursive_knowledge/model.py", "Evidence"),
    ("STATE", "Where a subject sits in the lattice, qualified by attributes.",
     "engine/recursive_knowledge/states.py", "transition"),
    ("GOVERNANCE", "The authority answerable for a subject, and the disposition it reached.",
     "engine/recursive_knowledge/bridge.py", "HANDLERS"),
    ("HISTORY", "The append-only record of what happened to a subject.",
     "engine/recursive_knowledge/ledger.py", "KnowledgeLedger"),
]

# ═══════════════════════════════════════════════════════════════════ seven states, and no more
LOCAL = ("No declared vocabulary owner carries a row for this lifecycle condition, so URKE holds it "
         "locally and discloses that it does.")
PROPOSE = "Propose a row with the named owner, or accept the local holding and its disclosure."

STATES = [
    ("UNKNOWN", "Unknown", "epistemic",
     "Identified and unresolved. Which flavour of not-knowing — residual, a stated question, "
     "unobserved, unmeasured, or inaccessible to every instrument — is the articulation and "
     "observability qualifiers, not five states.",
     {"owner": "UCOS-CEU-001", "population": "epistemic-state", "member": "unknown"}, None, "open"),
    ("RESEARCHING", "Researching", "lifecycle",
     "Under active investigation. Whether the activity is investigation, experiment, verification or "
     "validation is the activity qualifier.",
     None, ("URKE-G-01", "No owner carries a research-activity vocabulary. " + LOCAL,
            "UKDA-000001"), "in-progress"),
    ("BLOCKED", "Blocked", "governance",
     "Cannot advance until a named requirement is met. What is required — research, an instrument, "
     "an authority, knowledge, science, mathematics, discovery or a future capability — is the "
     "blocked-on qualifier. Eight conditions the directives named separately are one state and one "
     "qualifier.",
     None, ("URKE-G-02", "No owner carries a blocking-requirement vocabulary. " + LOCAL,
            "engine/governance"), "open"),
    ("KNOWN", "Known", "epistemic",
     "Held with a recorded basis. Whether it is verified, validated, certified or relied on is the "
     "independent axes, because those are orthogonal to being held. A gap whose closure criteria are "
     "satisfied rests here: what was missing is now known.",
     {"owner": "UCOS-CEU-001", "population": "knowledge-state", "member": "certainty"}, None,
     "supported"),
    ("CONTESTED", "Contested", "verification",
     "Incompatible positions are held at once. Whether the conflict is a refutation by evidence, an "
     "internal inconsistency, an evidence standoff or a dispute between authorities is the "
     "conflict-kind qualifier.",
     {"owner": "UCOS-CEU-001", "population": "epistemic-state", "member": "contradicted"}, None,
     "refuted"),
    ("UNDECIDABLE", "Undecidable", "epistemic",
     "No decision procedure available to this repository settles it. Recorded, never dropped.",
     None, ("URKE-G-03", "UCON-000001 discloses the same absence for its own undecidable state; "
            "URKE inherits the gap rather than inventing a binding. " + LOCAL, "UCOS-CEU-001"),
     "undecidable"),
    ("SUPERSEDED", "Superseded", "governance",
     "Replaced by a named later subject and retained in full. Whether it is superseded, deprecated "
     "or retired is the withdrawal qualifier.",
     {"owner": "UKDA-000001", "population": "lifecycle", "member": "superseded"}, None,
     "superseded"),
]

AXES = [
    ("existence", "Whether the thing is held to be, independent of whether we wrote it down.",
     "unresolved", ["unresolved", "claimed", "observed"]),
    ("representation", "Whether the repository can express it. Representation precedes understanding.",
     "represented", ["absent", "represented"]),
    ("admission", "Whether the construct foundation has dispositioned it.",
     "not-presented", ["not-presented", "presented", "disposed"]),
    ("verification", "What measurement says.",
     "unverified", ["unverified", "under-verification", "partially-verified", "verified", "refuted"]),
    ("validation", "Whether it is fit for the purpose offered.",
     "unvalidated", ["unvalidated", "under-validation", "validated", "invalidated"]),
    ("certification", "Whether an authority attested to it.",
     "uncertified", ["uncertified", "certified", "revoked"]),
    ("acceptance", "Whether the repository relies on it.",
     "unaccepted", ["unaccepted", "accepted", "declined-for-use"]),
]

QUALIFIERS = [
    ("knowledge_status",
     "How well the subject is known. With the domain attribute this replaces an entire family of "
     "unknown classes: unknown physics is two data values, not a type.",
     "unstated", ["unstated", "known", "partially-known", "unknown", "undecidable", "contested"]),
    ("articulation",
     "How precisely the not-knowing can be stated. Replaces UNKNOWN / KNOWN_UNKNOWN / "
     "UNKNOWN_UNKNOWN as three states.",
     "unstated", ["unstated", "residual", "stated-question", "stated-claim"]),
    ("observability",
     "Why the subject has not been observed. Replaces UNOBSERVED / UNMEASURED / NOT_YET_MEASURABLE / "
     "UNOBSERVABLE / NOT_YET_DISCOVERED as five states.",
     "unstated",
     ["unstated", "observed", "not-yet-observed", "not-yet-measured", "not-yet-discovered",
      "no-instrument-exists", "inaccessible-from-every-frame"]),
    ("blocked_on",
     "What a blocked subject waits for. Replaces RESEARCH_REQUIRED / DISCOVERY_REQUIRED / "
     "INSTRUMENT_REQUIRED / AUTHORITY_REQUIRED / KNOWLEDGE_NOT_YET_AVAILABLE / "
     "SCIENCE_NOT_YET_AVAILABLE / MATHEMATICS_NOT_YET_AVAILABLE / FUTURE_DEPENDENT as eight states.",
     "nothing",
     ["nothing", "research", "discovery", "instrument", "authority", "knowledge", "science",
      "mathematics", "future-capability"]),
    ("conflict_kind",
     "What incompatibility stands. Replaces CONTRADICTED / CONTRADICTORY / CONTESTED / DISPUTED as "
     "four states.",
     "none",
     ["none", "refuted-by-evidence", "internally-inconsistent", "evidence-standoff",
      "authority-dispute"]),
    ("withdrawal", "How something left use. Replaces SUPERSEDED / DEPRECATED / RETIRED as three "
                   "states.",
     "none", ["none", "superseded", "deprecated", "retired"]),
    ("activity", "What is being done. Replaces RESEARCHING / EXPERIMENTING / UNDER_VERIFICATION / "
                 "UNDER_VALIDATION as four states.",
     "none", ["none", "investigating", "experimenting", "verifying", "validating"]),
    ("record_stage", "How far the subject travelled through recording. Replaces PRESENTED / RECORDED "
                     "as states; both are events in a pipeline, not places a subject rests.",
     "unstated", ["unstated", "presented", "recorded"]),
    ("confidence", "How well supported the claim is held to be, stated rather than implied.",
     "unassessed", ["unassessed", "low", "moderate", "high", "contested"]),
    ("epistemic_form",
     "What kind of claim it is. Replaces a type per knowledge-object kind and a type per "
     "discovery-object kind — thirty-two drafted classes — with one open qualifier.",
     "unclassified",
     ["unclassified", "fact", "hypothesis", "theory", "model", "observation", "assumption",
      "question", "rule", "law", "authority", "capability", "evidence", "confidence-assessment",
      "limitation", "future-concept", "ontology", "taxonomy", "vocabulary", "programme",
      "experiment", "discovery-event", "discovery-finding", "discovery-outcome", "discovery-failure",
      "discovery-revision", "discovery-path", "temporal-system", "location-system",
      "measurement-system", "identity-system", "reality-model", "governance-rule",
      "verification-rule", "validation-rule"]),
]

DOMAINS = [
    ("mathematics", "Structures, proofs, decidability and formal systems."),
    ("physics", "Matter, energy, spacetime and their laws."),
    ("biology", "Living systems and their mechanisms."),
    ("chemistry", "Substances, reactions and their regimes."),
    ("computation", "Models of computation and their limits."),
    ("intelligence", "Cognition, reasoning and learning."),
    ("ontology", "What kinds of thing there are."),
    ("taxonomy", "How kinds are classified."),
    ("governance", "Who decides what, and to whom they answer."),
    ("verification", "How a claim is checked."),
    ("validation", "Whether something is fit for a purpose."),
    ("economics", "Value, exchange and allocation."),
    ("security", "Threat, adversary and protection."),
    ("temporal", "Time, chronology, ordering and causality."),
    ("location", "Position, frame and place."),
    ("measurement", "Units, instruments and traceability."),
    ("identity", "Naming, minting and re-finding."),
    ("reality", "Modes and structures of reality."),
    ("universe", "Containers of realities."),
    ("civilization", "Populations, their institutions and conventions."),
    ("dimension", "Axes of variation."),
    ("substrate", "What a system runs on."),
    ("language", "Notation, encoding and interpretation."),
    ("construct", "The repository's own constructs."),
    ("discovery", "How the unknown is found."),
    ("research", "How the unknown is investigated."),
    ("knowledge", "Knowledge itself, including knowledge about knowledge."),
    ("learning", "How the repository comes to hold something."),
    ("evolution", "How anything governed changes."),
    ("future-domain", "A field of inquiry that does not exist yet, admitted so its arrival is a data "
                      "row rather than a redesign."),
    ("unclassified-domain", "The residual: a domain not yet determined. Never an error."),
]

RELATIONS = [
    ("derived-from", "The source was produced from the target.", "produced"),
    ("supersedes", "The source replaces the target, which is retained.", "superseded-by"),
    ("contradicts", "The source and target cannot both hold.", "contradicts"),
    ("affects", "A change to the target changes the source's standing.", "affected-by"),
    ("generated-by", "The target caused the source to be admitted.", "generated"),
    ("depends-on", "The source cannot resolve until the target does.", "depended-on-by"),
    ("reflects-on", "The source is knowledge about the target. This one relation is the whole of the "
                    "reflexive meta-knowledge mechanism: no second layer.", "reflected-on-by"),
    ("classified-as", "The source is an instance of the target vocabulary member.", "classifies"),
    ("contained-by", "The source sits inside the target context. Contexts contain contexts through "
                     "this relation rather than through a nesting field.", "contains"),
    ("located-in", "The source holds within the target reality.", "locates"),
    ("timed-in", "The source is referenced against the target temporal system.", "times"),
    ("evidenced-by", "The target is offered in support of the source.", "evidence-for"),
    ("blocked-by", "The source cannot advance until the target is met.", "blocks"),
    ("resolves", "The source settles the target.", "resolved-by"),
    ("governs", "The source holds decision rights over the target.", "governed-by"),
    ("verifies", "The source is a measurement of the target.", "verified-by"),
    ("validates", "The source judges the target fit for a purpose.", "validated-by"),
    ("reviews", "The source is a review of the target.", "reviewed-by"),
    ("unclassified-relation", "The residual: a link whose relation is not yet determined.",
     "unclassified-relation"),
]

UNIVERSAL_ATTRS = ["identity", "entity_class", "natural_key", "title", "classification", "context",
                   "state", "state_history", "owner", "origin", "governance", "axes",
                   "evolution_metadata", "payload"]
ENTITY_CLASSES = [
    ("subject", "Subject",
     "The universal governed object. Everything is one of these except a link between two of them.",
     "concept", "none", "present_plain", UNIVERSAL_ATTRS),
    ("relationship", "Relationship",
     "The only irreducible second class: its subject is a pair, which no attribute set on a single "
     "subject can express without inventing one.",
     "relationship", "none", "present_plain",
     UNIVERSAL_ATTRS + ["source", "target", "relation", "basis", "evidence"]),
]

PROFILES = [
    ("subject", [], [], "The default: no requirement beyond the universal set."),
    ("context", ["payload"], ["context_kind"],
     "A subject that situates other subjects. Location, time, reality, universe, civilization, "
     "organisation, execution environment and knowledge domain are all contexts, and none is a "
     "primitive. Containment and reference are relations."),
    ("contradiction",
     ["lineage", "evidence", "competing_positions", "candidate_resolutions", "affected",
      "affected_entities", "resolution_status", "resolution_history", "verification_history"], [],
     "Competing claims that cannot all hold, with everything they affect and every attempt to "
     "resolve them retained."),
    ("gap", ["severity", "evidence", "resolution_path", "review_schedule", "closure_criteria"], [],
     "An assumption, limitation, unknown, open question, unresolved finding, missing evidence, "
     "missing knowledge, verification deficiency, coverage deficiency or future risk."),
    ("research", ["evidence", "lineage"],
     ["questions", "hypotheses", "experiments", "dependencies", "limitations", "blockers",
      "outcomes", "confidence", "history"],
     "An investigation of something unresolved. Recursive: research may generate further research, "
     "discovery, verification work or governance review, each as a related subject."),
    ("discovery", ["evidence", "lineage"], [],
     "Something a detector identified. Questions, hypotheses, observations, experiments, evidence, "
     "gaps, findings, failures, revisions and outcomes are this profile with a different epistemic "
     "form."),
    ("learning", ["evidence", "lineage"], ["stage"],
     "A candidate lesson travelling the governed pipeline. Its stage is data."),
    ("evolution", ["evidence", "lineage"], ["subject", "operator", "before", "after"],
     "One governed change to a declared subject, carrying the digest before and after."),
    ("vocabulary", ["payload"], ["definition"],
     "A declared vocabulary member, itself governed, so extending a vocabulary is a recorded act."),
    ("observation", ["evidence"], [], "Something seen, with its observer named."),
    ("claim", ["evidence"], [], "Something asserted, with what is offered for it."),
    ("architecture-proposal",
     ["evidence", "lineage", "resolution_path"],
     ["construct", "unrepresentable_because", "capability_gained", "complexity_added",
      "tradeoff_justification", "impact", "verification", "validation", "governance_decision"],
     "A proposal to change the constitutional foundation itself. Architecture is a governed subject: "
     "it may evolve, and it may not evolve silently. The burden of proof sits on the change, which "
     "is why every payload key above is required and a proposal missing one is refused rather than "
     "recorded as provisional."),
]


def cond(name, directive, state, qualifiers=None, axes=None, domain=None):
    row = OD([("condition", name), ("named_by", directive), ("state", state)])
    row["domain"] = domain or "unclassified-domain"
    row["qualifiers"] = OD(sorted((qualifiers or {}).items()))
    row["axes"] = OD(sorted((axes or {}).items()))
    return row


D0 = "URKE-000001"
S2, S3, S4, S5 = "steer-d21fbae7", "steer-1c35f27e", "steer-b36fdbd4", "steer-2be28076"
CONDITIONS = [
    cond("KNOWN", D0, "KNOWN", {"knowledge_status": "known"}),
    cond("VERIFIED", D0, "KNOWN", {}, {"verification": "verified"}),
    cond("PARTIALLY_VERIFIED", D0, "KNOWN", {}, {"verification": "partially-verified"}),
    cond("HYPOTHESIZED", D0, "UNKNOWN",
         {"epistemic_form": "hypothesis", "articulation": "stated-claim"}),
    cond("OBSERVED", D0, "KNOWN", {"observability": "observed", "epistemic_form": "observation"},
         {"existence": "observed"}),
    cond("UNOBSERVED", D0, "UNKNOWN", {"observability": "not-yet-observed"}),
    cond("UNKNOWN", D0, "UNKNOWN", {"knowledge_status": "unknown"}),
    cond("KNOWN_UNKNOWN", D0, "UNKNOWN", {"articulation": "stated-question"}),
    cond("UNKNOWN_UNKNOWN", D0, "UNKNOWN", {"articulation": "residual"}),
    cond("UNDECIDABLE", D0, "UNDECIDABLE", {"knowledge_status": "undecidable"}),
    cond("UNOBSERVABLE", D0, "UNKNOWN", {"observability": "inaccessible-from-every-frame"}),
    cond("NOT_YET_MEASURABLE", D0, "UNKNOWN", {"observability": "no-instrument-exists"}),
    cond("CONTRADICTED", D0, "CONTESTED", {"conflict_kind": "refuted-by-evidence"},
         {"verification": "refuted"}),
    cond("CONTESTED", D0, "CONTESTED", {"conflict_kind": "evidence-standoff"}),
    cond("ESCALATED", D0, "BLOCKED",
         {"blocked_on": "authority", "record_stage": "recorded"}),
    cond("RESEARCHING", D0, "RESEARCHING", {"activity": "investigating"}),
    cond("EXPERIMENTING", D0, "RESEARCHING", {"activity": "experimenting"}),
    cond("DEFERRED", D0, "BLOCKED", {"blocked_on": "nothing"}),
    cond("SUPERSEDED", D0, "SUPERSEDED", {"withdrawal": "superseded"}),
    cond("OPEN", D0, "UNKNOWN", {}),
    cond("CLOSED", D0, "KNOWN", {"knowledge_status": "known", "articulation": "stated-claim"}),
    *[cond(f"UNKNOWN_{d.upper().replace('-', '_')}", D0, "UNKNOWN",
           {"knowledge_status": "unknown"}, None, d)
      for d in ("mathematics", "physics", "ontology", "intelligence", "governance", "economics",
                "security", "temporal", "reality", "dimension", "substrate", "computation",
                "language", "construct", "discovery")],
    cond("UNMEASURED", S3, "UNKNOWN", {"observability": "not-yet-measured"}),
    cond("UNVERIFIED", S3, "UNKNOWN", {"articulation": "stated-claim"},
         {"verification": "unverified"}),
    cond("UNVALIDATED", S3, "UNKNOWN", {"articulation": "stated-claim"},
         {"validation": "unvalidated", "verification": "verified"}),
    cond("CONTRADICTORY", S3, "CONTESTED", {"conflict_kind": "internally-inconsistent"}),
    cond("FUTURE_DEPENDENT", S3, "BLOCKED", {"blocked_on": "future-capability"}),
    cond("RESEARCH_REQUIRED", S3, "BLOCKED", {"blocked_on": "research"}),
    cond("DISCOVERY_REQUIRED", S4, "BLOCKED", {"blocked_on": "discovery"}),
    cond("INSTRUMENT_REQUIRED", S3, "BLOCKED", {"blocked_on": "instrument"}),
    cond("AUTHORITY_REQUIRED", S3, "BLOCKED",
         {"blocked_on": "authority", "record_stage": "unstated"}),
    cond("KNOWLEDGE_NOT_YET_AVAILABLE", S3, "BLOCKED", {"blocked_on": "knowledge"}),
    cond("SCIENCE_NOT_YET_AVAILABLE", S3, "BLOCKED", {"blocked_on": "science"}),
    cond("MATHEMATICS_NOT_YET_AVAILABLE", S3, "BLOCKED", {"blocked_on": "mathematics"}),
    cond("NOT_YET_DISCOVERED", S5, "UNKNOWN", {"observability": "not-yet-discovered"}),
    cond("NOT_YET_VERIFIABLE", S5, "BLOCKED",
         {"blocked_on": "instrument", "observability": "no-instrument-exists"},
         {"verification": "unverified"}),
    cond("NOT_YET_VALIDATABLE", S5, "BLOCKED",
         {"blocked_on": "authority", "articulation": "stated-claim"},
         {"validation": "unvalidated"}),
    *[cond(f"Unknown{d.title().replace('-', '')}", S3, "UNKNOWN", {"knowledge_status": "unknown"},
           None, d)
      for d in ("biology", "chemistry", "civilization", "universe", "verification", "measurement",
                "location", "identity", "knowledge")],
    cond("Presented", S3, "UNKNOWN", {"record_stage": "presented"}, {"admission": "presented"}),
    cond("Recorded", S3, "UNKNOWN", {"record_stage": "recorded"}),
    cond("UnderVerification", S3, "RESEARCHING", {"activity": "verifying"},
         {"verification": "under-verification"}),
    cond("UnderValidation", S3, "RESEARCHING", {"activity": "validating"},
         {"validation": "under-validation"}),
    cond("Validated", S3, "KNOWN", {}, {"validation": "validated"}),
    cond("Certified", S3, "KNOWN", {}, {"certification": "certified"}),
    cond("Disputed", S3, "CONTESTED", {"conflict_kind": "authority-dispute"}),
    cond("Deprecated", S3, "SUPERSEDED", {"withdrawal": "deprecated"}),
    cond("Retired", S3, "SUPERSEDED", {"withdrawal": "retired"}),
    *[cond(k, S4, "UNKNOWN", {"epistemic_form": f}, None, "discovery")
      for k, f in (("DiscoveryEvent", "discovery-event"), ("DiscoveryFinding", "discovery-finding"),
                   ("DiscoveryOutcome", "discovery-outcome"),
                   ("DiscoveryFailure", "discovery-failure"),
                   ("DiscoveryRevision", "discovery-revision"), ("DiscoveryPath", "discovery-path"),
                   ("DiscoveryEvidence", "evidence"), ("DiscoveryObservation", "observation"),
                   ("DiscoveryHypothesis", "hypothesis"), ("DiscoveryQuestion", "question"),
                   ("DiscoveryExperiment", "experiment"))],
    cond("DiscoveryGap", S4, "UNKNOWN",
         {"knowledge_status": "unknown", "articulation": "stated-question"}, None, "discovery"),
    *[cond(k, S3, "KNOWN", {"epistemic_form": "fact"}, None, d)
      for k, d in (("KnowledgeAboutKnowledge", "knowledge"),
                   ("VerificationAboutVerification", "verification"),
                   ("GovernanceAboutGovernance", "governance"),
                   ("ResearchAboutResearch", "research"),
                   ("DiscoveryAboutDiscovery", "discovery"),
                   ("LearningAboutLearning", "learning"),
                   ("EvolutionAboutEvolution", "evolution"))],

]

TARGETS = [
    ("concept", "A concept in use and not defined."),
    ("ontology", "A link structure declared and ungoverned, or used and undeclared."),
    ("taxonomy", "A classification that classifies nothing."),
    ("governance-structure", "A subject whose governing authority is not resolvable."),
    ("scientific-domain", "A domain named and unpopulated."),
    ("intelligence-form", "An intelligence-domain subject with nothing verified about it."),
    ("contradiction", "A contradiction with no resolution path."),
    ("gap", "A gap unowned, uncriteria'd, unresearched or overdue."),
    ("opportunity", "A research subject that could advance and has not."),
    ("limitation", "A declared bound that nothing tracks."),
    ("composition", "A subject with no context, or a context nothing sits in."),
    ("unexplored-space", "A declared dimension, system or residual with nothing recorded."),
]
SOURCES = [
    ("URKE-DS-01", "unknown_without_research", "gap", "P1", "architectural",
     "A gap in an unresolved state with no research subject derived from it."),
    ("URKE-DS-02", "contradiction_without_resolution_path", "contradiction", "P0", "constitutional",
     "A standing contradiction whose resolution history is empty."),
    ("URKE-DS-03", "subject_without_owner", "governance-structure", "P0", "architectural",
     "A subject resting on the declared unassigned owner token."),
    ("URKE-DS-04", "gap_overdue_for_review", "gap", "P2", "operational",
     "An unsettled gap whose review point the ledger has advanced past."),
    ("URKE-DS-05", "state_without_successor", "limitation", "P0", "constitutional",
     "A declared state from which nothing is reachable."),
    ("URKE-DS-06", "vocabulary_binding_gap", "unexplored-space", "P2", "architectural",
     "A declared state binding to no owner, holding a vocabulary locally."),
    ("URKE-DS-07", "subject_without_governance", "governance-structure", "P0", "constitutional",
     "A subject whose governing authority is empty or unresolvable."),
    ("URKE-DS-08", "research_without_evidence", "opportunity", "P2", "operational",
     "A research subject under investigation with no evidence recorded."),
    ("URKE-DS-09", "reality_dimension_unresolved", "unexplored-space", "P2", "architectural",
     "A reality leaving a declared dimension unresolved."),
    ("URKE-DS-10", "temporal_epoch_unresolved", "unexplored-space", "P2", "architectural",
     "A temporal system whose epoch is unresolved."),
    ("URKE-DS-11", "domain_without_subject", "scientific-domain", "P1", "architectural",
     "A declared domain with nothing classified under it — a field named and unrecorded."),
    ("URKE-DS-12", "qualifier_value_unused", "taxonomy", "P3", "local",
     "A declared qualifier value nothing uses: a classification that classifies nothing."),
    ("URKE-DS-13", "subject_without_verification", "intelligence-form", "P1", "architectural",
     "An intelligence-domain subject with no verification recorded against it."),
    ("URKE-DS-14", "subject_without_definition", "concept", "P3", "local",
     "A vocabulary subject whose payload carries no definition."),
    ("URKE-DS-15", "relation_without_basis", "ontology", "P1", "architectural",
     "A relationship carrying no basis: a link nobody has to account for."),
    ("URKE-DS-16", "subject_without_context", "composition", "P0", "constitutional",
     "A subject sitting in no context. Every subject exists within one."),
    ("URKE-DS-17", "residual_population", "unexplored-space", "P1", "architectural",
     "Everything resting in a residual domain, form or relation — the honest measure of what the "
     "taxonomy has not resolved, and the nearest proxy for what no detector can see."),
]

OPERATORS = [
    ("extend", "Add a member to a declared vocabulary. Narrowing is not expressible here."),
    ("refine", "Change a definition or a binding without removing a member."),
    ("supersede", "Replace a member with a named later member, retaining the earlier one."),
    ("bind", "Attach a locally held vocabulary to the authority that owns it."),
]
EVO_SUBJECTS = [
    ("ontology", ["extend", "refine", "supersede", "bind"]),
    ("taxonomy", ["extend", "refine", "supersede"]),
    ("vocabulary", ["extend", "refine", "supersede", "bind"]),
    ("governance", ["extend", "refine", "supersede", "bind"]),
    ("verification", ["extend", "refine", "supersede"]),
    ("validation", ["extend", "refine", "supersede"]),
    ("authority", ["extend", "refine", "supersede"]),
    ("research", ["extend", "refine"]),
    ("discovery", ["extend", "refine"]),
    ("learning", ["extend", "refine"]),
    ("knowledge", ["extend", "refine", "supersede"]),
    ("identity", ["extend", "bind"]),
    ("context", ["extend", "refine", "bind"]),
    ("location", ["extend", "refine", "bind"]),
    ("temporal-system", ["extend", "refine", "bind"]),
    ("unit-system", ["extend", "refine", "bind"]),
    ("economic-system", ["extend", "refine"]),
    ("security-system", ["extend", "refine"]),
    ("reality-model", ["extend", "refine", "bind"]),
    ("intelligence-model", ["extend", "refine", "supersede"]),
]

EXTENSION_POINTS = [
    ("URKE-EP-01", "lifecycle state", "admit_state", "knowledge"),
    ("URKE-EP-02", "domain", "admit_domain", "taxonomy"),
    ("URKE-EP-03", "qualifier value", "admit_qualifier_value", "vocabulary"),
    ("URKE-EP-04", "relation", "admit_relation", "ontology"),
    ("URKE-EP-05", "profile", "admit_profile", "ontology"),
    ("URKE-EP-06", "discovery source", "admit_discovery_source", "discovery"),
    ("URKE-EP-07", "evolution subject", "admit_evolution_subject", "governance"),
    ("URKE-EP-08", "reality", "admit_reality", "reality-model"),
    ("URKE-EP-09", "temporal system", "admit_temporal_system", "temporal-system"),
    ("URKE-EP-10", "lifecycle axis", "admit_axis", "verification"),
    ("URKE-EP-11", "gap class", "admit_gap_class", "research"),
    ("URKE-EP-12", "learning stage", "admit_learning_stage", "learning"),
    ("URKE-EP-13", "composition", "admit_context", "context"),
    ("URKE-EP-14", "architectural change", "admit_architecture_proposal", "ontology"),
]
FUTURE_DOMAIN_SUBJECTS = [
    ("scientific-domain", "admit_domain"), ("mathematical-domain", "admit_domain"),
    ("intelligence-model", "admit_domain"), ("ontology", "admit_relation"),
    ("governance-model", "admit_evolution_subject"), ("verification-model", "admit_axis"),
    ("reality-model", "admit_reality"), ("temporal-system", "admit_temporal_system"),
    ("location-system", "admit_context"), ("civilization", "admit_context"),
    ("substrate", "admit_context"), ("future-construct", "admit_profile"),
]
SELF_EVOLUTION = [
    ("knowledge", "admit_state"), ("ontology", "admit_relation"), ("taxonomy", "admit_domain"),
    ("governance", "admit_evolution_subject"), ("verification", "admit_axis"),
    ("research", "admit_gap_class"), ("discovery", "admit_discovery_source"),
    ("context", "admit_context"), ("learning", "admit_learning_stage"),
    ("vocabulary", "admit_qualifier_value"),
]

SELF_IMPROVEMENT = [
    ("self-observation", "ledger", "summary", "reports its own population, states and histories"),
    ("self-analysis", "discovery", "discover", "runs its declared detectors over its own ledger"),
    ("self-validation", "declaration", "parse", "refuses its own declaration when incoherent"),
    ("self-verification", "contract", "measure", "measures its own laws and names every refusal"),
    ("self-learning", "subjects", "advance", "moves a candidate lesson through the pipeline"),
    ("self-correction", "subjects", "close_gap", "closes its own gaps only against satisfied criteria"),
    ("self-healing", "ledger", "supersede", "replaces a damaged record without removing it"),
    ("self-adaptation", "admission", "ADMISSIONS", "admits vocabulary it was not built with"),
    ("self-evolution", "evolution", "evolve", "records changes to its own declared subjects"),
    ("self-governance", "bridge", "govern", "presents its own subjects rather than dispositioning"),
    ("self-auditing", "ledger", "chain_is_intact", "verifies its own journal for tampering"),
    ("self-research", "research", "open_research", "opens research on its own unresolved subjects"),
    ("self-discovery", "discovery", "REALITY_PROBES", "compares its declaration against the world"),
]

SUBSTRATE = [
    ("URKE-S-01", "append-only chained ledger with no removal path", "ledger", "KnowledgeLedger"),
    ("URKE-S-02", "open state lattice with no terminal member", "states", "transition"),
    ("URKE-S-03", "governed admission for every declared data vocabulary", "admission", "ADMISSIONS"),
    ("URKE-S-04", "continuous discovery converging to a fixed point", "discovery", "DETECTORS"),
    ("URKE-S-05", "governed evolution carrying before and after digests", "evolution", "OPERATORS"),
    ("URKE-S-06", "profile-driven requirement enforcement at admission", "model",
     "missing_attributes"),
    ("URKE-S-07", "disposition binding to the construct foundation", "bridge", "HANDLERS"),
    ("URKE-S-08", "independent lifecycle axes", "states", "axis_initial"),
    ("URKE-S-09", "data-driven reality registry", "worlds", "resolve"),
    ("URKE-S-10", "data-driven temporal registry", "worlds", "resolve"),
    ("URKE-S-11", "declaration-versus-measured-reality probes", "discovery", "REALITY_PROBES"),
    ("URKE-S-12", "tamper-evident journal verification", "ledger", "chain_is_intact"),
    ("URKE-S-13", "governed contradictions with resolution and verification history",
     "subjects", "record_contradiction"),
    ("URKE-S-14", "governed gap lifecycle with closure criteria and review", "subjects", "close_gap"),
    ("URKE-S-15", "research lifecycle derivable from any unresolved subject", "research",
     "open_research"),
    ("URKE-S-16", "governed relationships carrying basis and evidence", "ledger", "relate"),
    ("URKE-S-17", "composition of state, axes and qualifiers in place of new types", "composition",
     "express"),
    ("URKE-S-18", "context as a subject, containing and referencing contexts", "composition", "situate"),
    ("URKE-S-19", "governed learning pipeline with no bypass", "subjects", "advance"),
    ("URKE-S-20", "representability measurement before any architectural change", "proposal",
     "representability"),
    ("URKE-S-21", "governed architectural change proposal with impact analysis", "proposal",
     "propose"),
]
FUTURE_CAPABILITIES = [
    ("recursive-self-learning", ["URKE-S-01", "URKE-S-02", "URKE-S-19", "URKE-S-15"]),
    ("recursive-self-validation", ["URKE-S-01", "URKE-S-06", "URKE-S-08"]),
    ("recursive-self-verification", ["URKE-S-01", "URKE-S-08", "URKE-S-13"]),
    ("recursive-self-governance", ["URKE-S-03", "URKE-S-07", "URKE-S-06"]),
    ("recursive-self-correction", ["URKE-S-05", "URKE-S-13", "URKE-S-14"]),
    ("recursive-self-healing", ["URKE-S-05", "URKE-S-12", "URKE-S-14"]),
    ("recursive-self-defense", ["URKE-S-11", "URKE-S-12", "URKE-S-13"]),
    ("recursive-anti-tampering", ["URKE-S-01", "URKE-S-12"]),
    ("recursive-anti-theft", ["URKE-S-01", "URKE-S-12", "URKE-S-07"]),
    ("recursive-anti-corruption", ["URKE-S-11", "URKE-S-12", "URKE-S-06"]),
    ("recursive-research-generation", ["URKE-S-04", "URKE-S-15", "URKE-S-02"]),
    ("recursive-discovery-generation", ["URKE-S-04", "URKE-S-01"]),
    ("recursive-capability-evolution", ["URKE-S-03", "URKE-S-05"]),
    ("recursive-ontology-evolution", ["URKE-S-03", "URKE-S-05", "URKE-S-16"]),
    ("recursive-taxonomy-evolution", ["URKE-S-03", "URKE-S-05", "URKE-S-17"]),
    ("recursive-verification-evolution", ["URKE-S-05", "URKE-S-08", "URKE-S-13"]),
    ("recursive-governance-evolution", ["URKE-S-03", "URKE-S-05", "URKE-S-07"]),
    ("recursive-intelligence-evolution", ["URKE-S-03", "URKE-S-05", "URKE-S-15"]),
    ("recursive-temporal-evolution", ["URKE-S-10", "URKE-S-03", "URKE-S-05"]),
    ("recursive-location-evolution", ["URKE-S-09", "URKE-S-18", "URKE-S-03"]),
    ("governed-architectural-evolution", ["URKE-S-20", "URKE-S-21", "URKE-S-05"]),
]

GAP_CLASSES = [
    ("assumption", "Taken as true without measurement.", "unknown-knowledge-form"),
    ("limitation", "Something the repository cannot do, stated as a bound.", "unknown-knowledge-form"),
    ("unknown", "Something not known, recorded as an object.", "unknown-unclassified"),
    ("open-question", "A question stated precisely and unanswered.", "unknown-unclassified"),
    ("unresolved-finding", "A finding not carried to closure.", "unknown-knowledge-form"),
    ("missing-evidence", "A claim held with less evidence than its state requires.",
     "unknown-knowledge-form"),
    ("missing-knowledge", "Knowledge needed and not held.", "unknown-knowledge-form"),
    ("verification-deficiency", "A verification absent, stale or itself unverified.",
     "unknown-knowledge-form"),
    ("coverage-deficiency", "A declared surface measurement does not reach.",
     "unknown-knowledge-form"),
    ("future-risk", "A risk not present now and foreseeable.", "unknown-future-domain"),
    ("unclassified-gap", "The residual: a gap whose class is not determined.",
     "unknown-unclassified"),
]

REALITY_DIMENSIONS = [
    ("location-system", "How a position is named."),
    ("coordinate-system", "The frame positions are expressed in."),
    ("unit-system", "The units quantities are expressed in."),
    ("temporal-system", "The time reference system in force."),
    ("calendar-system", "How dates are named."),
    ("communication-model", "The latency and reachability regime."),
    ("governance-model", "Who governs here."),
    ("economic-model", "How value is exchanged here."),
    ("measurement-model", "What can be measured here and how."),
]
REALITIES = [
    ("earth", "Earth", False, "planetary", None,
     ["geodetic-place", "planetary-datum", "si", "utc", "civil-calendar",
      "terrestrial-low-latency", "multi-jurisdictional", "fiat-multi-currency", "si-traceable"]),
    ("moon", "Moon", False, "planetary", None,
     ["selenographic-place", "mean-earth-axis", "si", "lunar-coordinated-time", "mission-calendar",
      "cislunar-delayed", "treaty-derived", U, "si-traceable"]),
    ("mars", "Mars", False, "planetary", None,
     ["areographic-place", "areocentric-datum", "si", "mars-coordinated-time", "sol-calendar",
      "interplanetary-high-delay", U, U, "si-traceable"]),
    ("orbital-habitat", "Orbital Habitat", False, "orbital", None,
     ["orbital-element-set", "station-body-fixed", "si", "mission-elapsed-time", "mission-calendar",
      "orbital-intermittent", "operator-derived", U, "si-traceable"]),
    ("interplanetary-system", "Interplanetary System", False, "interstellar",
     gap("URKE-G-04",
         "The reference frame catalogue declares an interstellar frame kind for corridors between "
         "bodies and no distinct interplanetary kind, so this reality binds to the nearest declared "
         "kind.", "UCXI-000001",
         "Declare an interplanetary frame kind, or record that interstellar covers both scales."),
     ["barycentric-place", "inertial-celestial", "si", "tt", "civil-calendar",
      "interplanetary-high-delay", U, U, "si-traceable"]),
    ("future-settlement", "Future Settlement", False, "planetary", None,
     [U, U, "si", U, U, U, U, U, U]),
    ("digital-reality", "Digital Reality", False, "virtual", None,
     ["addressable-namespace", "graph-position", "dimensionless-count", "logical-sequence",
      "sequence-only", "in-substrate", "operator-derived", U, "instrumented-counter"]),
    ("simulated-reality", "Simulated Reality", False, "simulated", None,
     ["simulation-place", "simulation-grid", "simulation-unit", "simulated-timeline",
      "sequence-only", "in-simulation", "operator-derived", "simulation-scrip",
      "simulation-instrument"]),
    ("distributed-substrate", "Distributed Substrate", False, "distributed", None,
     ["mesh-node-set", "graph-position", "dimensionless-count", "logical-sequence", "sequence-only",
      "partition-tolerant", U, U, "instrumented-counter"]),
    ("unknown-future-reality", "Unknown Future Reality", True, "",
     gap("URKE-G-05",
         "The residual reality binds to no frame kind by construction: a residual that named one "
         "would be a prediction about a reality nobody has met.", "URKE-000001",
         "None. The gap is the correct state and it is disclosed rather than defaulted."),
     [U] * 9),
]

TEMPORAL = [
    ("utc", "Coordinated Universal Time", "physical", "historical", "leap-second-aligned",
     "civil-calendar", "single-total-order", "earth", "BIPM", None),
    ("tai", "International Atomic Time", "physical", "historical", "atomic-continuous",
     "civil-calendar", "single-total-order", "earth", "BIPM", None),
    ("tt", "Terrestrial Time", "physical", "historical", "ephemeris-aligned", "civil-calendar",
     "single-total-order", "interplanetary-system", "IAU", None),
    ("lunar-coordinated-time", "Lunar Coordinated Time", "physical", "historical", U,
     "mission-calendar", "single-total-order", "moon", U, None),
    ("mars-coordinated-time", "Mars Coordinated Time", "physical", "historical", U, "sol-calendar",
     "single-total-order", "mars", U, None),
    ("mission-elapsed-time", "Mission Elapsed Time", "contextual", "historical", "mission-declared",
     "mission-calendar", "single-total-order", "orbital-habitat", "mission-operator", None),
    ("logical-sequence", "Logical Sequence", "logical", "historical", "sequence-zero",
     "sequence-only", "partial-order", "digital-reality", "URKE-000001", None),
    ("simulated-timeline", "Simulated Timeline", "simulated", "simulated", "simulation-declared",
     "sequence-only", "single-total-order", "simulated-reality", "simulation-operator", None),
    ("branching-chronology", "Branching Chronology", "logical", "branching", "branch-declared",
     "sequence-only", "branching-causality", U, U, None),
    ("recursive-chronology", "Recursive Chronology", "logical", "recursive", U, "sequence-only",
     "recursive-causality", U, U, None),
    ("predictive-chronology", "Predictive Chronology", "logical", "predicted", U, "sequence-only",
     "single-total-order", U, U, None),
    ("alternative-chronology", "Alternative Chronology", "logical", "alternative", U,
     "sequence-only", "branching-causality", U, U, None),
    ("unknown-future-temporal-system", "Unknown Future Temporal System", "unknown", "unknown", U, U,
     U, U, U,
     gap("URKE-G-06",
         "The residual temporal system declares no epoch by construction. A residual with an epoch "
         "would be an assumption about a chronology nobody has met.", "URKE-000001",
         "None. The unresolved epoch is the correct value, declared rather than defaulted.")),
]

CONTEXT_KINDS = [
    ("reality", "A mode or structure of reality."),
    ("universe", "A container of realities."),
    ("location", "A place, at any scale."),
    ("temporal-frame", "A time reference frame."),
    ("civilization", "A population and its institutions."),
    ("organization", "A body with decision rights."),
    ("execution-environment", "Where computation happens."),
    ("knowledge-domain", "A field of inquiry."),
    ("governance-domain", "A scope of decision rights."),
    ("simulation-domain", "A simulated setting."),
    ("physical-domain", "A physical setting."),
    ("unclassified-context", "The residual: a context whose kind is not determined."),
]

LEARNING_STAGES = [
    ("observe", "Something was seen. No claim yet."),
    ("record", "The observation was written into the ledger with identity and lineage."),
    ("analyze", "It was examined and a candidate claim was formed."),
    ("hypothesize", "The claim was stated as something testable."),
    ("experiment", "A measurement was performed against it."),
    ("validate", "Fitness for the purpose offered was judged and an authority decided."),
    ("operationalize", "It was dispositioned by the construct foundation and is relied on."),
]

META = [("knowledge-about-knowledge", "knowledge"), ("research-about-research", "research"),
        ("discovery-about-discovery", "discovery"),
        ("verification-about-verification", "verification"),
        ("validation-about-validation", "validation"),
        ("governance-about-governance", "governance"), ("learning-about-learning", "learning"),
        ("evolution-about-evolution", "evolution")]

FORBIDDEN_OUTCOMES = [
    ("ignore", "A presented subject that produces no record."),
    ("lose", "A recorded subject that later cannot be found."),
    ("silent-reject", "A refusal leaving no trace of what was refused."),
    ("untracked-failure", "A failure neither recorded nor surfaced."),
]

SEEDED = [
    ("states.seed", "seed_states"), ("domains.seed", "seed_domains"),
    ("qualifiers.seed", "seed_qualifiers"), ("relations.seed", "seed_relations"),
    ("profiles.seed", "seed_profiles"), ("lifecycle_axes.seed", "seed_axes"),
    ("gaps.classes", "seed_gap_classes"), ("reality.seed", "seed_realities"),
    ("temporal.seed", "seed_temporal_systems"), ("context.kinds", "seed_context_kinds"),
    ("evolution.subjects", "seed_evolution_subjects"),
    ("discovery.sources", "seed_discovery_sources"), ("learning.stages", "seed_learning_stages"),
    ("future_capabilities.seed", "seed_future_capabilities"),
    ("substrate.elements", "seed_substrate_elements"),
]

SCANNED = [
    "states.seed[].identifier", "states.classes[].class", "domains.seed[].identifier",
    "qualifiers.seed[].qualifier", "qualifiers.seed[].values[]", "relations.seed[].relation",
    "profiles.seed[].profile", "entity_classes.seed[].entity_class", "lifecycle_axes.seed[].axis",
    "lifecycle_axes.seed[].values[]", "gaps.classes[].identifier", "gaps.severities[].identifier",
    "contradiction.classes[].identifier", "contradiction.resolution_states[].identifier",
    "reality.seed[].identifier", "reality.dimensions[].identifier", "temporal.seed[].identifier",
    "context.kinds[].kind", "evolution.subjects[].identifier", "evolution.operators[].identifier",
    "discovery.targets[].identifier", "learning.stages[].stage",
    "future_capabilities.seed[].identifier", "meta_knowledge.subjects[].identifier",
]
BINDING_KINDS = [
    ("law check", "laws[].check", "contract.py::LAW_CHECKS"),
    ("detector", "discovery.sources[].detector", "discovery.py::DETECTORS"),
    ("admission", "extension_points[].admission", "admission.py::ADMISSIONS"),
    ("operator", "evolution.operators[].implementation", "evolution.py::OPERATORS"),
    ("bridge handler", "entity_classes.seed[].bridge_handler", "bridge.py::HANDLERS"),
    ("population reader", "self_application.seeded_populations[].reader",
     "ledger.py::POPULATION_READERS"),
    ("attribute reader", "entity_classes.seed[].required_attributes + profiles.seed[]",
     "model.py::ATTRIBUTE_READERS"),
    ("vocabulary owner reader", "states.binding_owners[].reader", "states.py::OWNER_READERS"),
    ("parity measure", "strategic_direction.parity_layers[].measured_by",
     "contract.py::PARITY_MEASURES"),
    ("reality probe", "strategic_direction.reality_probes[].probe", "probes.py::REALITY_PROBES"),
]

PROBES = [
    ("URKE-RP-01", "state_binding_reality", "states.seed[].binding",
     "the live vocabulary each declared owner carries"),
    ("URKE-RP-02", "gap_class_binding_reality", "gaps.classes[].ucon_unknown_class",
     "the unknown classes UCON-000001 declares"),
    ("URKE-RP-03", "reality_frame_reality", "reality.seed[].frame_kind",
     "the frame kinds the reference frame catalogue carries"),
    ("URKE-RP-04", "temporal_system_type_reality", "temporal.seed[].system_type",
     "the system types the temporal capability implements"),
    ("URKE-RP-05", "research_state_mapping_reality", "states.seed[].ucon_research_state",
     "the research states UCON-000001 declares"),
    ("URKE-RP-06", "contradiction_binding_reality", "contradiction.classes[]",
     "the contradiction classes and resolution states UCON-000001 declares"),
]
PARITY = [
    ("implementation", "engine/recursive_knowledge/", "module_present"),
    ("enforcement", "engine/recursive_knowledge/gate.py", "module_present"),
    ("measurement", "engine/recursive_knowledge/contract.py", "module_present"),
    ("verification", "engine/tests/unit/test_recursive_knowledge.py", "path_present"),
    ("validation", "engine/recursive_knowledge/declaration.py", "module_present"),
    ("evidence", "engine/recursive_knowledge/evidence.py", "module_present"),
    ("auditability", "engine/recursive_knowledge/ledger.py", "module_present"),
    ("failure_detection", "engine/recursive_knowledge/discovery.py", "module_present"),
    ("remediation", "gaps[].resolution_path", "every_gap_names_a_resolution_path"),
    ("evolution_pathway", "engine/recursive_knowledge/evolution.py", "module_present"),
]
ANTI_FINITE = [
    ("extension", "admission", "ADMISSIONS", "A member nobody declared is admitted at runtime."),
    ("replacement", "evolution", "operator_refine", "A definition changes without removing a member."),
    ("supersession", "ledger", "supersede", "A member is replaced by a named later one and retained."),
    ("subjects", "subjects", "record_contradiction",
     "Two incompatible positions are held at once, as an object."),
    ("coexistence", "ledger", "of_class", "Incompatible members coexist without removal."),
    ("future-discovery", "discovery", "discover",
     "What is missing is found by measurement rather than review."),
]

DISCLOSED = [
    ("URKE-G-07", "limitation", "S2-OPERATIONAL",
     "Subjects minted here carry no birth record: the object birth authority has not declared this "
     "namespace, so it does not know these identities exist.", "UOBC-000001",
     "Declare the namespace with the object birth authority and bind admission to it."),
    ("URKE-G-08", "limitation", "S1-ARCHITECTURAL",
     "Declared ownership roles are authority tokens checked against this declaration, not principals "
     "resolved through an identity authority. An owner is verifiable as declared, not as real.",
     "UIS-001", "Resolve ownership tokens through the identity authority."),
    ("URKE-G-09", "limitation", "S1-ARCHITECTURAL",
     "Review cadence is counted in ledger sequence, not elapsed time, because a clock reading would "
     "make two measurements of the same bytes differ. A review can be surfaced as due because work "
     "advanced past it, and not because time passed.", "CMG-000002",
     "Bind the review schedule to a temporal authority supplying a replayable coordinate."),
    ("URKE-G-10", "coverage-deficiency", "S1-ARCHITECTURAL",
     "Discovery detects the conditions its declared detectors describe. A condition no detector "
     "describes is not detected, and this capability cannot measure how large that set is.",
     "URKE-000001",
     "None available: a detector for an unanticipated condition cannot be written before the "
     "condition is anticipated. The residual-population detector is the nearest proxy and is not the "
     "same measurement."),
    ("URKE-G-11", "limitation", "S2-OPERATIONAL",
     "The population governed here is the population presented. An unknown nobody has identified is "
     "absent from the ledger, and its absence is indistinguishable from its non-existence.",
     "URKE-000001",
     "None available. This is the bound the principle is stated against: every identified unknown is "
     "governed, which is not a claim that every unknown is identified."),
    ("URKE-G-12", "verification-deficiency", "S1-ARCHITECTURAL",
     "This capability is subject to review on the terms it imposes on everything else, and its "
     "review is counted in ledger sequence rather than elapsed time.", "REPOSITORY-OWNER",
     "Review the laws, bindings and residual gaps whenever the ledger advances past the declared "
     "cadence, and record the review as an evolution step against the verification subject."),
    ("URKE-G-13", "limitation", "S1-ARCHITECTURAL",
     "The reality principle is enforced over the declared probes. A divergence between this "
     "declaration and a measured reality no probe examines is not detected.", "URKE-000001",
     "Add a probe whenever a new cross-capability binding is declared. Both counts are reported so "
     "the ratio is visible."),
    ("URKE-G-15", "coverage-deficiency", "S0-CONSTITUTIONAL",
     "The declaration exceeds the implementation. Thirty-two laws are declared and none is yet "
     "implemented, measured or tested; eight of the ten declared binding kinds have no implementing "
     "symbol; twelve of the fifteen declared modules do not exist; there is no gate, no evidence "
     "writer, no test suite and no verify.sh stage. Until those exist this capability is DECLARED "
     "and not IMPLEMENTED, and no part of it may be reported as complete.",
     "REPOSITORY-OWNER",
     "Implement the modules the substrate declares, bind every declared law to a measured check with "
     "a positive and a negative test, generate evidence, wire the gate into verify.sh, and close this "
     "gap only when the gate is measured OPEN on a clean checkout."),
    ("URKE-G-16", "verification-deficiency", "S0-CONSTITUTIONAL",
     "No law has a positive test or a negative test, so no law is known to be enforceable rather "
     "than merely computable. A law that cannot be made to fail measures nothing.",
     "REPOSITORY-OWNER",
     "Add, for every declared law, a test that forges a violating state and asserts the refusal, and "
     "a test that asserts the law holds on the seeded ledger."),
    ("URKE-G-17", "limitation", "S1-ARCHITECTURAL",
     "The self-improvement and future-capability registers name mechanisms and capabilities that are "
     "declared, not implemented. Every self-* mechanism is therefore a governed future capability at "
     "this point and none may be reported as an implemented behaviour.",
     "REPOSITORY-OWNER",
     "Implement each declared mechanism, bind it to the law that exercises it, and record the "
     "evidence it produces; until then the register is a plan under governance."),
    ("URKE-G-18", "coverage-deficiency", "S2-OPERATIONAL",
     "Discovery excludes its own findings from detector scope, so a finding that is unowned, "
     "contextless or undefined is not itself detected. Without the exclusion discovery never reached "
     "a fixed point, which was the worse defect.", "URKE-000001",
     "Give findings a narrower detector set of their own, so they are inspected without the "
     "inspection cascading."),
    ("URKE-G-14", "assumption", "S2-OPERATIONAL",
     "Composition replaces a type per condition, so two conditions composing to the same state, axes "
     "and qualifiers are indistinguishable in the ledger. The catalogue records the intended "
     "reading; the ledger records the composition.", "URKE-000001",
     "Add a qualifier whenever two conditions must be told apart, which is a data change. "
     "Collisions are measured every run and reported rather than argued about."),
]

FORBIDDEN_PHRASES = [
    "future completeness", "guaranteed first discovery", "guaranteed future knowledge",
    "guaranteed contradiction elimination", "guaranteed scientific supremacy",
    "guaranteed omniscience", "guaranteed perfect prediction", "guaranteed elimination of unknowns",
    "guaranteed future invention", "elimination of uncertainty", "provably complete",
    "complete knowledge", "omniscient", "every possible unknown", "all future knowledge",
    "eliminates all contradictions", "discovers everything", "knows everything", "cannot be wrong",
    "perfect prediction", "total knowledge", "perfect security", "perfect correctness",
    "permanently secure", "permanently complete", "final architecture",
]

LAWS = [
    ("URKE-L-01",
     "Every identified unknown becomes a governed subject: for every declared domain an unknown is "
     "admitted and receives identity, a context, a state, an owner, a governing authority and a "
     "disposition.", "every_identified_unknown_is_governed"),
    ("URKE-L-02",
     "Every residual is representable: the residual domain, epistemic form, articulation, relation, "
     "gap class and context kind each admit a subject rather than refusing one.",
     "residual_is_representable"),
    ("URKE-L-03",
     "Profile requirements are enforced at admission: for every declared profile, omitting any "
     "required attribute or required payload key is refused. This is what carries the contradiction "
     "and gap attribute sets, which are profiles rather than classes.",
     "profile_requirements_are_enforced"),
    ("URKE-L-04",
     "Histories are append-only: a state transition, a resolution step and a verification event each "
     "append, the earlier entries are byte-identical afterwards, and a verification declaring no "
     "assumptions or no limitations is refused.", "histories_are_append_only"),
    ("URKE-L-05",
     "A gap settles only when every declared closure criterion is recorded satisfied with a basis, "
     "and a review the ledger has advanced past is surfaced as a finding rather than dropped.",
     "gap_closure_and_review_are_governed"),
    ("URKE-L-06",
     "No member of any declared domain vocabulary appears as a string literal in this package's "
     "source: every one is read from the declaration.", "vocabulary_is_declared_not_coded"),
    ("URKE-L-07",
     "No state is terminal, and every declared state is reachable from the initial state.",
     "no_state_is_terminal"),
    ("URKE-L-08",
     "A state, domain, qualifier value, relation, profile, axis, gap class, discovery source, "
     "learning stage, context, reality and temporal system nobody declared can each be admitted at "
     "runtime, and admitting all of them changes no byte of this package.",
     "data_extension_needs_no_redesign"),
    ("URKE-L-09",
     "Every subject of the admissibility test is admissible at runtime — a future scientific domain, "
     "mathematical domain, intelligence model, ontology, governance model, verification model, "
     "reality model, temporal system, location system, civilization, substrate and future construct "
     "— and each admission is exercised on every measurement.", "future_domain_is_admissible"),
    ("URKE-L-10",
     "Discovery run twice over one ledger state admits nothing the second time, and a ledger "
     "carrying a detectable condition yields a finding: it converges without being inert.",
     "discovery_reaches_a_fixed_point"),
    ("URKE-L-11",
     "Discovery writes nothing outside the ledger: no forbidden write call is reachable from the "
     "discovery module, and the declaration digest is unchanged by a run.",
     "discovery_never_mutates_constitutional_truth"),
    ("URKE-L-12",
     "Every declared discovery target is claimed by a source, every declared source is implemented, "
     "and every implemented detector is claimed by a source.",
     "discovery_covers_every_declared_target"),
    ("URKE-L-13",
     "Evolution is observable, traceable and verifiable through one mechanism: every step carries "
     "subject, operator, before-digest, after-digest and basis; every declared subject evolves "
     "through the same entry point; no branch keyed on a subject identifier exists; and the chain "
     "detects tampering.", "evolution_is_one_traceable_mechanism"),
    ("URKE-L-14",
     "Realities and temporal systems are data: every declared reality resolves all declared "
     "dimensions or names them unresolved, every temporal system binds to a live system type and "
     "chronology model, no epoch, calendar, planet or coordinate literal is embedded in this "
     "package, and admitting a reality and a temporal system nobody declared changes no byte of it.",
     "worlds_are_data_driven"),
    ("URKE-L-15",
     "Nothing admitted can silently disappear and no forbidden outcome is reachable: the admitted "
     "count reconciles with the ledger population and the journal length, the chain is intact, no "
     "removal path exists, a presented subject always produces a record, a recorded subject is "
     "always retrievable, and no refusal is silent.",
     "nothing_admitted_can_silently_disappear"),
    ("URKE-L-16",
     "No subject exists outside governance: every ledger subject is presented into the UCON-000001 "
     "construct registry and carries exactly one active disposition there.",
     "no_subject_exists_outside_governance"),
    ("URKE-L-17",
     "No subject exists outside context: every subject names a context that is itself a governed "
     "subject, and the context of a context resolves to the declared root without a special case.",
     "no_subject_exists_outside_context"),
    ("URKE-L-18",
     "No declared guarantee of completeness, first discovery, future knowledge, contradiction "
     "elimination, supremacy, omniscience, perfect prediction, perfect security, perfect correctness "
     "or perfect stability appears in this package.", "no_completeness_claim_is_declared"),
    ("URKE-L-19",
     "Two measurements of the same committed bytes produce identical reports: no clock reading, no "
     "machine path, no iteration-order dependence.", "measurement_is_deterministic"),
    ("URKE-L-20",
     "Bound vocabularies are neither copied nor narrowed: every state binds to a row its owner "
     "carries or discloses a gap naming a finding, a referral and a remediation; no owner population "
     "is restated wholesale; and every UCON-000001 unknown class, contradiction class and resolution "
     "state is reachable through a declared binding.", "bound_vocabulary_is_neither_copied_nor_narrowed"),
    ("URKE-L-21",
     "Every gap this declaration discloses about itself is admitted into the ledger as a governed "
     "gap carrying every attribute the gap profile requires.",
     "disclosed_gaps_are_themselves_governed"),
    ("URKE-L-22",
     "Measured reality takes precedence over this declaration, parity is measured and review is not "
     "waivable: every declared probe is performed and a divergence is admitted as a governed "
     "contradiction that refuses this law, every parity layer is present, and the exemption lists "
     "are empty with this capability's own review obligation carried as a governed gap.",
     "reality_parity_and_review_are_enforced"),
    ("URKE-L-23",
     "Expressive power was preserved and the architecture did not grow: every condition any "
     "directive named is realised as a composition of one state, the independent axes and declared "
     "qualifiers with no type of its own; the primitive, entity-class and state counts stay within "
     "their declared bounds; and the complexity ratio is reported.",
     "expressiveness_is_preserved_within_bounds"),
    ("URKE-L-24",
     "The lifecycle axes are independent: the whole cross-product of declared axis values is "
     "reachable, and moving one axis changes no other.", "lifecycle_axes_are_independent"),
    ("URKE-L-25",
     "Every relationship is a governed subject carrying source, target, relation, basis and "
     "evidence, and one naming an absent endpoint is refused.", "relationships_carry_governance"),
    ("URKE-L-26",
     "Nothing unresolved becomes invisible: a gap and a contradiction each generate a research "
     "subject, a contradiction generates every declared consequence, and reflexive meta-knowledge is "
     "admitted through the declared relation with no new architectural layer.",
     "unresolved_generates_research"),
    ("URKE-L-27",
     "No learning path reaches the final stage without passing every declared stage in order, every "
     "bypass is forged and refused on every measurement, and reversal is supersession rather than "
     "deletion.", "learning_pipeline_cannot_be_bypassed"),
    ("URKE-L-28",
     "Every declared substrate element, anti-finite mechanism and self-improvement mechanism resolves "
     "to a live module symbol, is exercised on every measurement, and leaves a record: evidence "
     "rather than a claim.", "declared_mechanisms_are_live_and_exercised"),
    ("URKE-L-29",
     "Architecture may evolve and may not mutate silently: a change to the constitutional foundation "
     "requires a proposal carrying every declared requirement and one missing any is refused; and "
     "representability is measured first, so a construct the existing primitives can express yields "
     "a data extension rather than a proposal.",
     "architectural_change_requires_a_governed_proposal"),
    ("URKE-L-30",
     "Representation requires no understanding: a subject that is not understood, internally "
     "inconsistent, unverifiable, untestable and dependent on future science and future "
     "instrumentation is admitted, receives a disposition and becomes a governed research subject.",
     "representation_requires_no_understanding"),
    ("URKE-L-31",
     "Every subject in an unsettled state is eligible for a discovery workflow, and eligibility is "
     "computed from the declared lattice rather than from a list of favoured classes.",
     "unresolved_is_eligible_for_discovery"),
    ("URKE-L-32",
     "Stability is measured rather than claimed: every declared stability property resolves to a "
     "live measurement, every detected instability is admitted as a governed subject eligible for "
     "research, and no stability mechanism is exempt from review.",
     "stability_is_measured_and_instability_is_governed"),
    # THIS LAW WAS IN THE DECLARATION AND NOT IN THE BUILDER, WHICH MADE THE BUILDER A DELETION.
    # 6ad461ef added URKE-L-33 to urke-declaration.json directly; this list was not extended with
    # it, so the declaration carried 33 laws while `python3 build-declaration.py` produced 32 —
    # and the docstring above promises the run is idempotent. Anyone taking that promise at its
    # word silently removed a blocking law. UCOS-RFP-001 found it as CYC-UNGOVERNED on the first
    # verdict that gate has ever returned, and it is the reason the two disagree at all: a
    # declaration is the artifact of record, a builder is how it is written, and the moment the
    # two diverge the one that runs wins.
    ("URKE-L-33",
     "The declared vocabulary is not hardcoded: no module compares against, tests membership "
     "against, or enumerates a declared state, domain, relation or reality member. A member may "
     "be spelled in code as a serialization key or a label, which decides nothing; deciding from "
     "one forces a code change whenever the declaration gains a member, which is the harm this "
     "law names.",
     "vocabulary_is_not_hardcoded"),
]

def build() -> OD:
    d = OD()
    d["artifact_id"] = "URKE-000001"
    d["name"] = "Universal Recursive Knowledge, Discovery, Research and Evolution Foundation"
    d["version"] = "1.0.0"
    d["authority"] = (
        "NONE — DERIVED TRUTH. This declaration certifies nothing, admits no construct and owns no "
        "vocabulary another capability already owns. It declares the lifecycle the not-yet-known "
        "travels, and every claim in it is measured by engine/recursive_knowledge/contract.py "
        "rather than asserted here.")
    d["constitutional_superior"] = "UCON-000001"
    d["$constitutional_superior"] = (
        "UCON-000001 owns disposition. URKE owns none of it and re-implements none of it: every "
        "subject admitted here is presented into the UCON construct registry and receives its "
        "disposition there. That is why 'governed' never means 'admitted' in this capability, and "
        "why a subject can be fully governed while UCON has quarantined it.")
    d["strategic_superior"] = "USRD-000001"
    d["$strategic_superior"] = (
        "USRD-000001 sets direction and implements nothing. Three of its principles are directly "
        "measurable here and are bound to laws rather than quoted: the reality principle "
        "(URKE-L-27), declaration-implementation parity (URKE-L-28) and continuous improvement "
        "(URKE-L-29). The rest constrain what may be claimed, which URKE-L-21 enforces.")
    d["principle"] = OD([
        ("statement",
         "No identified unknown, contradiction, gap, limitation or unresolved question exists "
         "outside a governed lifecycle, and no mechanism here is closed against a future domain it "
         "has not met."),
        ("$statement",
         "Two halves, both measured. The first is arithmetic: what is admitted is counted, chained "
         "and not removable (URKE-L-18), and everything admitted carries a disposition (URKE-L-19) "
         "and a context (URKE-L-20). The second is structural: the vocabularies are data, so a "
         "state, a domain, a relation, a context, a reality or a temporal system nobody has named is "
         "admitted at runtime without a byte of this package changing (URKE-L-09, L-10, L-16, L-17)."),
        ("not_claimed",
         "That the population is exhaustive. An unknown nobody has identified is absent from it by "
         "construction, and that bound is recorded as gap URKE-G-11 rather than argued away."),
    ])
    d["design_rule"] = OD([
        ("statement",
         "A new primitive, entity class, state or vocabulary is admitted only on proof that the "
         "condition cannot be expressed through an existing subject, a relationship, an attribute, "
         "a qualifier, a context, evidence, governance or history."),
        ("$statement",
         "Applied, not aspired to. Forty-one lifecycle states, twenty-six unknown classes, "
         "thirty-two object kinds and fourteen entity classes were drafted for this capability and "
         "collapsed to seven states, two entity classes and two structural primitives. Every "
         "condition they named is still expressible and the condition catalogue records each one as "
         "a composition; URKE-L-30 realises every entry on every run and URKE-L-32 measures that "
         "the primitive count has not drifted upward while the data grew."),
        ("preferred_order", ["attribute", "qualifier", "relationship", "composition", "evidence",
                             "governance", "history", "state", "entity class", "primitive"]),
        ("new_primitive_proof_required", [
            "what capability cannot currently be represented",
            "why it cannot be represented through subject, relationship, attribute, qualifier, "
            "context, evidence, governance or history",
            "what measurable capability is gained",
            "what measurable complexity is added",
            "why the tradeoff is justified",
        ]),
        ("success_criterion",
         "Expressive power divided by structural complexity. The ratio is reported every run and is "
         "expected to rise as data grows, because data growth is not architecture growth."),
    ])
    d["primitives"] = OD([
        ("bound", 2),
        ("$bound",
         "Two, and the bound is measured rather than intended: URKE-L-32 refuses a count above it. "
         "A third is possible and must be a deliberate, visible act accompanied by the proof the "
         "design rule requires."),
        ("entity_class_bound", 2),
        ("state_bound", 9),
        ("$state_bound",
         "Headroom of two above the seven declared states, so a genuinely new lifecycle condition "
         "can be admitted at runtime while a drift back toward a state per concept is refused."),
        ("elements", [OD([("primitive", p), ("definition", defn), ("module", m), ("symbol", s)])
                      for p, defn, m, s in PRIMITIVES]),
        ("supporting", [OD([("device", p), ("definition", defn), ("module", m), ("symbol", s)])
                        for p, defn, m, s in SUPPORTING]),
        ("$supporting",
         "Expressive devices that are deliberately not primitives: each is data carried by a "
         "subject, and none is a type. They are declared so the distinction stays measurable — a "
         "device that quietly became a class would show up as a primitive-count refusal."),
    ])
    d["identity"] = OD([
        ("namespace", "ucos.recursive-knowledge"),
        ("key_domain", "urke.natural-key"),
        ("minted_by", "engine/kernel/identity.py::mint"),
        ("$minted_by",
         "Identity is derived, never assigned, and it is not a new grammar. UMK-000001 already owns "
         "deterministic identity; URKE folds a natural key through the Layer Zero digest and mints "
         "under its own namespace."),
    ])
    d["states"] = OD([
        ("initial", "UNKNOWN"),
        ("$initial", "The weakest available claim. Starting anywhere stronger would make the "
                     "framework assert knowledge at admission time."),
        ("settled", ["KNOWN", "SUPERSEDED"]),
        ("$settled",
         "The states in which no discovery workflow is owed. Settled is not terminal: both name "
         "successors, so a settled subject can be reopened the moment evidence changes. Everything "
         "else is eligible for discovery, and URKE-L-40 computes eligibility from this row rather "
         "than from a list of favoured classes."),
        ("classes", [
            OD([("class", "epistemic"), ("definition", "About what is or is not known."),
                ("binding_required", True)]),
            OD([("class", "verification"),
                ("definition", "About what evidence supports or refutes."),
                ("binding_required", True)]),
            OD([("class", "governance"), ("definition", "About who must decide next."),
                ("binding_required", False)]),
            OD([("class", "lifecycle"),
                ("definition", "About where in the working lifecycle the subject sits."),
                ("binding_required", False)]),
        ]),
        ("binding_owners", [
            OD([("owner", "UCOS-CEU-001"), ("reader", "ceu_populations"),
                ("definition", "The existence universe owns the existence, knowledge, epistemic and "
                               "temporal-model vocabularies. URKE binds to its rows and copies "
                               "none of them.")]),
            OD([("owner", "UKDA-000001"), ("reader", "ukda_lifecycle"),
                ("definition", "The knowledge-object lifecycle stages.")]),
        ]),
        ("seed", []),
    ])
    ids = [s[0] for s in STATES]
    for ident, title, cls, defn, binding, gp, ucon in STATES:
        d["states"]["seed"].append(OD([
            ("identifier", ident), ("title", title), ("state_class", cls), ("definition", defn),
            ("terminal", False), ("successors", sorted(i for i in ids if i != ident)),
            ("binding", OD(sorted(binding.items())) if binding else None),
            ("binding_gap", gap(gp[0], gp[1], gp[2], PROPOSE) if gp else None),
            ("ucon_research_state", ucon),
        ]))
    d["states"]["$successor_mesh"] = (
        "Every state names every other. With seven states that is not laxity, it is the honest "
        "shape: a subject can become contested from any state and can be reopened after "
        "supersession, so there is no working sequence to enforce. What constrains movement is "
        "evidence and governance, both recorded, neither a graph edge.")
    d["lifecycle_axes"] = OD([
        ("$purpose",
         "Existence, representation, admission, verification, validation, certification and "
         "acceptance are seven independent axes, not seven points on one scale. A single status "
         "field would make 'we can write it down' and 'we believe it' the same observable, and "
         "representation before understanding would stop being expressible — which is the one thing "
         "this capability exists to make possible. URKE-L-31 realises the whole cross-product."),
        ("seed", [OD([("axis", a), ("definition", defn), ("initial", i), ("values", v)])
                  for a, defn, i, v in AXES]),
    ])
    d["qualifiers"] = OD([
        ("confidence_qualifier", "confidence"),
        ("$confidence_qualifier", "The qualifier that records how well supported a claim is held to "
                                  "be. Named so a module can reach it by role."),
        ("$purpose",
         "Where a lifecycle state would otherwise multiply. Each qualifier below replaced between "
         "two and eight drafted states, and each definition records which. A qualifier value nobody "
         "declared is admitted through URKE-EP-03 and changes no byte of the package; a state cannot "
         "be added that cheaply, and that asymmetry is the design rule made operational."),
        ("seed", [OD([("qualifier", q), ("definition", defn), ("initial", i),
                      ("values", list(v))]) for q, defn, i, v in QUALIFIERS]),
    ])
    d["domains"] = OD([
        ("residual", "unclassified-domain"),
        ("$purpose",
         "A domain is data. Unknown physics is the domain 'physics' with knowledge status "
         "'unknown', not a class named UnknownPhysics — which is why admitting a science nobody has "
         "named is one row here and no code anywhere."),
        ("seed", [OD([("identifier", i), ("definition", defn)]) for i, defn in DOMAINS]),
    ])
    d["relations"] = OD([
        ("residual", "unclassified-relation"),
        ("$purpose",
         "Relationships carry what taxonomies would otherwise carry. Reflexive meta-knowledge is "
         "the reflects-on relation rather than a second layer; context containment is contained-by "
         "rather than a nesting field; a contradiction's consequences are generated-by rather than "
         "four object kinds; classification is classified-as rather than a subtype per class."),
        ("seed", [OD([("relation", r), ("definition", defn), ("inverse", inv)])
                  for r, defn, inv in RELATIONS]),
    ])
    d["entity_classes"] = OD([
        ("universal", "subject"),
        ("link", "relationship"),
        ("$link", "The class whose subject is a pair. Named here so a module can reach it without "
                  "writing a scanned vocabulary member as a literal."),
        ("$universal",
         "Everything is a subject unless its subject is a pair, in which case it is a relationship. "
         "URKE-L-32 refuses a third class: what would have been one is a profile, which is data."),
        ("seed", [OD([("entity_class", ec), ("title", t), ("definition", defn),
                      ("governance", "URKE-000001"), ("ucon_kind", uk), ("ucon_facet", uf),
                      ("bridge_handler", bh), ("required_attributes", attrs)])
                  for ec, t, defn, uk, uf, bh, attrs in ENTITY_CLASSES]),
    ])
    d["profiles"] = OD([
        ("default", "subject"),
        ("roles", [OD([("role", r), ("profile", p)]) for r, p in [
            ("situation", "context"),
            ("vocabulary_row", "vocabulary"),
            ("disclosure", "gap"),
            ("conflict", "contradiction"),
            ("investigation", "research"),
            ("lesson", "learning"),
            ("change_record", "evolution"),
            ("change_proposal", "architecture-proposal"),
            ("finding", "discovery"),
            ("statement", "claim"),
            ("sighting", "observation"),
        ]]),
        ("$roles", "A role is a code symbol bound to a profile. Modules address profiles through "
                   "these because writing a profile name in source would hardcode a scanned "
                   "vocabulary member, which URKE-L-06 refuses. Adding a profile therefore needs a "
                   "role only if code must reach it by name; data-only profiles need nothing."),
        ("$purpose",
         "A profile is the requirement set a subject carries because of what it is, keyed on its "
         "classification and declared as data. This is the whole of the entity collapse: a "
         "contradiction and a gap need different histories, and that difference is a row here "
         "rather than a class in code. A profile nobody declared is admitted through URKE-EP-05."),
        ("seed", [OD([("profile", p), ("required_attributes", ra), ("required_payload", rp),
                      ("definition", defn)]) for p, ra, rp, defn in PROFILES]),
    ])
    d["context"] = OD([
        ("$purpose",
         "Context is a subject, not a primitive special case. Earth, a temporal frame, a "
         "civilization, a simulation and an execution environment are all contexts, and each is a "
         "subject with the context profile. Containment and reference are relations, so a context "
         "inside a context needs no nesting field and no recursion in code. URKE-L-20 refuses a "
         "subject with no context and refuses a context whose own context does not resolve."),
        ("root", "unknown-future-reality"),
        ("$root",
         "The root context is the residual reality, deliberately: the outermost thing this "
         "repository can name is a reality it has not met, which is the honest top of the chain and "
         "the reason nothing bottoms out in a hardcoded planet."),
        ("kinds", [OD([("kind", k), ("definition", defn)]) for k, defn in CONTEXT_KINDS]),
        ("residual_kind", "unclassified-context"),
    ])
    d["context_instances"] = OD([
        ("$purpose",
         "Contexts the architecture must be able to represent. These are instances, not conditions: "
         "Earth and Mars are distinguished by identity, not by a different composition of state, axes "
         "and qualifiers, so listing them in the condition catalogue asked the uniqueness measurement "
         "to separate things classification does not separate. Their admissibility is measured by "
         "URKE-L-09 and their governance by URKE-L-17."),
        ("instances", [OD([("instance", i), ("domain", dm)]) for i, dm in [
            ("earth", "location"), ("moon", "location"), ("mars", "location"),
            ("orbital-habitat", "location"), ("galaxy", "location"), ("reality", "reality"),
            ("multireality", "reality"), ("temporal-frame", "temporal"),
            ("simulation", "reality"), ("civilization", "civilization"),
            ("organization", "governance"), ("execution-environment", "computation"),
            ("future-construct", "future-domain"),
        ]]),
    ])
    d["condition_catalogue"] = OD([
        ("$purpose",
         "Every condition any directive for this capability named by hand, resolved to a composition "
         "of one state, axis values, qualifier values and a domain. This is the evidence that "
         "collapsing the taxonomy cost no expressive power: URKE-L-30 realises every row on every "
         "measurement and refuses any that cannot be composed. Collisions — two conditions "
         "composing identically — are reported rather than hidden, because that is the real cost of "
         "composition and it belongs in the open."),
        ("conditions", CONDITIONS),
    ])
    d["contradiction"] = OD([
        ("minimum_positions", 2),
        ("affected_dimensions", ["knowledge", "authorities", "governance", "verification",
                                 "validation"]),
        ("generates", ["research", "discovery", "verification", "governance-review"]),
        ("verification_requires", ["verifier", "verdict", "assumptions", "limitations", "basis"]),
        ("$verification_requires",
         "A verification event declaring no assumptions or no limitations is refused, on the same "
         "principle UCON-000001 applies to verifiers: a verification that claims to assume nothing "
         "has not been examined."),
        ("classes", [OD([("identifier", i), ("definition", defn), ("ucon_contradiction_class", u)])
                     for i, defn, u in [
            ("logical", "Two statements that cannot both be true under the declared logic.", "logical"),
            ("evidential", "Two bodies of evidence pointing in opposite directions.", "evidential"),
            ("authority-conflict", "Two authorities claiming the same decision.", "authority-conflict"),
            ("temporal", "A conflict appearing only under a particular ordering or frame.", "temporal"),
            ("framework", "Positions expressible only in frameworks that cannot be reconciled as "
                          "stated.", "framework"),
            ("measurement", "Two measurements of one quantity disagreeing beyond their declared "
                            "uncertainty.", "measurement"),
            ("undetermined", "The residual: a contradiction whose class is not determined.",
             "undetermined"),
        ]]),
        ("resolution_states", [OD([("identifier", i), ("definition", defn), ("contradicting", c),
                                   ("ucon_resolution_state", u)]) for i, defn, c, u in [
            ("open", "Recorded, unresolved, owned.", True, "open"),
            ("under-research", "A research subject is investigating it.", True, "under-research"),
            ("resolved-by-evidence", "New measured evidence decided it.", False,
             "resolved-by-evidence"),
            ("resolved-by-supersession", "One position was superseded.", False,
             "resolved-by-supersession"),
            ("resolved-by-reframing", "The conflict dissolved once the framing was corrected.",
             False, "resolved-by-reframing"),
            ("undecidable", "No available decision procedure applies.", True, "undecidable"),
        ]]),
    ])
    d["gaps"] = OD([
        ("classes", [OD([("identifier", i), ("definition", defn), ("ucon_unknown_class", u)])
                     for i, defn, u in GAP_CLASSES]),
        ("residual", "unclassified-gap"),
        ("severities", [OD([("identifier", i), ("rank", r), ("definition", defn)])
                        for i, r, defn in [
            ("S0-CONSTITUTIONAL", 0, "Affects a constitutional invariant."),
            ("S1-ARCHITECTURAL", 1, "Affects a structural decision more than one capability relies on."),
            ("S2-OPERATIONAL", 2, "Affects operation of a capability."),
            ("S3-LOCAL", 3, "Local to one module or artifact."),
            ("SU-UNASSESSED", 9, "Not yet assessed. Never treated as low."),
        ]]),
        ("closure_rule", "all_criteria_satisfied"),
        ("$closure_rule",
         "A gap settles only when every declared criterion is recorded satisfied with a basis, and a "
         "gap with no criteria cannot be admitted at all — which is what stops settlement from "
         "meaning 'stopped being looked at'."),
        ("review", OD([
            ("cadence_unit", "ledger-sequence"),
            ("$cadence_unit",
             "Counted in ledger sequence, not wall-clock time, because the measurement must be "
             "identical on two runs of the same bytes. The consequence is disclosed as URKE-G-09 "
             "rather than hidden."),
            ("default_cadence", 64), ("minimum_cadence", 1),
        ])),
    ])
    d["discovery"] = OD([
        ("$never_mutates",
         "Discovery admits subjects into the URKE ledger and writes nothing else. URKE-L-12 parses "
         "this package and refuses any forbidden write call reachable from the discovery module, "
         "then re-measures the declaration digest after a run."),
        ("write_scope", ["engine/recursive_knowledge/ledger.py::KnowledgeLedger.admit"]),
        ("scope_excludes_role", "finding"),
        ("$scope_excludes_role",
         "Discovery does not inspect its own findings. Measured defect: with findings in scope the "
         "engine reported on its reports and each pass produced more, so it never converged and the "
         "fixed-point law could not hold. The exclusion is narrow and its cost is disclosed as "
         "URKE-G-18: a finding is not itself checked for an owner, a context or a definition."),
        ("forbidden_write_calls", ["open", "write_text", "write_bytes", "writelines", "mkdir",
                                   "replace", "remove", "unlink", "rmtree", "rename", "dump",
                                   "system", "run", "Popen"]),
        ("priority_scale", ["P0", "P1", "P2", "P3", "PU"]),
        ("impact_scale", ["constitutional", "architectural", "operational", "local", "unassessed"]),
        ("targets", [OD([("identifier", i), ("definition", defn)]) for i, defn in TARGETS]),
        ("sources", [OD([("source_id", s), ("detector", det), ("target", t), ("priority", p),
                         ("impact", im), ("definition", defn)])
                     for s, det, t, p, im, defn in SOURCES]),
    ])
    d["evolution"] = OD([
        ("$observable",
         "Every evolution step is a subject in the same append-only chained ledger as everything "
         "else, carrying subject, operator, before-digest, after-digest and basis. Evolution of the "
         "framework is measured by the framework, which is what makes URKE-L-13 computable."),
        ("entry_point", "engine/recursive_knowledge/evolution.py::evolve"),
        ("$entry_point",
         "One entry point for every subject. URKE-L-15 parses the module and refuses a branch keyed "
         "on a subject identifier, because a special case for one subject is the beginning of a "
         "special case for each."),
        ("operators", [OD([("identifier", i), ("definition", defn),
                           ("implementation", "operator_" + i)]) for i, defn in OPERATORS]),
        ("subjects", [OD([("identifier", i),
                          ("definition", f"How the repository expresses {i.replace('-', ' ')}."),
                          ("operators", ops)]) for i, ops in EVO_SUBJECTS]),
    ])
    d["self_evolution"] = OD([
        ("$purpose", "The subjects this capability must extend in itself, exercised in memory on "
                     "every measurement so the claim is performed rather than asserted."),
        ("subjects", [OD([("identifier", i), ("exercised_by", e)]) for i, e in SELF_EVOLUTION]),
    ])
    d["self_improvement"] = OD([
        ("$purpose",
         "Self-improvement as measurable mechanism rather than claim. Each row names a live symbol "
         "that runs on every measurement and leaves a record in the ledger; URKE-L-37 refuses a "
         "mechanism whose symbol is absent, that does not run, or that produces no evidence."),
        ("mechanisms", [OD([("mechanism", m), ("module", mod), ("symbol", s), ("behaviour", b)])
                        for m, mod, s, b in SELF_IMPROVEMENT]),
    ])
    d["learning"] = OD([
        ("$purpose",
         "One governed pipeline. No path reaches the final stage without passing every stage in "
         "order, and URKE-L-36 forges each bypass and asserts the refusal. Reversal is supersession, "
         "never deletion: a retracted lesson keeps its record and gains a successor."),
        ("stages", [OD([("stage", s), ("definition", defn)]) for s, defn in LEARNING_STAGES]),
        ("bypass_refused", True), ("reversal_operator", "supersede"),
    ])
    d["meta_knowledge"] = OD([
        ("$purpose",
         "Knowledge about knowledge needs no new layer: the subject of a subject is expressed with "
         "the declared reflects-on relation. URKE-L-35 admits each reflexive form through that "
         "relation and refuses if any requires new structure."),
        ("relation", "reflects-on"),
        ("subjects", [OD([("identifier", i), ("reflects_on", r)]) for i, r in META]),
    ])
    d["reality"] = OD([
        ("$data_driven",
         "A reality is a row, not a branch. Declared dimensions are resolved from this data and an "
         "unresolved dimension is the declared token, never a default and never a silence. Admitting "
         "a reality nobody has named leaves every byte of the package unchanged, which URKE-L-16 "
         "measures."),
        ("unresolved_token", U),
        ("dimensions", [OD([("identifier", i), ("definition", defn)])
                        for i, defn in REALITY_DIMENSIONS]),
        ("frame_kind_owner", "engine/context/catalog/reference-frames.json"),
        ("seed", [OD([("identifier", i), ("title", t), ("residual", res), ("frame_kind", fk),
                      ("frame_kind_gap", fg),
                      ("systems", OD(zip([x[0] for x in REALITY_DIMENSIONS], sv)))])
                  for i, t, res, fk, fg, sv in REALITIES]),
    ])
    d["temporal"] = OD([
        ("$no_finite_assumption",
         "No epoch, calendar, planet, coordinate or clock literal appears in this package's source. "
         "Each is a field below, and the residual system declares its epoch unresolved rather than "
         "inheriting one. URKE-L-17 parses the package for the declared literals and refuses any "
         "occurrence."),
        ("unresolved_token", U),
        ("exempt_modules", ["engine/recursive_knowledge/evidence.py"]),
        ("$exempt_modules",
         "The evidence writer holds the single clock reading in this capability, and naming the clock "
         "requires the literal the scan forbids everywhere else. It is exempt from the temporal scan "
         "and from nothing else; the reading enters evidence only and is an input to no digest, no "
         "identity and no verdict."),
        ("system_type_owner", "engine/temporal/coordinate.py::SystemType"),
        ("chronology_owner", "UCOS-CEU-001"),
        ("forbidden_source_literals", ["1970-01-01", "1972-01-01", "2000-01-01", "J2000",
                                        "gregorian", "unix epoch", "datetime.now", "time.time",
                                        "utcnow", "latitude", "longitude", "nation-state", "wgs84"]),
        ("seed", [OD([("identifier", i), ("title", t), ("system_type", st),
                      ("chronology_model", cm), ("epoch", ep), ("calendar_system", cal),
                      ("causality_model", cau), ("reference_frame", rf),
                      ("conversion_authority", ca), ("epoch_gap", eg)])
                  for i, t, st, cm, ep, cal, cau, rf, ca, eg in TEMPORAL]),
    ])
    d["ownership"] = OD([
        ("unassigned_token", "UNASSIGNED"),
        ("$unassigned_token",
         "An explicit token, so 'nobody owns this' is a fact a detector finds rather than a blank "
         "that reads as an oversight. Admission still requires the attribute to be present."),
        ("roles", [OD([("identifier", i), ("definition", defn)]) for i, defn in [
            ("URKE-000001", "This capability, for subjects describing its own declared vocabulary."),
            ("UNASSIGNED", "No owner assigned yet. Discoverable, never silent."),
            ("REPOSITORY-OWNER", "The human authority of record."),
            ("UCON-000001", "The construct foundation."),
            ("UCOS-CEU-001", "The existence universe."),
            ("UKDA-000001", "The knowledge object authority."),
            ("UCXI-000001", "The context and location authority."),
            ("UOBC-000001", "The object birth authority."),
            ("UIS-001", "The identity authority."),
            ("CMG-000002", "The temporal authority."),
            ("engine/governance", "The governance engine."),
        ]]),
    ])
    d["extension_points"] = [OD([("point_id", p), ("subject", s), ("owner", "URKE-000001"),
                                 ("admission", a), ("evolution_subject", e)])
                             for p, s, a, e in EXTENSION_POINTS]
    d["future_domain_subjects"] = [OD([("identifier", i), ("admission", a)])
                                   for i, a in FUTURE_DOMAIN_SUBJECTS]
    d["admissibility_test"] = OD([
        ("question",
         "Can this mechanism represent, govern, research, verify, validate, evolve and integrate a "
         "future scientific domain, future intelligence model, future ontology, future temporal "
         "system, future reality model, future civilization or future construct without "
         "architectural redesign?"),
        ("$question",
         "Applied as a measurement. Every subject is admitted at runtime on every measurement and "
         "the package fingerprint is compared before and after; a mechanism that cannot answer yes "
         "fails URKE-L-10."),
        ("subjects", [i for i, _ in FUTURE_DOMAIN_SUBJECTS]),
    ])
    d["substrate"] = OD([
        ("$purpose",
         "The mechanisms a future recursive capability stands on. Each is a live module symbol, and "
         "URKE-L-41 refuses an element whose module or symbol is absent, a capability requiring an "
         "undeclared element, and an element no capability requires."),
        ("elements", [OD([("substrate_id", s), ("mechanism", m),
                          ("module", f"engine/recursive_knowledge/{mod}.py"), ("symbol", sym)])
                      for s, m, mod, sym in SUBSTRATE]),
    ])
    d["future_capabilities"] = OD([
        ("$purpose",
         "This capability is a substrate, not a repository. These are the capabilities it exists to "
         "make implementable without architectural redesign."),
        ("$not_claimed",
         "That any of them exists, or that the substrate is sufficient for them. What is measured is "
         "that each named element is present and exercised."),
        ("seed", [OD([("identifier", i), ("requires", r)]) for i, r in FUTURE_CAPABILITIES]),
    ])
    d["anti_finite_mechanisms"] = OD([
        ("$purpose",
         "No capability may assume its ontology, taxonomy, vocabulary, science, mathematics, "
         "intelligence models, governance models, verification models or reality models are "
         "complete. Operationally that obligation is six governed mechanisms, each a live symbol. "
         "URKE-L-43 resolves and exercises every one."),
        ("$implementation_may_be_finite",
         "The implementation is finite; the architecture does not require finiteness. That is the "
         "distinction these mechanisms exist to hold, and it is why every bound above is a declared "
         "number a law reads rather than a constant in code."),
        ("mechanisms", [OD([("mechanism", m),
                            ("module", f"engine/recursive_knowledge/{mod}.py"), ("symbol", s),
                            ("definition", defn)]) for m, mod, s, defn in ANTI_FINITE]),
    ])
    d["forbidden_outcomes"] = OD([
        ("$purpose",
         "The four outcomes no code path here may produce. URKE-L-38 measures each: a presented "
         "subject always produces a record, a recorded subject is always retrievable, no refusal is "
         "silent, and no failure is untracked."),
        ("outcomes", [OD([("outcome", o), ("definition", defn)]) for o, defn in FORBIDDEN_OUTCOMES]),
    ])
    d["implementation_priorities"] = OD([
        ("$purpose", "The ordering used to settle design questions here, recorded so a later reader "
                     "can tell a decision from an accident."),
        ("priorities", [
            "A working implementation before a larger declaration.",
            "Measured laws before declared intentions.",
            "Non-vacuous tests before coverage.",
            "Evidence generation before reporting.",
            "Deterministic behaviour before convenience.",
            "Extensibility before additional vocabulary.",
            "Composition before proliferation.",
        ]),
    ])
    d["architecture_evolution"] = OD([
        ("$purpose",
         "An architecture freeze is not a claim that architecture can never change; it is a claim "
         "that change is governed. Three tiers, with different burdens: the constitutional "
         "foundation is stable and the burden of proof sits on any change to it, architecture itself "
         "is a governed subject that may evolve through an evidenced proposal, and domains are "
         "unbounded and evolve by adding a data row."),
        ("tiers", [
            OD([("tier", "constitutional-foundation"),
                ("scope", "the two structural primitives, the two entity classes, the state lattice"),
                ("burden_of_proof", "change"),
                ("mechanism", "architectural change proposal"),
                ("$note", "Stability is the default and needs no argument; change needs evidence "
                          "that the existing primitives cannot represent the construct.")]),
            OD([("tier", "governed-architectural-evolution"),
                ("scope", "how the foundation is measured, enforced and bound to other capabilities"),
                ("burden_of_proof", "change"),
                ("mechanism", "architectural change proposal with impact analysis"),
                ("$note", "Architecture is a subject in the ledger like anything else, so its "
                          "changes carry lineage and are replayable.")]),
            OD([("tier", "unlimited-domain-evolution"),
                ("scope", "domains, qualifier values, relations, profiles, contexts, realities, "
                          "temporal systems, discovery sources, states within the declared bound"),
                ("burden_of_proof", "none"),
                ("mechanism", "governed admission"),
                ("$note", "Unbounded by construction. Unknown mathematics, unknown physics, an "
                          "unknown civilization or a reality nobody has met are each one admitted "
                          "row and no code change, which URKE-L-09 measures.")]),
        ]),
        ("proposal_requirements", ["proposal", "evidence", "verification", "validation", "lineage",
                                   "impact", "governance_decision"]),
        ("$proposal_requirements",
         "All seven, and URKE-L-44 forges a proposal missing each one in turn and asserts the "
         "refusal. A proposal that could be recorded incomplete would be an architectural mutation "
         "with a paper trail that reads as governance."),
        ("default_rule", [
            "attempt representation with the existing primitives",
            "measure representability rather than judging it",
            "if representable, extend data only and record the composition",
            "if not representable, raise an architectural change proposal",
            "subject the proposal to governance, verification and validation",
        ]),
        ("$default_rule",
         "Executable, not advisory: engine/recursive_knowledge/proposal.py::representability "
         "performs step two and returns either the composition that expresses the construct or the "
         "reason no composition does. URKE-L-45 exercises both outcomes every run, so 'architecture "
         "evolves by evidence, not by anticipation' is a measured behaviour."),
        ("silent_mutation_refused", True),
    ])
    d["stability"] = OD([
        ("$purpose",
         "Perfect stability is not claimed and cannot be. What is implemented is continuous "
         "measurement: every stability property below resolves to a live measurement, and every "
         "instability it finds becomes a governed subject like anything else — which is why no new "
         "primitive was needed to hold one. An instability is a gap or a contradiction, and it is "
         "therefore already investigable, verifiable, researchable and correctable."),
        ("$not_claimed", "That the system is stable, that instability is prevented, or that every "
                         "instability is detectable. Only that what is detected is governed."),
        ("properties", [OD([("property", p), ("measured_by", m)]) for p, m in [
            ("measurable", "chain_integrity"), ("observable", "population_reconciles"),
            ("explainable", "every_finding_names_its_detector"),
            ("governable", "every_instability_is_a_governed_subject"),
            ("verifiable", "declaration_matches_measured_world"),
            ("validatable", "profile_requirements_hold"),
            ("improvable", "instability_generates_research"),
            ("recoverable", "supersession_restores_without_deletion"),
            ("evolvable", "stability_mechanisms_are_evolution_subjects"),
        ]]),
        ("instability_becomes", "gap"),
        ("$instability_becomes",
         "Detected instability is admitted as a gap subject: detectable because a detector found it, "
         "representable because a gap is a profile not a type, traceable through its lineage, "
         "attributable through its owner, analyzable because it is eligible for research, and "
         "correctable because a gap closes only against satisfied criteria."),
        ("exempt", []),
        ("$exempt", "No stability mechanism is exempt from review. The list is empty and a law "
                    "refuses a non-empty one."),
    ])
    d["strategic_direction"] = OD([
        ("directive", "USRD-000001"),
        ("$reality_principle",
         "Measured reality takes precedence over this declaration. Where the two disagree the "
         "disagreement is admitted as a governed contradiction carrying both positions, and it is "
         "never resolved by editing the measurement."),
        ("reality_probes", [OD([("probe_id", p), ("probe", pr), ("declared", dec),
                                ("measured", m),
                                ("on_conflict", "admit a contradiction of the declared class and "
                                                "refuse the law")])
                            for p, pr, dec, m in PROBES]),
        ("conflict_contradiction_class", "evidential"),
        ("conflict_owner", "URKE-000001"),
        ("parity_layers", [OD([("layer", lay), ("evidence", e), ("measured_by", mb)])
                           for lay, e, mb in PARITY]),
        ("$parity_layers", "A capability missing any layer is partial, and the report says so rather "
                           "than rounding up. Standing is computed, never asserted."),
        ("review", OD([
            ("$purpose", "No capability is permanently exempt from review, including this one."),
            ("self_review_gap", "URKE-G-12"), ("cadence", 64), ("exempt", []),
            ("$exempt", "Empty, and URKE-L-29 refuses a non-empty list. An exemption mechanism that "
                        "exists is an exemption mechanism that will be used."),
        ])),
    ])
    d["bound_vocabularies"] = OD([
        ("$purpose",
         "Explicit reachability. The construct foundation declares fourteen unknown classes and this "
         "capability declares eleven gap classes, so reachability cannot be read off the gap table "
         "alone. Each row below states which declared member reaches which class of the superior "
         "vocabulary. Nothing is inferred from a name resembling another name."),
        ("ucon_unknown_classes", [OD([("ucon_class", u), ("reached_by", r), ("via", v)])
                                  for u, r, v in [
            ("unknown-mathematics", "mathematics", "domains.seed"),
            ("unknown-physics", "physics", "domains.seed"),
            ("unknown-ontology", "ontology", "domains.seed"),
            ("unknown-intelligence", "intelligence", "domains.seed"),
            ("unknown-governance", "governance", "domains.seed"),
            ("unknown-economic-model", "economics", "domains.seed"),
            ("unknown-temporal-model", "temporal", "domains.seed"),
            ("unknown-reality-model", "reality", "domains.seed"),
            ("unknown-location-model", "location", "domains.seed"),
            ("unknown-computation-model", "computation", "domains.seed"),
            ("unknown-identity-model", "identity", "domains.seed"),
            ("unknown-knowledge-form", "missing-knowledge", "gaps.classes"),
            ("unknown-future-domain", "future-risk", "gaps.classes"),
            ("unknown-unclassified", "unclassified-gap", "gaps.classes"),
        ]]),
    ])

    d["gap_disclosure"] = OD([
        ("$purpose",
         "Every gap this declaration discloses about itself is admitted into the ledger as a "
         "governed gap. The attributes an inline binding gap does not carry are declared here per "
         "disclosure source rather than invented in code, so URKE-L-25 measures data against data."),
        ("closure_criterion_template",
         "the remediation this gap names is performed and the performance is recorded"),
        ("review_cadence", 64),
        ("sources", [OD([("source", s), ("classification", c), ("severity", sev),
                         ("definition", defn)]) for s, c, sev, defn in [
            ("state_binding", "limitation", "S1-ARCHITECTURAL",
             "A declared state holding a vocabulary locally because no owner carries a row for it."),
            ("reality_frame_binding", "assumption", "S2-OPERATIONAL",
             "A reality whose frame-kind binding is approximate or absent."),
            ("temporal_epoch", "unknown", "S2-OPERATIONAL",
             "A temporal system whose epoch is unresolved."),
            ("declared", "limitation", "S1-ARCHITECTURAL",
             "A limitation stated directly rather than as a side effect of a binding."),
        ]]),
    ])
    d["disclosed_gaps"] = [OD([("gap_id", g), ("classification", c), ("severity", s),
                               ("finding", f), ("referred_to", r), ("remediation", rem)])
                           for g, c, s, f, r, rem in DISCLOSED]
    d["non_goals"] = OD([
        ("$purpose",
         "The phrases this capability must never declare, kept as data so the detector cannot match "
         "its own source. The ratchet runs both ways: an undeclared occurrence refuses, and a "
         "preserved site whose occurrence has vanished also refuses."),
        ("forbidden_phrases", FORBIDDEN_PHRASES),
        ("preserved_sites", []),
        ("stated_non_goals", [
            "The population of unknowns here is not claimed exhaustive.",
            "No claim is made to identify a discovery before anyone else.",
            "No claim is made that future knowledge is obtainable.",
            "No claim is made that contradictions will be eliminated.",
            "No claim is made that unknowns or uncertainty will be eliminated.",
            "No claim of scientific precedence over any other body of work is made.",
            "No claim is made to know what has not been measured.",
            "No claim is made that predictions are correct.",
            "No security posture is claimed; this capability claims none.",
            "No correctness is claimed beyond what the laws measure.",
            "No completeness is claimed now or later, and a review obligation is carried as a "
            "governed gap.",
        ]),
    ])
    d["self_application"] = OD([
        ("$purpose", "What this capability measures about itself every run, so its claims are "
                     "performed rather than described."),
        ("seeded_populations", [OD([("population", p), ("reader", r), ("entity_class", "subject")])
                                for p, r in SEEDED]),
    ])
    d["metrics"] = OD([
        ("$purpose",
         "The complexity budget, reported on every measurement. Architectural growth that adds "
         "primitives without adding expressive power is visible here as a falling ratio, and "
         "URKE-L-32 refuses a primitive count above the declared bound."),
        ("reported", ["primitive_count", "entity_class_count", "state_count", "axis_count",
                      "qualifier_count", "qualifier_value_count", "domain_count", "relation_count",
                      "profile_count", "condition_count", "law_count", "data_row_count",
                      "complexity_ratio"]),
        ("complexity_ratio", "condition_count / primitive_count"),
    ])
    d["source_discipline"] = OD([
        ("package", "engine/recursive_knowledge"),
        ("$purpose",
         "Domain vocabulary is data. A member of any scanned vocabulary appearing as a string "
         "literal in this package's source is a hardcoded vocabulary and URKE-L-07 refuses it. "
         "Binding names are the opposite case: they are code symbols the declaration names on "
         "purpose and must appear in the source, because that is what a two-way binding is."),
        ("scanned_vocabularies", SCANNED),
        ("binding_kinds", [OD([("kind", k), ("declared_at", da), ("implemented_in", im)])
                           for k, da, im in BINDING_KINDS]),
        ("exempt_modules", ["engine/recursive_knowledge/declaration.py"]),
        ("$exempt_modules",
         "The parser names the JSON keys it reads. A key name is the shape of a document, not a "
         "member of a vocabulary, and a parser that could not name its own keys could not be "
         "written. No vocabulary member is exempt anywhere, including here."),
    ])
    d["laws"] = [OD([("law_id", i), ("statement", s), ("check", c), ("blocking", True)])
                 for i, s, c in LAWS]
    d["evidence"] = OD([
        ("home", ".ucos/recursive-knowledge/"),
        ("$home", "Untracked by design. Evidence here is a record of a measurement, never Repository "
                  "Truth, and deleting the directory changes no verdict."),
        ("records", [
            OD([("record_name", "recursive-knowledge-report.json"),
                ("producer", "engine/recursive_knowledge/evidence.py::build"),
                ("content", "the law report and the complexity metrics")]),
            OD([("record_name", "knowledge-ledger.json"),
                ("producer", "engine/recursive_knowledge/evidence.py::write_ledger"),
                ("content", "every governed subject, its histories and the journal chain")]),
        ]),
    ])
    d["gate"] = OD([
        ("command", "python -m engine.recursive_knowledge.gate --gate --quiet"),
        ("repair_command", "make urke"),
        ("verify_stage_label",
         "universal recursive knowledge foundation (URKE-000001, every unknown governed and no "
         "mechanism closed against a future domain)"),
        ("exit_codes", [
            OD([("code", 0), ("meaning", "OPEN — every blocking law was measured and holds")]),
            OD([("code", 1), ("meaning", "CLOSED — a blocking law was measured and refused")]),
            OD([("code", 2), ("meaning", "FAULT — no verdict could be reached")]),
        ]),
    ])
    d["closed_set"] = False
    d["upper_limit"] = None
    return d


def main() -> None:
    doc = build()
    (HERE / "urke-declaration.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(
        f"primitives={len(doc['primitives']['elements'])} "
        f"entity_classes={len(doc['entity_classes']['seed'])} "
        f"states={len(doc['states']['seed'])} axes={len(doc['lifecycle_axes']['seed'])} "
        f"qualifiers={len(doc['qualifiers']['seed'])} domains={len(doc['domains']['seed'])} "
        f"relations={len(doc['relations']['seed'])} profiles={len(doc['profiles']['seed'])} "
        f"conditions={len(doc['condition_catalogue']['conditions'])} "
        f"sources={len(doc['discovery']['sources'])} laws={len(doc['laws'])}"
    )


if __name__ == "__main__":
    main()
