"""UCKP Layer Zero — Universal Persistence Abstraction (Article 9).

Article 9 requires that every persistence mechanism satisfy one identical
constitutional contract, so that replacing storage costs zero constitutional change.
The contract is deliberately tiny, because a large contract is one that only some
technologies can honour:

    1. ``write(objects)`` durably records the universe and returns a receipt.
    2. ``read()`` returns the same universe.
    3. The universe digest of what was read equals the universe digest of what was
       written — byte for byte, through the one canonical form.

That is all. Nothing about files, transactions, schemas, regions, indexes or query
languages appears in it, because those are properties of a mechanism and the law is
not about mechanisms.

Ten adapters are provided, spanning the technologies the mission names, and
:func:`verify_interchangeable` runs the identical contract against all of them and
compares digests. Interchangeability is therefore *measured on real round trips*
rather than asserted in prose.

One honest note on scope. ``git``, ``cloud`` and ``distributed-ledger`` are modelled
here on the local filesystem: the ledger really does chain hashes and the git adapter
really does keep an append-only content-addressed journal, but neither shells out to a
daemon or a remote service. What the code proves is that the *constitutional contract*
is technology-independent, which is the claim Article 9 makes. Proving that a
particular vendor's API honours it is integration work for that adapter, and the
contract is what such work would be measured against.
"""

from __future__ import annotations

import base64
import io
import json
import sqlite3
import tarfile
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from engine.uckp.canonical import canonical_json, content_hash
from engine.uckp.errors import PersistenceContractError
from engine.uckp.ucko import UCKO

#: The persistence technologies the mission names. Open by registration (Article 17).
MEMORY = "memory"
FILESYSTEM = "filesystem"
GIT = "git"
DATABASE = "database"
OBJECT_STORAGE = "object-storage"
KNOWLEDGE_GRAPH = "knowledge-graph"
DISTRIBUTED_LEDGER = "distributed-ledger"
CLOUD = "cloud"
OFFLINE_ARCHIVE = "offline-archive"
FUTURE_STORAGE = "future-storage"

KNOWN_PERSISTENCE_KINDS: tuple[str, ...] = (
    CLOUD,
    DATABASE,
    DISTRIBUTED_LEDGER,
    FILESYSTEM,
    FUTURE_STORAGE,
    GIT,
    KNOWLEDGE_GRAPH,
    MEMORY,
    OBJECT_STORAGE,
    OFFLINE_ARCHIVE,
)


def universe_digest(objects: Iterable[UCKO]) -> str:
    """The digest of a universe, independent of iteration order or storage layout."""
    return content_hash(
        sorted(
            ({"id": obj.ucko_id, "sha256": obj.content_sha256} for obj in objects),
            key=lambda item: item["id"],
        )
    )


@dataclass(frozen=True, slots=True)
class PersistenceReceipt:
    """Proof that a universe was recorded, and of what it consisted."""

    kind: str
    locator: str
    count: int
    digest: str

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "locator": self.locator,
            "count": self.count,
            "digest": self.digest,
        }


class PersistenceAdapter(ABC):
    """The one constitutional persistence contract every mechanism implements."""

    kind: str = ""

    @property
    @abstractmethod
    def locator(self) -> str:
        """Where this adapter keeps the universe. Advisory: never an identity."""

    @abstractmethod
    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        """Record the universe durably."""

    @abstractmethod
    def read(self) -> tuple[UCKO, ...]:
        """Return the recorded universe, sorted by identity."""

    def capabilities(self) -> frozenset[str]:
        """Mechanism-specific capabilities. Never consulted by the law."""
        return frozenset({"write", "read"})

    def describe(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "locator": self.locator,
            "capabilities": sorted(self.capabilities()),
            "authoritative": False,
        }

    def round_trip(self, objects: Sequence[UCKO]) -> tuple[UCKO, ...]:
        """Write then read. The whole contract in one call."""
        self.write(objects)
        return self.read()

    def verify_contract(self, objects: Sequence[UCKO]) -> None:
        """Fail closed unless this mechanism satisfies the constitutional contract."""
        expected = universe_digest(objects)
        restored = self.round_trip(objects)
        observed = universe_digest(restored)
        if observed != expected:
            raise PersistenceContractError(
                "persistence mechanism did not preserve the universe",
                kind=self.kind,
                expected=expected,
                observed=observed,
            )
        for original, recovered in zip(
            sorted(objects, key=lambda o: o.ucko_id), restored, strict=True
        ):
            recovered.require_integrity()
            if recovered != original:
                raise PersistenceContractError(
                    "persistence mechanism altered an object",
                    kind=self.kind,
                    ucko_id=original.ucko_id,
                )


