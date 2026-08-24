# RecordFuse

**Consensus-based semantic entity resolution for GenLayer.**

RecordFuse is a standalone, reusable Intelligent Contract primitive for answering a deceptively hard registry question:

> Do these two records refer to the same underlying entity or event?

Hashes, IDs, and exact strings can detect byte-for-byte duplicates. They cannot reliably decide whether differently worded records describe the same real-world thing. RecordFuse lets a registry define an immutable semantic identity rule, register records backed by public evidence, and use GenLayer consensus to decide whether two canonical record clusters should be fused.

**This repository intentionally has no frontend.** It is designed to be imported by other Intelligent Contracts and applications.

## Why this belongs on GenLayer

Entity resolution is not a deterministic string-matching problem. Two records can use different names, formatting, timestamps, aliases, or prose while still describing the same event; conversely, two nearly identical records may describe different things.

RecordFuse separates the problem into two layers:

- **Deterministic state:** namespaces, immutable record metadata, canonical IDs, cluster membership, proposal lifecycle, stale-proposal handling, and bounded cluster merges.
- **Non-deterministic judgment:** validators inspect the two public evidence sources and independently decide whether the namespace's identity rule is satisfied.

The consensus-critical output is deliberately narrow:

- `SAME_ENTITY`
- `DISTINCT_ENTITY`
- `INCONCLUSIVE`
- `EXTERNAL_FAILURE`

`SAME_ENTITY` is fail-closed: it is accepted only when the result includes affirmative identity-bearing evidence. `DISTINCT_ENTITY` likewise requires a material conflicting identifier. Ambiguity becomes `INCONCLUSIVE`, not a forced merge.

## Core model

### Namespace

A namespace defines a domain-specific identity boundary:

```text
Namespace
├── name
├── record_type
├── identity_rule   # immutable
├── creator
└── status
```

Example identity rule:

> Two incident records are the same incident only when reliable evidence ties them to the same incident identifier or the same service, region, and occurrence window. Similar wording alone is insufficient.

### Record

```text
Record
├── namespace_id
├── external_ref
├── source_uri
├── summary
├── canonical_id
├── members[]       # stored on canonical roots
└── status
```

Each new record begins as its own canonical cluster.

### Merge proposal

```text
Record A ─┐
          ├─ propose_merge() ── GenLayer consensus ──┬─ SAME_ENTITY ── fuse clusters
Record B ─┘                                          ├─ DISTINCT_ENTITY
                                                     ├─ INCONCLUSIVE
                                                     └─ EXTERNAL_FAILURE
```

The proposal snapshots both canonical roots. If a selected record changes canonical identity before resolution, the proposal becomes `STALE` rather than applying an old judgment to a new state.

## Consensus design

During `resolve_merge`:

1. Deterministic code verifies that the proposal is still fresh.
2. The non-deterministic block fetches both public evidence URIs.
3. An LLM evaluates the evidence under the namespace's immutable identity rule.
4. The leader returns structured JSON containing a decision, reason, matched identifiers, conflicting identifiers, and bounded evidence excerpts.
5. `gl.eq_principle.prompt_comparative` requires validators to agree on the substantive identity decision. Wording may differ, but the decision and material identity facts must be equivalent.
6. Deterministic post-processing fails closed if a decisive label lacks the evidence category it requires.
7. Only `SAME_ENTITY` mutates canonical identity state.

See [docs/CONSENSUS.md](docs/CONSENSUS.md) for the complete equivalence rule and threat model.

## Deterministic canonicalization

When two clusters are fused:

- the lowest member record ID becomes the canonical ID;
- every member is updated to that canonical ID;
- only the canonical root retains the bounded member list;
- cluster size is capped at 32 records;
- canonical cluster count decreases by exactly one.

This makes the post-consensus state transition deterministic and easy for downstream contracts to consume.

## Public API

### Writes

| Method | Purpose |
|---|---|
| `create_namespace(name, record_type, identity_rule)` | Create a reusable identity domain. |
| `deactivate_namespace(namespace_id)` | Stop new registrations and merges for a namespace. |
| `register_record(namespace_id, external_ref, source_uri, summary)` | Register an immutable record. |
| `propose_merge(left_record_id, right_record_id, rationale)` | Open a semantic identity comparison. |
| `resolve_merge(proposal_id)` | Run GenLayer consensus and apply the result. |
| `retry_unresolved(proposal_id)` | Retry `INCONCLUSIVE` or `EXTERNAL_FAILURE` proposals if still fresh. |

