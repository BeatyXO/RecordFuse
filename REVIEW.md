# Reviewer Map

- **Standalone Intelligent Contract:** yes; no frontend or product flow.
- **Reusable primitive:** consumers import identity via `canonical_of` / `same_entity`.
- **Real consensus logic:** public evidence is fetched inside nondeterministic execution and evaluated with comparative consensus.
- **Clear state design:** namespaces, records, canonical clusters, merge proposals, stale handling, lifecycle counters.
- **Thoughtful equivalence:** same/distinct decisions have explicit identity-evidence requirements and ambiguity fails closed.
- **Tests:** Direct Mode suite plus StudioNet smoke test.
- **Final hardening:** terminal distinctness is stored as immutable record-pair constraints and checked across complete candidate clusters, preventing intermediate merges from bypassing prior distinct decisions.
- **Observed validation:** preflight 13/13; contract and consumer GenVM lint checks passed previously; live SAME_ENTITY and DISTINCT_ENTITY consensus paths were exercised on Studionet. Direct Mode has 23 passing cases plus five known `prompt_comparative` harness limitations in `genlayer-test 0.29.2`.
- **Documentation:** architecture, consensus, security, integration, deployment, and design decisions.

Key invariant: only a consensus result that survives deterministic positive-evidence checks can collapse two canonical clusters into one.
