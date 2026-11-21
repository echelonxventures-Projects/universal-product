# UCOS Ω∞ — PHASE 1 PROVIDER MODEL
## Deliverables 1, 2 and 6 — the contract, the implementations, the self-description

**AUTHORITY = NONE (DERIVED TRUTH).**

---

## 1. THE ASSUMPTION, QUOTED FROM THE CODE THAT HELD IT

```python
# engine/universal_discovery/discovery.py
subprocess.run(
    ["git", "ls-files", "-z", "--cached", "--exclude-standard", "*.py"],
    cwd=root, capture_output=True, check=True,
)
```

That line is the entire discovery mechanism of UCOS. It is correct, it is deliberate, and it is a
hard architectural limit: **there is no seam at which a different enumeration could be
substituted.** "UCOS governs a git repository of Python" was not a configuration of the system — it
*was* the system.

Two further consequences, both invisible until named:

- **The filter is fused to the mechanism.** `'*.py'` is a string literal inside the only
  enumeration there is. Changing the population meant editing an argv list.
- **Availability cannot be asked.** `tracked_python` *raises* when git is absent, because it has no
  notion of a provider being unavailable. There is nothing else it could do, so there is no
  fallback path anywhere in the system.

---

## 2. THE CONTRACT (DELIVERABLE 1)

```python
@runtime_checkable
class DiscoveryProvider(Protocol):
    def identifier(self) -> str: ...
    def enumerate(self, selector: Selector | None = None) -> tuple[Artifact, ...]: ...
    def metadata(self) -> ProviderMetadata: ...
    def capabilities(self) -> CapabilitySet: ...
```

Four questions. **The fourth is what makes the other three safe** — see §4.

### Why a `Protocol` and not an ABC

A third-party provider must need **no dependency on this package's classes**. `BaseProvider` exists
and provides the plumbing every provider would otherwise duplicate, but it is strictly optional.

Verified: `test_provider.py::test_a_protocol_only_provider_appears_in_evidence_without_inheriting_baseprovider`
registers a class that inherits nothing, and it resolves, enumerates and appears in the capability
matrix. `ProviderRegistry._report_of` prefers a provider's own `report()` and falls back to the
contract's four questions, so the registry never requires more than the Protocol.

### `enumerate()` — what a provider answers

A provider answers exactly one question: **"what is here?"** It does *not* classify (D4 does), does
*not* derive authority, and does *not* decide what a knowledge space is (D5 does). A provider that
typed its own artifacts would be a second classification path disagreeing with the first.

### `Selector` — the relocated filter

```python
@dataclass(frozen=True)
class Selector:
    patterns: tuple[str, ...] = ()      # EMPTY MEANS EVERYTHING
    limit: int | None = None
```

Ω-1's hard-coded `'*.py'` is now `compat.PYTHON_ONLY = Selector(patterns=("*.py",))` — a value with
a name, a docstring and a test. **The honest default is no filter at all**, so a provider's answer to
"what is here?" is the whole population and narrowing it is an explicit act by the caller.

Patterns are matched against the **locator** with `fnmatch` — a string operation, not a filesystem
one — so the same selector works against object keys and graph node names.

```python
space.discover(Selector(patterns=("*.md",))).locators()   # ('docs/guide.md',)
space.discover(compat.PYTHON_ONLY).locators()             # ('src/module.py', 'src/nested/deep.py')
```

In Ω-1 that required editing an argv list.

### Determinism is enforced once, centrally

`BaseProvider.enumerate` sorts and deduplicates on `Artifact.identifier` for **every** provider,
because `git ls-files` returns sorted output and `os.walk` does not. A population whose order
depended on which provider produced it would make two evidence documents differ for no governed
reason.

---

## 3. THE REGISTRY AND RESOLUTION (DELIVERABLE 1)

### Resolution is by capability, never by name

```python
registry.resolve_capable(TRACKED_CONTENT)   # what a MEASUREMENT calls
registry.resolve("git")                     # evidence and tests ONLY
```

If a measurement had to say `"git"`, the assumption would simply have moved one layer up. That is
the smuggling Rule Ω-1 forbids.

### Refusals name every provider considered and its gap

```
no registered provider declares REMOTE_STORAGE; considered
  git (missing REMOTE_STORAGE); filesystem (missing REMOTE_STORAGE)
```

"No provider supports X" is a far less useful sentence. `Resolution` carries the `rejected` list on
purpose.

