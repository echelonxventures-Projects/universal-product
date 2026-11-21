# UCOS Ω∞ — PHASE 1 KNOWLEDGE SPACE MODEL
## Deliverable 5 — a repository root is one kind of space, and no longer the only one

**AUTHORITY = NONE (DERIVED TRUTH).**

---

## 1. THE ASSUMPTION WAS A FUNCTION SIGNATURE

```python
def build(root: str = ".") -> OmegaSurface
def evaluate(root: str = ".") -> Verdict
def derived_scope(root: str) -> tuple[...]
```

One string, carrying **three unstated commitments at once**:

1. it is a filesystem path,
2. it is a git repository,
3. it is the whole world.

A bucket is not a path. A registry has no root. A federation has several. **So the signature itself
is the limit** — not any decision inside those functions. No amount of care within `build` could
have made it describe a bucket, because its only parameter cannot denote one.

---

## 2. WHAT A KNOWLEDGE SPACE IS

> The bounded world a measurement is made over, **plus** the providers that can enumerate it,
> **plus** what those providers declare they can do.

It answers *"what is in scope, and by what mechanism do we know?"* — which is exactly the pair that
`root: str` conflated into one word.

```python
@runtime_checkable
class KnowledgeSpace(Protocol):
    def identifier(self) -> str: ...
    def kind(self) -> SpaceKind: ...
    def registry(self) -> ProviderRegistry: ...
    def discover(self, selector: Selector | None = None) -> SpacePopulation: ...
```

---

## 3. THE SIX KINDS, AND HOW EACH ARRIVES

| Kind | Status | Mechanism |
|---|---|---|
| `REPOSITORY` | **implemented** | Version-controlled content; requires a `TRACKED_CONTENT` provider |
| `FILESYSTEM` | **implemented** | Direct storage; no version control anywhere in the path |
| `BUCKET` | registration | A provider declaring `REMOTE_STORAGE`, registered into a space of this kind |
| `REGISTRY` | registration | A provider whose locators are names in a catalogue rather than paths |
| `FEDERATION` | registration | A space holding **several** providers. The seam is already open — see §5 |
| `GRAPH` | registration | A provider whose artifacts carry `relationships`, which the universal `Artifact` already models for exactly this reason |

Only two are implemented, because Phase 1's goal is to **remove the structural limit**, not to
support every platform. The test of success is that the four unimplemented kinds require
**registration, not restructuring** — which is why each is named above with the mechanism it would
use rather than left as a gesture at future work.

`SpaceKind` is a value class. **Nothing quantifies over `KINDS`** — no dispatch, no validation, no
branch. A space kind absent from that tuple works identically, which is the property that makes the
list safe to be incomplete.

---

## 4. RESOLUTION — THE REPLACEMENT FOR `root: str`

```python
def resolve_space(root: str, identifier: str = "") -> KnowledgeSpace:
    if git_provider.available(root):
        return repository_space(root, identifier)
    return filesystem_space(root, identifier)
```

**Probes rather than assumes**, and the order is by **strength of guarantee**: a version-controlled
space carries an eligibility boundary a filesystem space cannot, so it is preferred when available.

A directory that has never been a repository **still resolves** — to a `FILESYSTEM` space with
`TRACKED_CONTENT` undeclared. That is the Deliverable 2 success criterion reached through
Deliverable 5.

### The eligibility boundary is now an assertion, not a side effect

```python
class RepositoryKnowledgeSpace(BaseKnowledgeSpace):
    space_kind = REPOSITORY

    def __init__(self, identifier: str, registry: ProviderRegistry) -> None:
        super().__init__(identifier, registry)
        self.require(TRACKED_CONTENT)     # ← refused at CONSTRUCTION
```

Constructing a repository space over a provider that enumerates the working copy is refused
**loudly, at the point of construction**, rather than silently at verdict time. In Ω-1 the boundary
was an unstated consequence of calling `git ls-files`; here it is a capability requirement that can
fail with a message.

Symmetrically, `FilesystemKnowledgeSpace` declares **no guarantee it does not have**. A measurement
needing the boundary is refused there — correctly, and with a message naming the space. That is the
difference between an abstraction and a pretence.

---

## 5. UNION VERSUS INTERSECTION — THE FEDERATION-CRITICAL DISTINCTION

```python
space.capabilities()   # UNION:        what this space can do by SOME mechanism
space.guarantees()     # INTERSECTION: what holds for EVERY artifact, whichever provider found it
space.require(cap)     # checks GUARANTEES, never the union
```

A space unioning a tracked and an untracked provider can offer `LOCAL_STORAGE` for everything but
`TRACKED_CONTENT` for only *part* of the population. A measurement whose correctness depends on the
eligibility boundary must consult `guarantees()`.

Getting this wrong is how a federated population silently claims a property only some of its members
have. Verified by
`test_union_is_what_the_space_can_do_and_intersection_is_what_holds_for_everything`.

---

## 6. THE FEDERATION SEAM IS ALREADY OPEN

