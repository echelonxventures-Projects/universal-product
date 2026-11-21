# UCOS Ω∞ — PHASE 1 ARTIFACT MODEL
## Deliverables 3 and 4 — the universal artifact, and classification without extensions

**AUTHORITY = NONE (DERIVED TRUTH).** A vocabulary, not a policy.

---

## 1. THE ASSUMPTION, AS FIELDS

`engine/universal_discovery/model.py` defines an artifact this way:

```python
path: str          # a POSIX repo-relative FILESYSTEM path
module: str        # a dotted PYTHON module name
statements: int    # counted from a PYTHON ast
callables: int     # counted from a PYTHON ast
imports: int       # counted from a PYTHON ast
```

**Five fields are Python and one is a filesystem.** That model cannot describe a row in a dataset, an
object in a bucket, or a workflow definition — not because anyone decided to exclude them, but
because *the vocabulary has no word for them.*

This is the sharpest form of Rule Ω-1. Python and the filesystem must be **implementations of
abstractions**, never the abstractions themselves.

---

## 2. THE SIX-PART SHAPE (DELIVERABLE 3)

```python
@dataclass(frozen=True)
class Artifact:
    identifier: str
    location: Location
    artifact_type: ArtifactType = UNKNOWN
    authority: Authority = field(default_factory=Authority)
    metadata: Mapping[str, str] = field(default_factory=dict)
    relationships: tuple[Relationship, ...] = ()
    classification_rule: str = ""
```

| Part | Why it is universal rather than convenient |
|---|---|
| `identifier` | Stable, provider-scoped, opaque. **Not a path** — a path is one provider's way of naming a thing; an object key, a URN and a graph node id are others |
| `location` | `(provider, locator, revision)`. The provider is *part of the location* because "the same locator" means different things to different providers, and conflating them is how a federation double-counts |
| `artifact_type` | An extensible `ArtifactType`. **PYTHON is a value here** — the system no longer has a Python *case*, it has a Python *type* |
| `authority` | Who owns it and by which derivation step. **Carried, never inferred here** |
| `metadata` | Provider-declared facts. Open by construction, because a provider knows things about its own artifacts no abstraction can anticipate |
| `relationships` | Typed edges to other **identifiers**. The landing place for graph spaces, dependency closure and lineage |
| `classification_rule` | Which classifier produced the type, so a type is auditable rather than asserted |

### What is deliberately absent — the hardest constraint in the file

There is **no** `statements`, **no** `callables`, **no** `imports`, **no** `module`, **no** `path`,
**no** `root`.

Those are measurements of *one artifact type*, produced by a Python-specific analyser. Putting them
here is exactly what made the previous model unable to describe anything else. A language-specific
measurement belongs in a language-specific analyser and reaches this model through `metadata` —
which is why `metadata` is a mapping and not a fixed record.

**Asserted structurally**, not promised:

```python
def test_the_model_carries_no_language_specific_field() -> None:
    fields = set(Artifact.__dataclass_fields__)
    assert not fields & {"module", "statements", "callables", "imports", "path", "root"}
```

If that test ever fails, the abstraction has been re-specialised and Phase 1 has been undone.

### The lift proves nothing is lost

`compat.as_universal()` converts an Ω-1 artifact into the universal model. Every Python-specific
field becomes metadata; the type becomes a value; the Ω-1 governance verdicts ride along:

```
artifact_type            = PYTHON                      ← was implicit in the query
metadata.python_statements  = "42"                     ← was a FIELD
metadata.python_callables   = "7"                      ← was a FIELD
metadata.python_imports     = "3"                      ← was a FIELD
metadata.python_module      = "engine.foundation.identity"
metadata.omega_disposition  = "MEASURED"
metadata.omega_reachable    = "true"
authority                = Authority("engine.foundation", "Ω-A-06")
```

Duck-typed on purpose: importing the legacy dataclass for an `isinstance` check would make
`engine.universal_discovery` an import-time dependency of the abstraction layer, inverting the
dependency Phase 1 exists to remove.

### Supporting value objects

**`Location`** — `revision` is optional and **empty is honest**. A provider that cannot name a
revision declares no `VERSIONED_CONTENT` and leaves it empty, rather than inventing a timestamp that
would make an unversioned enumeration look reproducible.

**`Authority`** — defaults to the sentinel `UNRESOLVED`, distinct from `""`, so "nobody asked" and
"asked, and the answer was nobody" are different states in a record. The Ω-2 chain is
repository-specific; a bucket provider will have a different chain and a registry provider a
different one again. This model records the **answer and the rule**, and stays silent about how to
compute one.

