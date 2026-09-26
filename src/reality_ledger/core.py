from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from typing import Any

from .models import LedgerRecord


def canonical_json(value: Any) -> str:
    """Serialize deterministically for hashing and public verification."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def content_hash(record: LedgerRecord) -> str:
    encoded = canonical_json(record.payload()).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def version_ref(record: LedgerRecord) -> str:
    return f"{record.record_id} v{record.version}"


def validate_version_chain(records: Iterable[LedgerRecord]) -> None:
    ordered = sorted(records, key=lambda r: r.version)
    if not ordered:
        raise ValueError("version chain cannot be empty")

    record_id = ordered[0].record_id
    investigation_id = ordered[0].investigation_id

    for expected, record in enumerate(ordered, start=1):
        if record.record_id != record_id:
            raise ValueError("all versions must share record_id")
        if record.investigation_id != investigation_id:
            raise ValueError("all versions must share investigation_id")
        if record.version != expected:
            raise ValueError("versions must be contiguous starting at 1")
        if expected == 1:
            if record.supersedes is not None:
                raise ValueError("first version cannot supersede another version")
        else:
            prior = ordered[expected - 2]
            if record.supersedes != version_ref(prior):
                raise ValueError("supersedes must reference the immediately prior version")
            if prior.superseded_by not in (None, version_ref(record)):
                raise ValueError("superseded_by conflicts with the next version")
