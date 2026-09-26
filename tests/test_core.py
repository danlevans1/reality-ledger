from dataclasses import replace

import pytest

from reality_ledger import (
    Classification,
    Confidence,
    LedgerRecord,
    canonical_json,
    content_hash,
    validate_version_chain,
)


def record(**changes):
    base = LedgerRecord(
        record_id="RL-2026-000001",
        investigation_id="RLI-2026-000001",
        version=1,
        classification=Classification.UNKNOWN,
        claim="The disruptions are centrally coordinated.",
        finding="Available evidence does not establish central coordination.",
        confidence=Confidence.HIGH,
        evidence_ids=("E-000001", "E-000002"),
        source_ids=("S-000001",),
        created_at="2026-09-25T20:00:00-07:00",
        verified_at="2026-09-25T20:00:00-07:00",
    )
    return replace(base, **changes)


def test_canonical_json_is_stable():
    assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_hash_is_deterministic_and_prefixed():
    first = content_hash(record())
    assert first == content_hash(record())
    assert first.startswith("sha256:")
    assert len(first) == 71


def test_hash_changes_when_finding_changes():
    assert content_hash(record()) != content_hash(record(finding="New evidence changes the finding."))


def test_unknown_can_have_high_confidence():
    item = record()
    assert item.classification is Classification.UNKNOWN
    assert item.confidence is Confidence.HIGH


def test_invalid_identifier_rejected():
    with pytest.raises(ValueError):
        record(record_id="1")


def test_later_version_requires_change_reason():
    with pytest.raises(ValueError):
        record(version=2, supersedes="RL-2026-000001 v1")


def test_valid_two_version_chain():
    v1 = record(superseded_by="RL-2026-000001 v2")
    v2 = record(
        version=2,
        supersedes="RL-2026-000001 v1",
        change_reason="New primary evidence became available.",
        finding="New primary evidence establishes a narrower relationship.",
    )
    validate_version_chain([v2, v1])


def test_chain_rejects_gap():
    v1 = record()
    v3 = record(
        version=3,
        supersedes="RL-2026-000001 v2",
        change_reason="Changed.",
    )
    with pytest.raises(ValueError):
        validate_version_chain([v1, v3])


def test_chain_rejects_wrong_prior_reference():
    v1 = record()
    v2 = record(
        version=2,
        supersedes="RL-2025-999999 v1",
        change_reason="Changed.",
    )
    with pytest.raises(ValueError):
        validate_version_chain([v1, v2])