def _decode(records: Iterable[object]) -> tuple[UCKO, ...]:
    restored = [UCKO.from_dict(record) for record in records]
    return tuple(sorted(restored, key=lambda obj: obj.ucko_id))


def _encode(objects: Sequence[UCKO]) -> list[dict[str, object]]:
    return [obj.to_dict() for obj in sorted(objects, key=lambda o: o.ucko_id)]


class MemoryPersistence(PersistenceAdapter):
    """The universe held in process memory. The simplest possible mechanism."""

    kind = MEMORY

    def __init__(self) -> None:
        self._records: list[dict[str, object]] = []

    @property
    def locator(self) -> str:
        return "memory://uckp"

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        self._records = _encode(objects)
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def read(self) -> tuple[UCKO, ...]:
        return _decode(self._records)


class FilesystemPersistence(PersistenceAdapter):
    """One canonical JSON file per object, under a directory."""

    kind = FILESYSTEM

    def __init__(self, base: str | Path) -> None:
        self._base = Path(base)

    @property
    def locator(self) -> str:
        return f"file://{self._base}"

    def _path(self, obj: UCKO) -> Path:
        return self._base / f"{obj.identity.uuid}.json"

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        self._base.mkdir(parents=True, exist_ok=True)
        for existing in sorted(self._base.glob("*.json")):
            existing.unlink()
        for obj in objects:
            self._path(obj).write_text(canonical_json(obj.to_dict()) + "\n", encoding="utf-8")
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def read(self) -> tuple[UCKO, ...]:
        if not self._base.exists():
            return ()
        records = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(self._base.glob("*.json"))
        ]
        return _decode(records)

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "per-object-addressing"})


class GitPersistence(PersistenceAdapter):
    """A content-addressed, append-only journal over a working tree.

    This is the shape of git that matters constitutionally — objects addressed by
    content and history that only grows — without depending on the git binary. The
    journal is never rewritten, so a prior recorded universe stays recoverable, which
    is the property Article 12 needs from any mechanism claiming to hold history.
    """

    kind = GIT

    def __init__(self, base: str | Path) -> None:
        self._base = Path(base)

    @property
    def locator(self) -> str:
        return f"git://{self._base}"

    @property
    def _objects_dir(self) -> Path:
        return self._base / "objects"

    @property
    def _journal(self) -> Path:
        return self._base / "journal.jsonl"

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        self._objects_dir.mkdir(parents=True, exist_ok=True)
        entries = []
        for obj in sorted(objects, key=lambda o: o.ucko_id):
            payload = canonical_json(obj.to_dict())
            blob = content_hash(payload)
            (self._objects_dir / f"{blob}.json").write_text(payload, encoding="utf-8")
            entries.append({"ucko_id": obj.ucko_id, "blob": blob})
        commit = {
            "commit": content_hash(entries),
            "parent": self._head(),
            "entries": entries,
        }
        with self._journal.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(commit) + "\n")
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def _head(self) -> str:
        commits = self.commits()
        return commits[-1]["commit"] if commits else ""

    def commits(self) -> tuple[dict[str, object], ...]:
        if not self._journal.exists():
            return ()
        lines = [
            line for line in self._journal.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        return tuple(json.loads(line) for line in lines)

    def read(self) -> tuple[UCKO, ...]:
        commits = self.commits()
        if not commits:
            return ()
        entries = commits[-1]["entries"]
        records = []
        for entry in entries:  # type: ignore[union-attr]
            blob = self._objects_dir / f"{entry['blob']}.json"
            records.append(json.loads(blob.read_text(encoding="utf-8")))
        return _decode(records)

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "history", "content-addressed"})


