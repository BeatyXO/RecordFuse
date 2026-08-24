# Architecture

RecordFuse turns semantic entity resolution into a reusable contract primitive. The contract owns canonical identity state; GenLayer consensus is used only for the judgment that deterministic code cannot safely perform.

## State domains

Namespaces isolate identity semantics. `identity_rule` is immutable because changing the rule after records have been fused would silently change the meaning of earlier decisions.

Record metadata is immutable after registration. Each record stores a `canonical_id`; canonical roots also store the bounded member list.

A proposal snapshots the selected records' canonical roots so a decision cannot be silently applied to a materially different identity graph.

## State machine

```text
OPEN
├── SAME_ENTITY       -> FUSED
├── DISTINCT_ENTITY   -> DISTINCT_ENTITY
├── INCONCLUSIVE      -> INCONCLUSIVE -> retry -> OPEN
├── external read err -> EXTERNAL_FAILURE -> retry -> OPEN
└── changed baseline  -> STALE
```

## Canonical union rule

After `SAME_ENTITY`, deterministic code combines unique member IDs, sorts them, rejects oversized clusters, selects the lowest record ID as canonical, updates every member, and decrements the canonical cluster count exactly once.

## Why not fuzzy matching?

A similarity score is not identity. Similar wording can describe different events and very different wording can describe the same event. Namespace rules supply domain semantics, public evidence supplies grounding, and consensus resolves the judgment.
