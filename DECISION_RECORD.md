# Design Decision Record

1. **Contract-only:** no frontend; this is a reusable Intelligent Contract primitive.
2. **Namespace-specific identity rules:** identity is domain-specific, so every namespace stores an immutable rule.
3. **Public evidence mandatory:** records require HTTP(S) evidence; summaries alone cannot justify fusion.
4. **Bounded outcomes:** `SAME_ENTITY`, `DISTINCT_ENTITY`, `INCONCLUSIVE`, plus operational `EXTERNAL_FAILURE`.
5. **Fail closed:** decisive outputs lacking their required evidence category are downgraded to `INCONCLUSIVE`.
6. **Irreversible fusion:** canonical references stay stable; split/appeal semantics belong in an explicit higher-level primitive.
7. **Lowest ID wins:** canonical selection is deterministic, never chosen by a validator or proposer.
8. **Cluster cap:** unions are capped at 32 members to bound persistent writes.
9. **Stale proposals terminate:** proposals are tied to the canonical roots present when opened.
10. **Distinct is not a permanent blacklist:** new evidence can justify a later comparison while preserving the earlier decision record.