class DatabasePersistence(PersistenceAdapter):
    """A relational table of canonical records. Parameterised queries only."""

    kind = DATABASE

    def __init__(self, path: str | Path = ":memory:") -> None:
        self._path = str(path)
        self._connection = sqlite3.connect(self._path)
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS ucko (ucko_id TEXT PRIMARY KEY, record TEXT NOT NULL)"
        )
        self._connection.commit()

    @property
    def locator(self) -> str:
        return f"sqlite://{self._path}"

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        with self._connection:
            self._connection.execute("DELETE FROM ucko")
            self._connection.executemany(
                "INSERT INTO ucko (ucko_id, record) VALUES (?, ?)",
                [(obj.ucko_id, canonical_json(obj.to_dict())) for obj in objects],
            )
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def read(self) -> tuple[UCKO, ...]:
        rows = self._connection.execute("SELECT record FROM ucko ORDER BY ucko_id").fetchall()
        return _decode(json.loads(row[0]) for row in rows)

    def close(self) -> None:
        self._connection.close()

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "query", "transactional"})


class ObjectStoragePersistence(PersistenceAdapter):
    """Flat key/blob storage — the shape every object store shares."""

    kind = OBJECT_STORAGE

    def __init__(self, base: str | Path, bucket: str = "uckp") -> None:
        self._base = Path(base)
        self._bucket = bucket

    @property
    def locator(self) -> str:
        return f"s3-like://{self._bucket}/{self._base.name}"

    @property
    def _bucket_dir(self) -> Path:
        return self._base / self._bucket

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        self._bucket_dir.mkdir(parents=True, exist_ok=True)
        for existing in sorted(self._bucket_dir.glob("*.blob")):
            existing.unlink()
        for obj in objects:
            key = obj.identity.uuid
            (self._bucket_dir / f"{key}.blob").write_bytes(
                canonical_json(obj.to_dict()).encode("utf-8")
            )
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def read(self) -> tuple[UCKO, ...]:
        if not self._bucket_dir.exists():
            return ()
        records = [
            json.loads(path.read_bytes().decode("utf-8"))
            for path in sorted(self._bucket_dir.glob("*.blob"))
        ]
        return _decode(records)

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "flat-namespace"})


class KnowledgeGraphPersistence(PersistenceAdapter):
    """Node and edge tables. The universe stored as a graph rather than as records.

    The nodes hold the canonical records and the edges are re-derived on write, so the
    graph store carries no knowledge the objects do not already state (Article 3). The
    edge table is an index, and an index is a projection.
    """

    kind = KNOWLEDGE_GRAPH

    def __init__(self, base: str | Path) -> None:
        self._base = Path(base)

    @property
    def locator(self) -> str:
        return f"graph://{self._base}"

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        from engine.uckp.graph import UniversalKnowledgeGraph

        self._base.mkdir(parents=True, exist_ok=True)
        graph = UniversalKnowledgeGraph.from_objects(objects)
        (self._base / "nodes.json").write_text(
            canonical_json(_encode(objects)) + "\n", encoding="utf-8"
        )
        (self._base / "edges.json").write_text(
            canonical_json([edge.to_dict() for edge in graph.edges()]) + "\n",
            encoding="utf-8",
        )
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def read(self) -> tuple[UCKO, ...]:
        nodes = self._base / "nodes.json"
        if not nodes.exists():
            return ()
        return _decode(json.loads(nodes.read_text(encoding="utf-8")))

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "traversal"})


class DistributedLedgerPersistence(PersistenceAdapter):
    """An append-only hash chain. Tamper-evident by construction."""

    kind = DISTRIBUTED_LEDGER

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    @property
    def locator(self) -> str:
        return f"ledger://{self._path}"

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        previous = self.head()
        block = {
            "previous": previous,
            "records": _encode(objects),
        }
        block["block"] = content_hash(block)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(block) + "\n")
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def blocks(self) -> tuple[dict[str, object], ...]:
        if not self._path.exists():
            return ()
        return tuple(
            json.loads(line)
            for line in self._path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )

    def head(self) -> str:
        blocks = self.blocks()
        return str(blocks[-1]["block"]) if blocks else ""

    def verify_chain(self) -> bool:
        """True iff every block still hashes to its recorded identity and links back."""
        previous = ""
        for block in self.blocks():
            recorded = dict(block)
            claimed = recorded.pop("block")
            if recorded.get("previous") != previous:
                return False
            if content_hash(recorded) != claimed:
                return False
            previous = str(claimed)
        return True

    def read(self) -> tuple[UCKO, ...]:
        blocks = self.blocks()
        if not blocks:
            return ()
        return _decode(blocks[-1]["records"])  # type: ignore[arg-type]

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "append-only", "tamper-evident"})


