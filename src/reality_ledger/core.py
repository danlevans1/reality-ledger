from __future__ import annotations
import hashlib,json
from collections.abc import Iterable
from typing import Any
from .models import EvidenceRecord,InvestigationRecord,LedgerRecord

def canonical_json(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
def content_hash(record:LedgerRecord|EvidenceRecord|InvestigationRecord)->str:
    return "sha256:"+hashlib.sha256(canonical_json(record.payload()).encode()).hexdigest()
def version_ref(record:LedgerRecord)->str: return f"{record.record_id} v{record.version}"
def validate_version_chain(records:Iterable[LedgerRecord])->None:
    ordered=sorted(records,key=lambda r:r.version)
    if not ordered: raise ValueError("version chain cannot be empty")
    rid,iid=ordered[0].record_id,ordered[0].investigation_id
    for expected,record in enumerate(ordered,start=1):
        if record.record_id!=rid: raise ValueError("all versions must share record_id")
        if record.investigation_id!=iid: raise ValueError("all versions must share investigation_id")
        if record.version!=expected: raise ValueError("versions must be contiguous starting at 1")
        if expected==1:
            if record.supersedes is not None: raise ValueError("first version cannot supersede another version")
        else:
            prior=ordered[expected-2]
            if record.supersedes!=version_ref(prior): raise ValueError("supersedes must reference the immediately prior version")
            if prior.superseded_by not in (None,version_ref(record)): raise ValueError("superseded_by conflicts with the next version")
def validate_references(investigation:InvestigationRecord,ledger_records:Iterable[LedgerRecord],evidence_records:Iterable[EvidenceRecord])->None:
    ledgers=list(ledger_records); evidence=list(evidence_records)
    ledger_ids={x.record_id for x in ledgers}; evidence_ids={x.evidence_id for x in evidence}; source_ids={x.source_id for x in evidence}
    if any(x.investigation_id!=investigation.investigation_id for x in ledgers): raise ValueError("ledger record belongs to another investigation")
    missing=set(investigation.ledger_record_ids)-ledger_ids
    if missing: raise ValueError(f"investigation references missing ledger records: {sorted(missing)}")
    missing=set(investigation.source_ids)-source_ids
    if missing: raise ValueError(f"investigation references missing sources: {sorted(missing)}")
    for item in ledgers:
        missing=set(item.evidence_ids)-evidence_ids
        if missing: raise ValueError(f"{item.record_id} references missing evidence: {sorted(missing)}")
        missing=set(item.source_ids)-source_ids
        if missing: raise ValueError(f"{item.record_id} references missing sources: {sorted(missing)}")