`BaseKnowledgeSpace` takes a **`ProviderRegistry`, not a provider**. That single decision is what
makes `FEDERATION` a registration:

```python
def discover(self, selector=None) -> SpacePopulation:
    merged: dict[str, Artifact] = {}
    for provider in self._registry.providers():
        for artifact in provider.enumerate(chosen):
            merged.setdefault(artifact.identifier, artifact)
    ...
```

`discover` **already** merges across every provider, deduplicates on `Artifact.identifier`, and
reports every contributing provider. A space with one provider and a space with nine differ only in
what was registered — so federation needs a subclass that registers more providers, **not a redesign
of this file**.

Deduplication on the identifier is why `Location` carries the provider (see
`PHASE1_ARTIFACT_MODEL.md` §2): two providers handing back the locator `config.toml` produce
*different* identifiers and are not merged.

---

## 7. POPULATIONS CARRY PROVENANCE

```python
@dataclass(frozen=True)
class SpacePopulation:
    space: str
    kind: SpaceKind
    artifacts: tuple[Artifact, ...]
    providers: tuple[str, ...]
    selector: Selector
    capabilities: CapabilitySet
```

**Why provenance is not optional.** The repository already computed four independent populations —
a coverage scope, an executable surface, a governed surface and a discovery surface — and *no code
had ever asked whether they agreed*. A file could sit in exactly one of them indefinitely, and 619
did.

A population that does not carry the space, the providers and the selector that produced it **cannot
be compared** with another population. So `SpacePopulation` carries all three, and
`by_type()` / `as_record()` make it reportable.

---

## 8. UNLIMITED EXPANSION, DEMONSTRATED

```python
def space_of(identifier: str, kind: SpaceKind,
             providers: Iterable[DiscoveryProvider]) -> BaseKnowledgeSpace
```

A bucket space is:

```python
space_of("s3://ucos-evidence", BUCKET, [S3Provider(...)])
```

**No subclass. No edit to `knowledge_space.py`. No new branch anywhere in the package.**

> If supporting object storage required changing that file, the abstraction would not have removed
> the limit — it would have moved it.

`test_a_space_of_a_kind_this_package_does_not_implement_needs_no_edit` builds a space of kind
`BUCKET_V2` (asserted **absent** from `KINDS`) over a provider declaring `REMOTE_STORAGE`, discovers
its population, and confirms the result satisfies the `KnowledgeSpace` Protocol.

`evidence.expansion_probe` goes further and is the Ω∞-5 criterion: at runtime it registers

- a capability absent from `capability.WELL_KNOWN` (`STREAMING_CONTENT`),
- an artifact type absent from `artifact.INITIAL_TYPES` (`TELEMETRY_STREAM`),
- a space kind absent from `knowledge_space.KINDS` (`STREAM`),
- a provider for a storage model this package does not implement,

then enumerates and classifies the population correctly — with zero edits to `engine/omega_infinite/`.
It uses private registry instances so running the evidence does not mutate global vocabulary as a
side effect, and it is idempotent across runs.

---

## 9. RESOLUTION HELPERS

| Function | Purpose |
|---|---|
| `resolve_space(root)` | The strongest space `root` can honestly support |
| `repository_space(root)` | Refuses when no version control provider can serve it |
| `filesystem_space(root)` | Works where no version control exists at all |
| `space_of(id, kind, providers)` | Any kind, any providers — the registration path for kinds 3–6 |
| `strongest_provider(space, *caps)` | Resolution **by capability**, never by name |

---

## 10. TEST INDEX

| Property | Test |
|---|---|
| A repository root resolves to a REPOSITORY space | `test_a_repository_root_resolves_to_a_repository_space` |
| **A non-repository still resolves** | `test_a_directory_that_never_was_a_repository_still_resolves` |
| Resolution prefers the stronger guarantee | `test_resolution_prefers_the_stronger_guarantee` |
| A non-repository cannot be declared REPOSITORY | `test_a_non_repository_cannot_be_declared_a_repository_space` |
| Eligibility boundary refused at construction | `test_a_repository_space_refuses_a_provider_without_the_eligibility_boundary` |
| Filesystem space declares no guarantee it lacks | `test_a_filesystem_space_declares_no_guarantee_it_lacks` |
| Union vs intersection | `test_union_is_what_the_space_can_do_and_intersection_is_what_holds_for_everything` |
| Populations carry provenance | `test_discovery_carries_the_provenance_needed_to_compare_populations` |
| Merge + dedup across providers | `test_a_space_merges_and_deduplicates_across_providers` |
| **A kind this package does not implement needs no edit** | `test_a_space_of_a_kind_this_package_does_not_implement_needs_no_edit` |
| Nothing quantifies over KINDS | `test_the_six_named_kinds_exist_but_nothing_quantifies_over_them` |
| Empty registry refused | `test_a_space_needs_an_identifier_and_at_least_one_provider` |
| Space self-describes, both capability views | `test_a_space_describes_itself_including_both_capability_views` |
| Capability resolution inside a space | `test_the_strongest_provider_is_resolved_by_capability` |
