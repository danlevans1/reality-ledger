import pytest
from reality_ledger import Classification,Confidence,EvidenceRecord,InvestigationRecord,LedgerRecord,content_hash,validate_references

def evidence():
    return EvidenceRecord("E-000001","Primary record","Direct evidence.","S-000001","government_dataset",1,"Example Agency","https://example.gov/data",retrieved_at="2026-09-25T18:00:00-07:00")
def ledger(**changes):
    d=dict(record_id="RL-2026-000001",investigation_id="RLI-2026-000001",version=1,classification=Classification.FACT,claim="A measurable event occurred.",finding="The primary record supports the claim.",confidence=Confidence.HIGH,evidence_ids=("E-000001",),source_ids=("S-000001",),created_at="2026-09-25T18:00:00-07:00",verified_at="2026-09-25T18:00:00-07:00"); d.update(changes); return LedgerRecord(**d)
def investigation(**changes):
    d=dict(investigation_id="RLI-2026-000001",slug="example-investigation",headline="Example Investigation",originating_claim="A claim is circulating.",originating_source="https://example.com/claim",opened_at="2026-09-25T18:00:00-07:00",ledger_record_ids=("RL-2026-000001",),source_ids=("S-000001",)); d.update(changes); return InvestigationRecord(**d)
def test_evidence_hash_is_deterministic(): assert content_hash(evidence())==content_hash(evidence())
def test_source_tier_is_bounded():
    with pytest.raises(ValueError): EvidenceRecord("E-000001","x","x","S-000001","x",6,"x","https://example.com")
def test_investigation_slug_is_strict():
    with pytest.raises(ValueError): investigation(slug="Not Valid")
def test_cross_record_references_are_valid(): validate_references(investigation(),[ledger()],[evidence()])
def test_missing_evidence_is_rejected():
    with pytest.raises(ValueError,match="missing evidence"): validate_references(investigation(),[ledger(evidence_ids=("E-999999",))],[evidence()])
def test_missing_investigation_ledger_is_rejected():
    with pytest.raises(ValueError,match="missing ledger"): validate_references(investigation(ledger_record_ids=("RL-2026-999999",)),[ledger()],[evidence()])
def test_cross_investigation_ledger_is_rejected():
    with pytest.raises(ValueError,match="another investigation"): validate_references(investigation(),[ledger(investigation_id="RLI-2026-000002")],[evidence()])
