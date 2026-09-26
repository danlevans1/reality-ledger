from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import StrEnum
import re
from typing import Any

_RECORD_ID=re.compile(r"^RL-\d{4}-\d{6}$"); _INVESTIGATION_ID=re.compile(r"^RLI-\d{4}-\d{6}$")
_EVIDENCE_ID=re.compile(r"^E-\d{6}$"); _SOURCE_ID=re.compile(r"^S-\d{6}$")

class Classification(StrEnum):
    FACT="FACT"; CONTRADICTION="CONTRADICTION"; UNKNOWN="UNKNOWN"; EVIDENCE="EVIDENCE"; CONSTRAINT="CONSTRAINT"; HISTORY="HISTORY"
class Confidence(StrEnum):
    HIGH="HIGH"; MEDIUM="MEDIUM"; LOW="LOW"

@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id:str; title:str; description:str; source_id:str; source_type:str; source_tier:int
    publisher_or_origin:str; original_url:str; publication_date:str|None=None; retrieved_at:str=""
    archive_reference:str|None=None; supports:tuple[str,...]=(); contradicts:tuple[str,...]=()
    limitations:tuple[str,...]=(); content_hash:str|None=None
    def __post_init__(self):
        if not _EVIDENCE_ID.fullmatch(self.evidence_id): raise ValueError("evidence_id must match E-NNNNNN")
        if not _SOURCE_ID.fullmatch(self.source_id): raise ValueError("source_id must match S-NNNNNN")
        if self.source_tier not in range(1,6): raise ValueError("source_tier must be 1 through 5")
        if not self.title.strip() or not self.description.strip(): raise ValueError("title and description must be non-empty")
        if not self.original_url.startswith(("https://","http://")): raise ValueError("original_url must be HTTP(S)")
    def payload(self)->dict[str,Any]: return asdict(self)

@dataclass(frozen=True)
class InvestigationRecord:
    investigation_id:str; slug:str; headline:str; originating_claim:str; originating_source:str; opened_at:str
    published_at:str|None=None; last_verified_at:str|None=None; status:str="OPEN"; summary:str=""
    ledger_record_ids:tuple[str,...]=(); source_ids:tuple[str,...]=(); update_history:tuple[str,...]=()
    def __post_init__(self):
        if not _INVESTIGATION_ID.fullmatch(self.investigation_id): raise ValueError("investigation_id must match RLI-YYYY-NNNNNN")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",self.slug): raise ValueError("slug must be lowercase kebab-case")
        if not self.headline.strip() or not self.originating_claim.strip(): raise ValueError("headline and originating_claim must be non-empty")
        if any(not _RECORD_ID.fullmatch(x) for x in self.ledger_record_ids): raise ValueError("ledger_record_ids contain an invalid record id")
        if any(not _SOURCE_ID.fullmatch(x) for x in self.source_ids): raise ValueError("source_ids contain an invalid source id")
    def payload(self)->dict[str,Any]: return asdict(self)

@dataclass(frozen=True)
class LedgerRecord:
    record_id:str; investigation_id:str; version:int; classification:Classification; claim:str; finding:str; confidence:Confidence
    evidence_ids:tuple[str,...]=(); source_ids:tuple[str,...]=(); constraints:tuple[str,...]=(); created_at:str=""; verified_at:str=""
    supersedes:str|None=None; superseded_by:str|None=None; change_reason:str|None=None; status:str="PUBLISHED"
    def __post_init__(self):
        if not _RECORD_ID.fullmatch(self.record_id): raise ValueError("record_id must match RL-YYYY-NNNNNN")
        if not _INVESTIGATION_ID.fullmatch(self.investigation_id): raise ValueError("investigation_id must match RLI-YYYY-NNNNNN")
        if self.version<1: raise ValueError("version must be >= 1")
        if not self.claim.strip() or not self.finding.strip(): raise ValueError("claim and finding must be non-empty")
        if any(not _EVIDENCE_ID.fullmatch(x) for x in self.evidence_ids): raise ValueError("evidence_ids contain an invalid evidence id")
        if any(not _SOURCE_ID.fullmatch(x) for x in self.source_ids): raise ValueError("source_ids contain an invalid source id")
        if self.version==1 and self.supersedes is not None: raise ValueError("version 1 cannot supersede another version")
        if self.version>1 and not self.supersedes: raise ValueError("later versions must identify the version they supersede")
        if self.version>1 and not self.change_reason: raise ValueError("later versions require change_reason")
    def payload(self)->dict[str,Any]:
        d=asdict(self); d["classification"]=self.classification.value; d["confidence"]=self.confidence.value; return d