### Views

| Method | Purpose |
|---|---|
| `namespace_of(id)` | Return namespace JSON. |
| `record_of(id)` | Return record JSON. |
| `proposal_of(id)` | Return proposal JSON. |
| `record_by_external_ref(namespace_id, ref)` | Resolve an exact external reference. |
| `canonical_of(record_id)` | Return the current canonical record ID. |
| `same_entity(left, right)` | Check whether two records are already in the same canonical cluster. |
| `cluster_of(record_id)` | Return canonical cluster membership. |
| `stats()` | Return lifecycle counters. |

## Consumer integration

A downstream contract does not need to repeat the adjudication logic. It can synchronously read RecordFuse:

```python
@gl.contract_interface
class IRecordFuse:
    class View:
        def same_entity(self, left_record_id: u256, right_record_id: u256) -> bool: ...
        def canonical_of(self, record_id: u256) -> u256: ...
    class Write:
        pass

fuse = IRecordFuse(record_fuse_address)
canonical_id = fuse.view().canonical_of(record_id)
```

A complete consumer is included at [`examples/canonical_record_consumer.py`](examples/canonical_record_consumer.py).

## Example use cases

RecordFuse is intentionally domain-neutral. A namespace can represent:

- duplicate incident/postmortem records;
- research datasets published under different names;
- grants submitted through multiple portals;
- governance proposals that are republished or mirrored;
- supply-chain events from independent reporting systems;
- vulnerability/bug reports that refer to the same underlying issue;
- marketplace catalog records describing the same underlying item.

The namespace identity rule decides what counts as identity in each domain.

## Repository layout

```text
RecordFuse/
├── contracts/
│   └── record_fuse.py
├── examples/
│   └── canonical_record_consumer.py
├── tests/
│   ├── direct/
│   │   └── test_record_fuse.py
│   └── integration/
│       └── test_record_fuse_studionet.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CONSENSUS.md
│   ├── DEPLOYMENT.md
│   ├── INTEGRATION.md
│   └── SECURITY.md
├── .github/workflows/ci.yml
├── gltest.config.yaml
├── requirements.txt
├── DECISION_RECORD.md
├── REVIEW.md
└── SUBMISSION.md
```

## Test and lint

Python 3.12+ is recommended.

```bash
pip install -r requirements.txt
genvm-lint check contracts/record_fuse.py
pytest tests/direct/ -v
```

The direct suite covers namespace lifecycle, record uniqueness, cross-namespace isolation, merge proposal state, successful fusion, fail-closed output handling, distinct decisions, external failures, retries, transitive canonicalization, stale proposals, access control, and state counters.

For the opt-in StudioNet smoke test:

```bash
gltest tests/integration/test_record_fuse_studionet.py -v -s --network studionet
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Security posture

RecordFuse deliberately biases against false-positive merges because canonical fusion is irreversible inside this primitive. Important protections include:

- immutable namespace identity rules;
- explicit prompt-injection treatment of fetched content as evidence, never instructions;
- `INCONCLUSIVE` as the default for ambiguous evidence;
- positive-evidence requirement for `SAME_ENTITY`;
- conflict-evidence requirement for `DISTINCT_ENTITY`;
- stale proposal invalidation;
- same-namespace enforcement;
- bounded evidence, reasoning, identifiers, and cluster sizes;
- exact external-reference uniqueness within a namespace.

See [docs/SECURITY.md](docs/SECURITY.md) for limitations and integration guidance.

## Consensus-shopping protection

Terminal identity decisions are tied to the symmetric canonical pair. `SAME_ENTITY` fuses the clusters and therefore cannot be reproposed; `DISTINCT_ENTITY` is terminal for the immutable evidence pair. Only `INCONCLUSIVE` and `EXTERNAL_FAILURE` may be reopened through `retry_unresolved()`.

## Differentiation

RecordFuse is a domain-neutral canonicalization primitive, not an archive-specific product or frontend. Each namespace supplies its own immutable identity rule, and downstream contracts consume `canonical_of()` / `same_entity()` without an archive schema or application layer.

## What RecordFuse is not

RecordFuse is **not** a truth oracle, credibility score, dispute escrow, reputation system, or generic "AI decides X" wrapper. It solves one reusable state problem: maintaining canonical identity across semantically duplicate records while keeping the consensus boundary explicit and auditable.

## License

MIT. See [LICENSE](LICENSE).