class CloudPersistence(PersistenceAdapter):
    """Region-partitioned object storage — the shape of a managed cloud store.

    ``region`` is supplied by the caller and never defaulted. It previously carried
    a single-planet default, which made a planet an architectural assumption baked
    into a signature rather than data the caller provides (ADR-0012, UCKP-ART-20:
    the law remains valid across planetary locations and civilizations). A caller
    that knows where it is says so; a caller that does not know asserts no location
    at all and the store is unpartitioned, which is the honest reading of absence.
    A region may name any locality — orbital, lunar, interplanetary or a locality
    of a kind not yet described — because nothing here interprets the string.
    """

    kind = CLOUD

    def __init__(self, base: str | Path, region: str | None = None) -> None:
        self._base = Path(base)
        self._region = region

    @property
    def region(self) -> str | None:
        """The locality the caller supplied, or ``None`` when none was asserted."""
        return self._region

    @property
    def locator(self) -> str:
        if self._region is None:
            return f"cloud://{self._base.name}"
        return f"cloud://{self._region}/{self._base.name}"

    @property
    def _region_dir(self) -> Path:
        if self._region is None:
            return self._base
        return self._base / self._region

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        self._region_dir.mkdir(parents=True, exist_ok=True)
        (self._region_dir / "universe.json").write_text(
            canonical_json(_encode(objects)) + "\n", encoding="utf-8"
        )
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def read(self) -> tuple[UCKO, ...]:
        payload = self._region_dir / "universe.json"
        if not payload.exists():
            return ()
        return _decode(json.loads(payload.read_text(encoding="utf-8")))

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "regional", "managed"})


class OfflineArchivePersistence(PersistenceAdapter):
    """A sealed archive, readable with no service running at all.

    This adapter is the answer to the question Article 20 raises: if every system that
    understands UCOS is gone, can the universe still be recovered? A compressed archive
    of canonical JSON is recoverable by any future reader that can decompress and parse,
    which is a far weaker requirement than running this code.
    """

    kind = OFFLINE_ARCHIVE

    _MEMBER = "universe.json"

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    @property
    def locator(self) -> str:
        return f"archive://{self._path}"

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = (canonical_json(_encode(objects)) + "\n").encode("utf-8")
        with tarfile.open(self._path, "w:gz") as archive:
            info = tarfile.TarInfo(self._MEMBER)
            info.size = len(payload)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(payload))
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def read(self) -> tuple[UCKO, ...]:
        if not self._path.exists():
            return ()
        with tarfile.open(self._path, "r:gz") as archive:
            member = archive.extractfile(self._MEMBER)
            if member is None:
                return ()
            return _decode(json.loads(member.read().decode("utf-8")))

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "offline", "sealed"})


class FutureStoragePersistence(PersistenceAdapter):
    """A mechanism whose encoding Layer Zero does not understand.

    Article 17 requires the universe to admit a storage technology nobody has invented.
    This adapter stands in for one: it stores through an opaque codec Layer Zero treats
    as a black box, and it satisfies the identical contract regardless. If the contract
    depended on knowing the encoding, the abstraction would be a leak and Article 9
    would be false for every future mechanism.
    """

    kind = FUTURE_STORAGE

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    @property
    def locator(self) -> str:
        return f"future://{self._path}"

    def write(self, objects: Sequence[UCKO]) -> PersistenceReceipt:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        opaque = base64.b85encode(canonical_json(_encode(objects)).encode("utf-8"))
        self._path.write_bytes(opaque)
        return PersistenceReceipt(self.kind, self.locator, len(objects), universe_digest(objects))

    def read(self) -> tuple[UCKO, ...]:
        if not self._path.exists():
            return ()
        payload = base64.b85decode(self._path.read_bytes()).decode("utf-8")
        return _decode(json.loads(payload))

    def capabilities(self) -> frozenset[str]:
        return frozenset({"write", "read", "opaque-codec"})


