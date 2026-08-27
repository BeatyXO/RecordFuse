# Consensus and Equivalence

## Consensus question

> Under this namespace's immutable identity rule, do these two public records describe the same underlying entity or event?

The proposer rationale is context only. It cannot substitute for public evidence.

## Leader execution

For a fresh proposal, the leader fetches both evidence URIs, truncates each to a bounded evidence window, asks an LLM to apply the identity rule, and requires structured JSON containing `decision`, `reason`, `matched_identifiers`, and `conflicting_identifiers`.

Allowed semantic decisions are `SAME_ENTITY`, `DISTINCT_ENTITY`, and `INCONCLUSIVE`. Source-read failure is normalized to `EXTERNAL_FAILURE`.

## Equivalence principle

RecordFuse uses `gl.eq_principle.prompt_comparative`.

- `SAME_ENTITY` is equivalent only when validators identify affirmative identity-bearing evidence satisfying the rule.
- `DISTINCT_ENTITY` is equivalent only when validators identify a material identity conflict proving the records are different.
- Similar names, topics, prose, or proposer assertions are insufficient for `SAME_ENTITY`.
- Ambiguous evidence must remain `INCONCLUSIVE`.
- Identifier wording and reasoning may differ if they refer to the same material facts.

## Deterministic postconditions

`SAME_ENTITY` with no matched identifiers is downgraded to `INCONCLUSIVE`. `DISTINCT_ENTITY` with no conflicting identifiers is likewise downgraded. Malformed or unknown output is also downgraded.

Fetched content is explicitly framed as untrusted evidence, never executable instructions. High-stakes integrations should prefer stable or content-addressed public evidence where possible.

## Cluster-wide distinctness

Every terminal `DISTINCT_ENTITY` result is also stored as an immutable record-pair constraint. Before creating a proposal or fusing clusters, the contract checks every member pair across the two candidate clusters. Therefore a later intermediate merge cannot absorb records that were previously adjudicated distinct, even when the original pair is no longer the current pair of canonical roots.