### Registry invariants

| Invariant | Why |
|---|---|
| Duplicate identifier → **refused**, never replaced | Silent replacement makes the population depend on **import order** — the class of defect that cannot be reproduced from a diff |
| Empty identifier → refused | A provider that cannot be named cannot appear in evidence |
| Resolution over an empty registry → **raises** | Returning `None` would let a caller measure an empty population and report a pass; an empty population satisfies every invariant |
| Order is `(-priority, identifier)` | Total and reproducible; ties do not depend on registration order |

`priority` is a **number, not a branch**, so a future provider with stronger guarantees outranks git
without an edit anywhere.

### Capability reporting

```python
registry.capability_matrix()
# {'git': ['AUTHORITY_METADATA', 'CONTENT_HASHING', 'LOCAL_STORAGE',
#          'TRACKED_CONTENT', 'VERSIONED_CONTENT']}
```

---

## 4. CAPABILITY DECLARATION (DELIVERABLE 6)

### The defect this closes

`tracked_python` requires git. **Nothing says so. Nothing can ask.** An assumption that cannot be
interrogated cannot be replaced.

### Open vocabulary, canonical spellings

`Capability` is a value class, not an `Enum`. The six well-known capabilities are a *convenience*:

| Capability | Means |
|---|---|
| `TRACKED_CONTENT` | Only content an index admits is enumerated, so untracked debris cannot change a verdict |
| `VERSIONED_CONTENT` | A revision can be named, so an enumeration is reproducible against history |
| `LOCAL_STORAGE` | Bytes readable with no network call |
| `REMOTE_STORAGE` | Bytes behind a network boundary — cost and failure modes are *not* a filesystem's |
| `CONTENT_HASHING` | A stable digest is obtainable without the caller reading bytes |
| `AUTHORITY_METADATA` | The provider holds ownership information of its own |

`CapabilityRegistry` canonicalises: a name registers once with a description; a conflicting
re-declaration is **refused**, because one name with two meanings makes every requirement on it
unenforceable. `resolve()` raises on an unknown name — the anti-typo boundary, so
`require(resolve("CONTENT_HASHNG"))` cannot pass vacuously forever.

Extending the vocabulary is a registration:
`registry.declare_name("QUANTUM_ENTANGLED_STORAGE", "...")`.

### A capability is a promise about what can be *asked*

Not about what has already been paid for. `GitDiscoveryProvider` declares `AUTHORITY_METADATA` and
supplies it via `authority_metadata(locator)` **on demand, never during enumeration** — one
`git log` per artifact would make enumerating a large repository cost thousands of subprocesses.

### Every capability-dependent method asks first

```python
def content_hash(self, locator: str) -> str:
    self.require(CONTENT_HASHING)
    ...
```

`require` is called even where the class declares the capability unconditionally. That is not
ceremony: it is the pattern every such method must follow, and a method that skipped it would be the
template someone copies. Verified by
`test_providers_concrete.py::test_a_capability_gated_method_asks_before_acting`, which subclasses the
git provider with a stripped declaration and observes both methods refuse.

---

## 5. THE TWO PROVIDERS (DELIVERABLE 2)

### `GitDiscoveryProvider` — priority 100

Git is still how *this repository* is discovered, and no longer how *UCOS* discovers. The sentence
"UCOS requires git" became "this provider requires git, **and says so**".

It remains the **preferred** provider here, and the demotion is not a downgrade. Version control is
an **eligibility boundary**, which is a real governance property:
`platform/tests/test_coverage_scope.py` records the measurement — a control that enumerates the
working copy decides differently on a developer's machine than on a clean checkout, and a control
whose verdict depends on local debris gets suppressed. So the provider declares `TRACKED_CONTENT`
and carries `priority = 100`, and capability resolution prefers it **with no call site naming it**.

| Method | Notes |
|---|---|
| `revision()` | `""` in a repository with no commits. **Empty is honest** — inventing an identifier would make an unreproducible enumeration look reproducible |
| `content_hash()` | The index's own object id (40 chars) |
| `authority_metadata()` | Last author name/email, on demand |
| `available(root)` | **The question Ω-1 cannot ask.** Returns `False` instead of raising, which is what creates a fallback path |

One subprocess call site (`_run`), fixed argv, never a shell, caller data never spliced into a
command string.

### `FilesystemDiscoveryProvider` — priority 10

