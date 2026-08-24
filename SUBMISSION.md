# Submission Copy

## Title

RecordFuse — Semantic Entity Resolution Primitive

## Description

RecordFuse is a standalone GenLayer Intelligent Contract for semantic entity resolution: deciding whether differently worded public records refer to the same underlying entity or event. Each namespace defines an immutable identity rule, records are anchored to public evidence URLs, and merge proposals use GenLayer comparative consensus to return SAME_ENTITY, DISTINCT_ENTITY, INCONCLUSIVE, or EXTERNAL_FAILURE. SAME_ENTITY requires affirmative identity-bearing evidence; ambiguity fails closed. Confirmed matches are deterministically fused into a bounded canonical cluster using the lowest record ID as root. Downstream contracts can reuse the result through canonical_of() and same_entity() instead of rebuilding adjudication. The repo is contract-only and includes a consumer example, Direct Mode tests, a StudioNet smoke test, architecture/security/consensus docs, CI, and deployment guidance.

## Repository

https://github.com/BeatyXO/RecordFuse

## StudioNet Explorer

Add the deployed contract explorer URL after final StudioNet deployment.