**`Relationship`** — targets an **identifier**, not a path, which is what lets an edge cross a
provider boundary: a document in a bucket can describe a module in a git repository only if the edge
names something neither provider owns exclusively.

### Determinism is a construction, not a convention

`metadata` is normalised to sorted order and `relationships` are sorted on construction. Two
artifacts built from the same facts **in a different order are equal and serialise identically** —
the evidence document is compared byte-for-byte, and a dict ordering difference would break that for
a reason unrelated to discovery.

### Non-mutating derivation, one construction point

`with_type`, `with_authority`, `with_metadata`, `with_relationships` all route through `_replace`, so
no field is dropped by omission. `with_type` **requires** the rule: classifying without naming the
rule raises, because a type with no rule cannot be argued with.

### Type extensibility

`ArtifactType` is a value class, not an `Enum`. An enum member cannot be added at runtime, so an enum
would mean supporting a new artifact kind requires editing this file — the exact structural limit
Phase 1 removes.

| Initial type | Meaning |
|---|---|
| `PYTHON` | Executable Python source. A **type**, not a system assumption |
| `DOCUMENT` | Prose intended to be read |
| `CONFIGURATION` | Declarative settings, not executed directly |
| `WORKFLOW` | An orchestration definition |
| `DATASET` | Structured data consumed as input or emitted as evidence |
| `UNKNOWN` | No classifier could type it. A **named finding**, never an absence |

A seventh is `TYPES.declare_name("SCHEMA", "A structural contract.")`. Conflicting re-declaration is
refused; an unknown name raises rather than becoming a new type by spelling.

---

## 3. CLASSIFICATION (DELIVERABLE 4)

### The constraint, taken literally

> "Classification must be independent from file extension."

Independence is **not** achieved by deleting extension logic — a suffix is real evidence and
discarding it would make the layer worse. It is achieved by making the suffix the **weakest and
last** source of evidence, so that no classification *depends* on it.

### The pipeline

| # | Classifier | Rule | Evidence |
|---|---|---|---|
| 1 | `ProviderDeclaredClassifier` | `Ω∞-T-01` | The system of record already knows — an object store's content type, a registry's schema field, a graph node label. **Strongest**, and needs no bytes |
| 2 | `InterpreterClassifier` | `Ω∞-T-02` | A shebang names its interpreter. Travels with the bytes |
| 3 | `ContentProbeClassifier` | `Ω∞-T-03` | The bytes have a recognisable shape |
| 4 | `SuffixClassifier` | `Ω∞-T-04` | The locator's suffix. **Weakest** — a name is a claim by whoever typed it |
| 5 | terminal | `Ω∞-T-05` | `UNKNOWN`, **unconditional** |

**Order is the architecture.** Reversing those four lines would restore extension-primary
classification exactly, which is why the order is stated in one place (`default_pipeline`) and
asserted by `test_the_declared_pipeline_order_is_the_architecture`.

### The headline demonstrations

```python
# NO extension at all → PYTHON, from bytes. The suffix classifier is never consulted.
pipeline.apply(artifact("bin/ucos-report"), "#!/usr/bin/env python3\nX = 1\n")
#   → PYTHON, rule Ω∞-T-02

# A MISLEADING extension → content wins.
pipeline.apply(artifact("docs/thing.md"), "#!/usr/bin/python3.12\nX = 1\n")
#   → PYTHON, rule Ω∞-T-02
```

Renaming an artifact can only change its type when nothing stronger had an opinion. That is the
honest amount of authority a filename deserves.

### Abstaining is a first-class answer

`classify` returns `None` for "I have no evidence", which is **different** from "this is UNKNOWN".
Only the terminal rule may say `UNKNOWN`. A classifier that guessed instead of abstaining would
prevent every weaker classifier from ever being consulted.

### No giant rule table, no hard-coded language list

The module contains **no** mapping from suffixes to languages. The data lives in an injected
`TypeVocabulary`:

```python
@dataclass(frozen=True)
class TypeVocabulary:
    suffixes: dict[str, ArtifactType]
    interpreters: dict[str, ArtifactType]
```

`seed_vocabulary()` is deliberately tiny — 9 suffixes, 1 interpreter — and asserted small by
`test_the_seed_vocabulary_is_deliberately_minimal`. A hundred-entry table would be the giant rule
table the directive forbids, and would encode a language list that goes stale exactly the way
`SOURCE_TREES = ("engine", "platform")` did.

Adding a language touches no code in this module:

