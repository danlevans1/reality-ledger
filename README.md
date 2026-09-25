# Reality Ledger

**A public record of what the evidence supports.**

Reality Ledger is a source-transparent evidence publication and append-only public record for consequential claims, evidence, contradictions, uncertainty, constraints, and historical change.

## Core doctrine

- Structure over narrative.
- Primary sources first.
- Publish uncertainty rather than conceal it.
- Corrections are additive; published history is not silently rewritten.
- The public factual record is not paywalled.
- Records are designed to be auditable and provenance-aware.

## Canonical classifications

`FACT` · `CONTRADICTION` · `UNKNOWN` · `EVIDENCE` · `CONSTRAINT` · `HISTORY`

Evidentiary confidence is expressed as `HIGH`, `MEDIUM`, or `LOW`. Confidence describes support for the classification, not a numerical probability of truth.

## Architecture

Reality Ledger v1 separates three layers:

1. **Investigation** — human-readable reconstruction of a consequential circulating claim.
2. **Evidence Record** — atomic claims connected to sources, contradictions, unknowns, and constraints.
3. **Ledger Record** — append-only, versioned, hashable history preserving provenance and corrections.

The article is an interface to the evidence. The evidence is not decoration for the article.

## Status

Phase 1: repository and schema foundation.

The first planned end-to-end investigation is `RLI-2026-000001`, examining claims surrounding simultaneous oil-route, refinery, and diesel-market disruptions.

## Integrity

Canonical records will use deterministic serialization and SHA-256 content hashes. A hash proves the integrity of a serialized record; it does **not** prove that the factual assertion itself is true.

## License

No license has been granted yet. All rights are reserved until a project license is explicitly adopted.