**The deliverable, stated as the test that proves it:** works without git, hg, svn or p4.
`test_discovery_works_with_no_version_control_of_any_kind` enumerates a tree that has never been a
repository — no `.git`, no index, no VCS binary consulted — and gets a population. The
`untracked_tree` fixture deliberately never runs `git init`, and never will; a fixture that quietly
initialised a repository would make the requirement untestable while appearing to test it.

**What it honestly cannot do, and declaring it is the whole value of D6:**

| Not declared | Because |
|---|---|
| `TRACKED_CONTENT` | It enumerates whatever is on disk, so local debris **is** in the population. Asserted by `test_untracked_debris_is_visible_to_the_filesystem_provider` so it is not a surprise |
| `VERSIONED_CONTENT` | A filesystem has no revision. `revision` stays `""` rather than being filled with an mtime |
| `AUTHORITY_METADATA` | A POSIX owner is not an authority. `uid 501` answers "which account wrote this", never "which programme owns it" |

**Exclusions are injected, not hard-coded.** A walk meets `.git`, `__pycache__`, virtualenvs and
caches, and enumerating them would drown the population — but a fixed noise list inside the module
would be the `SOURCE_TREES` defect again. `DEFAULT_EXCLUSIONS` is a constructor default any caller
may replace wholesale, and `metadata()` reports the exclusions **actually in force**, so a
population is always explainable without reading the module.

**Two bounds, both tested:** `MAX_DEPTH = 64` so a symlink cycle terminates instead of hanging a
gate, and `follow_symlinks = False` by default because a followed symlink can leave the knowledge
space entirely.

### The comparison — Deliverable 6's payoff

```
git         AUTHORITY_METADATA  CONTENT_HASHING  LOCAL_STORAGE  TRACKED_CONTENT  VERSIONED_CONTENT
filesystem                      CONTENT_HASHING  LOCAL_STORAGE

gap = ('AUTHORITY_METADATA', 'TRACKED_CONTENT', 'VERSIONED_CONTENT')
```

Computed, not narrated — `test_the_two_providers_differ_only_in_what_they_declare`.

### Hashes are not comparable across providers

Git reports a blob id over a prefixed payload; the filesystem provider reports a plain sha256. Two
providers hashing the same bytes to different values is **expected**. Treating a digest as globally
comparable is the defect, and including the provider in `Location` is what prevents it.

---

## 6. ADDING A PROVIDER

Nothing enumerates provider kinds, so a new provider is registered rather than integrated:

1. Implement the four Protocol methods (inheriting `BaseProvider` is optional).
2. Declare capabilities — including any this package has never named, via
   `CapabilityRegistry.declare_name`.
3. Register into a `ProviderRegistry`.

No edit to `provider.py`, no new branch, no subclass of anything mandatory. Demonstrated at runtime
by `evidence.expansion_probe`, which registers a provider for a storage model this package does not
implement, declaring a capability absent from `WELL_KNOWN`, and enumerates and classifies its
population correctly.

---

## 7. TEST INDEX

| Property | Test |
|---|---|
| Discovery with no VCS at all | `test_discovery_works_with_no_version_control_of_any_kind` |
| Eligibility boundary applied by git | `test_the_git_provider_applies_the_eligibility_boundary` |
| Filter is an argument, not a literal | `test_the_selector_replaces_the_hard_coded_python_query` |
| Availability answers instead of raising | `test_git_availability_answers_rather_than_raising` |
| Capability gap is computable | `test_the_two_providers_differ_only_in_what_they_declare` |
| Undeclared capability refuses, naming subject and gap | `test_require_refuses_and_names_the_subject_and_the_gap` |
| Capability-gated methods ask first | `test_a_capability_gated_method_asks_before_acting` |
| Resolution never names a provider | `test_resolution_by_capability_prefers_the_strongest_provider` |
| Duplicate registration refused | `test_a_duplicate_identifier_is_refused_rather_than_replacing_silently` |
| Empty resolution raises | `test_resolution_over_an_empty_registry_refuses_rather_than_returning_nothing` |
| Protocol-only provider works | `test_a_protocol_only_provider_appears_in_evidence_without_inheriting_baseprovider` |
| Enumeration deterministic for all providers | `test_enumeration_is_sorted_and_deduplicated_for_every_provider_uniformly` |
| Depth bound enforced | `test_the_walk_is_depth_bounded_so_a_pathological_tree_terminates` |
| Symlinks not followed by default | `test_symlinks_are_not_followed_by_default` |