```python
rust = ArtifactType("RUST", "Rust source.")
vocabulary = seed_vocabulary().with_suffix(".rs", rust).with_interpreter("cargo", rust)
pipeline = default_pipeline(vocabulary)
```

A caller may also replace the vocabulary **wholesale** — `default_pipeline(only_rust)` types `a.py`
as `UNKNOWN`, proving no entry is privileged.

**One vocabulary, two access paths.** The suffix classifier and the interpreter probe read the *same*
`TypeVocabulary`. A hard-coded "shebang mentions python → PYTHON" branch would be a second language
list, disagreeing with the first the moment either changed. Interpreter matching ignores a trailing
version, so `python`, `python3` and `/usr/bin/python3.12` all resolve; `/usr/bin/env` is skipped.
Suffix matching takes the **longest** registered match, so `.tar.gz` can beat `.gz` later.

### Content probes are data

```python
ContentProbe = Callable[[str], ArtifactType | None]
```

Two generic probes ship: `structured_data_probe` (opens as a JSON object or array — a property of
the bytes, not of any format's naming) and `prose_probe` (opens with a markup heading). Recognising a
new format is a registration; **no branch in `ContentProbeClassifier` names a format**, which is what
keeps it from becoming the rule table.

Reading is bounded at `CONTENT_WINDOW = 4096`, **enforced in the classifier rather than by the
caller** — the same lesson `MARKER_WINDOW` records in UCOS-OMEGA-001: a bound enforced by the caller
is a bound some other caller will not enforce.

### Totality, and why `UNKNOWN` is a population

`classify` never returns `None` and never raises for an unrecognised artifact. It returns `UNKNOWN`
with `Ω∞-T-05`. That makes "we could not type this" a **countable population** instead of a silence,
which is the only form in which it can be reported and driven to zero:

```python
unknown_population(typed)   # the number Phase 2 is measured against
```

Same construction as Ω-5's dispositions, and for the same reason: an unclassified artifact is a
governance hole no measurement can see.

### Reading is injected

```python
pipeline.apply_all(artifacts, read=lambda a: provider.read(a.location.locator))
pipeline.apply_all(artifacts)    # no reader → no bytes fetched at all
```

A pipeline that read content itself could not run against a knowledge space whose bytes cost a
network call each — so **who** reads, and **whether** reading happens, is the caller's decision.

### Third-party classifiers need no dependency

`Classifier` is a `Protocol`, so a caller injects its own:

```python
ClassificationPipeline((MyClassifier(),))
```

---

## 4. TEST INDEX

| Property | Test |
|---|---|
| Model carries zero Python fields | `test_the_model_carries_no_language_specific_field` |
| All six directive parts present | `test_the_six_directive_parts_are_all_present` |
| Default type is UNKNOWN, not PYTHON | `test_an_unclassified_artifact_defaults_to_unknown_rather_than_to_python` |
| Provider is part of location identity | `test_the_provider_is_part_of_the_location_identity` |
| Absent revision omitted, not faked | `test_an_absent_revision_is_omitted_rather_than_faked` |
| Deterministic bytes regardless of build order | `test_metadata_and_relationships_are_normalised_for_deterministic_bytes` |
| A type always carries its rule | `test_with_type_requires_the_rule_that_produced_the_type` |
| Derived copies preserve every field | `test_the_derived_copies_preserve_every_other_field` |
| Seventh type is a registration | `test_a_seventh_type_is_a_registration_and_not_a_code_change` |
| **Suffixless artifact typed from bytes** | `test_a_suffixless_executable_is_typed_from_its_bytes` |
| **Content beats a misleading suffix** | `test_content_evidence_beats_a_misleading_suffix` |
| Provider declaration outranks inference | `test_a_provider_declaration_outranks_every_inference` |
| Pipeline order is the architecture | `test_the_declared_pipeline_order_is_the_architecture` |
| Classifiers abstain rather than guess | `test_each_classifier_abstains_when_it_has_no_evidence` |
| Totality: UNKNOWN with a rule | `test_an_artifact_nothing_recognises_becomes_a_named_unknown` |
| UNKNOWN is countable | `test_the_unknown_population_is_reportable` |
| Vocabulary extends without editing | `test_the_vocabulary_extends_without_editing_the_module` |
| Vocabulary replaceable wholesale | `test_a_caller_may_replace_the_vocabulary_wholesale` |
| Content read is bounded | `test_content_reading_is_bounded` |
| Reader is injected | `test_apply_all_injects_the_reader_so_a_remote_provider_may_decline_to_fetch` |
| Lift loses nothing | `test_a_legacy_artifact_lifts_into_the_universal_model_losing_nothing` |