@dataclass(frozen=True, slots=True)
class InterchangeabilityReport:
    """Whether a set of mechanisms are genuinely substitutable for one another."""

    expected_digest: str
    observed: tuple[tuple[str, str], ...]
    failures: tuple[str, ...] = ()

    @property
    def interchangeable(self) -> bool:
        return not self.failures and all(
            digest == self.expected_digest for _, digest in self.observed
        )

    def kinds(self) -> tuple[str, ...]:
        return tuple(kind for kind, _ in self.observed)

    def to_dict(self) -> dict[str, object]:
        return {
            "expected_digest": self.expected_digest,
            "observed": [{"kind": kind, "digest": digest} for kind, digest in self.observed],
            "failures": list(self.failures),
            "interchangeable": self.interchangeable,
        }


def verify_interchangeable(
    adapters: Sequence[PersistenceAdapter], objects: Sequence[UCKO]
) -> InterchangeabilityReport:
    """Round-trip the universe through every mechanism and compare digests (Article 9)."""
    expected = universe_digest(objects)
    observed: list[tuple[str, str]] = []
    failures: list[str] = []
    for adapter in adapters:
        try:
            restored = adapter.round_trip(objects)
        except Exception as exc:  # noqa: BLE001 - reported, never silent
            failures.append(f"{adapter.kind}: {exc}")
            continue
        observed.append((adapter.kind, universe_digest(restored)))
    return InterchangeabilityReport(
        expected_digest=expected,
        observed=tuple(sorted(observed)),
        failures=tuple(sorted(failures)),
    )


def build_persistence_suite(
    base: str | Path, *, cloud_region: str | None = None
) -> tuple[PersistenceAdapter, ...]:
    """Every mechanism Layer Zero ships, rooted under ``base``.

    ``base`` is created if it does not exist. Without this, constructing the suite
    over a fresh path raised whichever native error the first path-bound adapter
    happened to produce — an ``sqlite3.OperationalError`` from the database adapter —
    which lets a technology-specific failure escape the abstraction whose entire
    purpose is that no caller needs to know which technologies are inside it
    (Article 9).

    ``cloud_region`` is the seam through which a caller that knows its locality
    supplies it. It is not defaulted to any locality: a suite built without one
    asserts no location rather than assuming a planet (ADR-0012).
    """
    root = Path(base)
    root.mkdir(parents=True, exist_ok=True)
    return (
        MemoryPersistence(),
        FilesystemPersistence(root / "filesystem"),
        GitPersistence(root / "git"),
        DatabasePersistence(root / "database.sqlite3"),
        ObjectStoragePersistence(root / "object-storage"),
        KnowledgeGraphPersistence(root / "knowledge-graph"),
        DistributedLedgerPersistence(root / "ledger" / "chain.jsonl"),
        CloudPersistence(root / "cloud", cloud_region),
        OfflineArchivePersistence(root / "archive" / "universe.tar.gz"),
        FutureStoragePersistence(root / "future" / "universe.opaque"),
    )


__all__ = [
    "CLOUD",
    "DATABASE",
    "DISTRIBUTED_LEDGER",
    "FILESYSTEM",
    "FUTURE_STORAGE",
    "GIT",
    "KNOWLEDGE_GRAPH",
    "KNOWN_PERSISTENCE_KINDS",
    "MEMORY",
    "OBJECT_STORAGE",
    "OFFLINE_ARCHIVE",
    "CloudPersistence",
    "DatabasePersistence",
    "DistributedLedgerPersistence",
    "FilesystemPersistence",
    "FutureStoragePersistence",
    "GitPersistence",
    "InterchangeabilityReport",
    "KnowledgeGraphPersistence",
    "MemoryPersistence",
    "ObjectStoragePersistence",
    "OfflineArchivePersistence",
    "PersistenceAdapter",
    "PersistenceReceipt",
    "build_persistence_suite",
    "universe_digest",
    "verify_interchangeable",
]
