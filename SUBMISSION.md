# Submission Copy

## Title

RecordFuse — Semantic Entity Resolution Primitive

## Description

RecordFuse is a standalone GenLayer Intelligent Contract for semantic entity resolution: deciding whether differently worded public records refer to the same underlying entity or event. Each namespace defines an immutable identity rule, records are anchored to public evidence URLs, and merge proposals use GenLayer comparative consensus to return SAME_ENTITY, DISTINCT_ENTITY, INCONCLUSIVE, or EXTERNAL_FAILURE. SAME_ENTITY requires affirmative identity-bearing evidence; ambiguity fails closed. Confirmed matches are deterministically fused into a bounded canonical cluster using the lowest record ID as root. Downstream contracts can reuse the result through canonical_of() and same_entity() instead of rebuilding adjudication. The repo is contract-only and includes a consumer example, Direct Mode tests, a StudioNet smoke test, architecture/security/consensus docs, CI, and deployment guidance.

## Repository

https://github.com/BeatyXO/RecordFuse

## StudioNet Explorer

Canonical hardened Studionet deployment: `0xbdDBcae297B7a816Fbb20274CFDdCFEdE71Ff841`.
The earlier `0x3A7ca437743B648d7c74841E9490A6ed43Ae5bB7` deployment is superseded pre-hardening history.
Explorer/Studio: [GenLayer Studio](https://studio.genlayer.com/).

Verified smoke transactions:

- Namespace: `0xc15560e02cbb8593dfae6d0e83fd08ebd023613d555594a438d2f94b6f5e9ebb`
- Record: `0xdf08b5b161b9b3123d0ad0bf25f9cad1811e51b1075eed14898d622a56b57d3d`

The live evidence proves deployment, consensus-backed deterministic writes, public reads, and the semantic merge path.

Live semantic merge evidence: resolve transaction `0x4f1930860d13c5446bc2d681f25b830f0aaea63166e59cad2a500e12fdde0e34` reached `SAME_ENTITY` with majority agreement; proposal status was `FUSED`, canonical ID `1`, and the cluster contained records `1` and `2`.

Live distinct evidence: resolve transaction `0x945f425e540fa5aded8b81f9bf343ea525aa2195d4305bea60e7d36dd8a6f3fc` reached `DISTINCT_ENTITY` with conflicting identifiers; the reversed terminal pair returned an explicit rollback.

Final steward correction: terminal distinctness is now persisted as immutable record-pair constraints and checked across full clusters before any fusion. This prevents indirect intermediate merges from violating a prior distinct decision. The corrected contract requires a fresh deployment and fresh matching live evidence.
