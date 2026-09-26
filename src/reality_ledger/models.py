from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
import re
from typing import Any

_RECORD_ID = re.compile(r"^RL-\d{4}-\d{6}$")
_INVESTIGATION_ID = re.compile(r"^RLI-\d{4}-\d{6}$")


class Classification(StrEnum):
    FACT = "FACT"
    CONTRADICTION = "CONTRADICTION"
    UNKNOWN = "UNKNOWN"
    EVIDENCE = "EVIDENCE"
    CONSTRAINT = "CONSTRAINT"
    HISTORY = "HISTORY"


class Confidence(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class LedgerRecord:
    record_id: str
    investigation_id: str
    version: int
    classification: Classification
    claim: str
    finding: str
    confidence: Confidence
    evidence_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    created_at: str = ""
    verified_at: str = ""
    supersedes: str | None = None
    superseded_by: str | None = None
    change_reason: str | None = None
    status: str = "PUBLISHED"

    def __post_init__(self) -> None:
        if not _RECORD_ID.fullmatch(self.record_id):
            raise ValueError("record_id must match RL-YYYY-NNNNNN")
        if not _INVESTIGATION_ID.fullmatch(self.investigation_id):
            raise ValueError("investigation_id must match RLI-YYYY-NNNNNN")
        if self.version < 1:
            raise ValueError("version must be >= 1")
        if not self.claim.strip() or not self.finding.strip():
            raise ValueError("claim and finding must be non-empty")
        if self.version == 1 and self.supersedes is not None:
            raise ValueError("version 1 cannot supersede another version")
        if self.version > 1 and not self.supersedes:
            raise ValueError("later versions must identify the version they supersede")
        if self.version > 1 and not self.change_reason:
            raise ValueError("later versions require change_reason")

    def payload(self) -> dict[str, Any]:
        data = asdict(self)
        data["classification"] = self.classification.value
        data["confidence"] = self.confidence.value
        return data
