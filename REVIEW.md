# Reviewer Map

- **Standalone Intelligent Contract:** yes; no frontend or product flow.
- **Reusable primitive:** consumers import identity via `canonical_of` / `same_entity`.
- **Real consensus logic:** public evidence is fetched inside nondeterministic execution and evaluated with comparative consensus.
- **Clear state design:** namespaces, records, canonical clusters, merge proposals, stale handling, lifecycle counters.
- **Thoughtful equivalence:** same/distinct decisions have explicit identity-evidence requirements and ambiguity fails closed.
- **Tests:** Direct Mode suite plus StudioNet smoke test.
- **Documentation:** architecture, consensus, security, integration, deployment, and design decisions.

Key invariant: only a consensus result that survives deterministic positive-evidence checks can collapse two canonical clusters into one.
