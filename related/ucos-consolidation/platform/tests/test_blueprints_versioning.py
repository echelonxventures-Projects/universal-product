"""EC2-TASK-000101 — Blueprint versioning tests (EC2-EPIC-006, P5/P18).

Covers content-addressed immutable versions, append-only lineage, parent references,
supersession by reference (never mutation), and determinism.
"""

from __future__ import annotations

from platform.blueprints.errors import BlueprintVersionError
from platform.blueprints.metadata import BlueprintMetadata
from platform.blueprints.versioning import BlueprintVersion, VersionLineage, content_hash_of

import pytest


def test_version_create_is_content_addressed_and_deterministic():
    a = BlueprintVersion.create(blueprint_id="UCOS-BLPR-1", revision=1, content_hash="h1")
    b = BlueprintVersion.create(blueprint_id="UCOS-BLPR-1", revision=1, content_hash="h1")
    assert a.version_id == b.version_id
    assert a.version_id.startswith("UCOS-BVER-")
    assert a.is_root is True
    assert a.is_current is True


@pytest.mark.parametrize(
    "kwargs",
    [
        {"blueprint_id": ""},
        {"revision": 0},
        {"revision": True},
        {"content_hash": ""},
    ],
)
def test_version_rejects_malformed(kwargs):
    base = {"blueprint_id": "UCOS-BLPR-1", "revision": 1, "content_hash": "h1"}
    base.update(kwargs)
    with pytest.raises(BlueprintVersionError):
        BlueprintVersion.create(**base)


def test_root_must_have_no_parent_and_nonroot_must_have_parent():
    with pytest.raises(BlueprintVersionError):
        BlueprintVersion.create(
            blueprint_id="b", revision=1, content_hash="h", parent_version_id="p"
        )
    with pytest.raises(BlueprintVersionError):
        BlueprintVersion.create(blueprint_id="b", revision=2, content_hash="h")
    with pytest.raises(BlueprintVersionError):
        BlueprintVersion.create(
            blueprint_id="b", revision=2, content_hash="h", parent_version_id=""
        )
    with pytest.raises(BlueprintVersionError):
        BlueprintVersion.create(
            blueprint_id="b",
            revision=1,
            content_hash="h",
            metadata="x",  # type: ignore[arg-type]
        )


def test_supersession_is_immutable_copy():
    v = BlueprintVersion.create(blueprint_id="b", revision=1, content_hash="h")
    superseded = v.superseded("UCOS-BVER-next")
    assert superseded.superseded_by == "UCOS-BVER-next"
    assert superseded.is_current is False
    assert v.is_current is True  # original unchanged
    with pytest.raises(BlueprintVersionError):
        v.superseded("")
    with pytest.raises(BlueprintVersionError):
        v.superseded(v.version_id)  # cannot supersede itself


def test_version_serialisation_and_hash_helper():
    v = BlueprintVersion.create(blueprint_id="b", revision=1, content_hash="h")
    assert v.to_dict()["revision"] == 1
    assert len(content_hash_of({"x": 1})) == 16
    assert isinstance(v.fingerprint(), str)


# --------------------------------------------------------------------------- #
# Lineage                                                                      #
# --------------------------------------------------------------------------- #


def test_lineage_appends_and_supersedes_prior_head():
    lineage = VersionLineage("UCOS-BLPR-1")
    assert len(lineage) == 0
    v1 = lineage.append("h1")
    v2 = lineage.append("h2", metadata=BlueprintMetadata.create(description="r2"))
    assert v1.revision == 1
    assert v2.revision == 2
    assert v2.parent_version_id == v1.version_id
    # After appending v2, the stored v1 is superseded by v2.
    assert lineage.get(v1.version_id).superseded_by == v2.version_id
    assert lineage.head().version_id == v2.version_id
    assert len(lineage) == 2
    assert lineage.blueprint_id == "UCOS-BLPR-1"


def test_lineage_requires_blueprint_id_and_head_fail_closed():
    with pytest.raises(BlueprintVersionError):
        VersionLineage("")
    empty = VersionLineage("UCOS-BLPR-1")
    with pytest.raises(BlueprintVersionError):
        empty.head()
    with pytest.raises(BlueprintVersionError):
        empty.get("UCOS-BVER-missing")


def test_lineage_serialisation_is_deterministic():
    def build() -> str:
        lineage = VersionLineage("UCOS-BLPR-1")
        lineage.append("h1")
        lineage.append("h2")
        return lineage.fingerprint()

    assert build() == build()


def test_lineage_revisions_and_get_by_id():
    lineage = VersionLineage("UCOS-BLPR-1")
    v1 = lineage.append("h1")
    v2 = lineage.append("h2")
    assert lineage.revisions == (lineage.get(v1.version_id), lineage.get(v2.version_id))
    # get() must scan past the first revision to resolve a later one.
    assert lineage.get(v2.version_id).revision == 2
