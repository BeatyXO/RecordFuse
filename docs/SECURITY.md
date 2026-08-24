# Security and Failure Model

False-positive fusion is more damaging than a false negative because fusion changes canonical identity for every downstream consumer. RecordFuse therefore fails closed.

Protections include immutable identity rules, prompt-injection treatment of web content as evidence only, positive-evidence requirements for `SAME_ENTITY`, conflict-evidence requirements for `DISTINCT_ENTITY`, stale proposal handling, namespace isolation, bounded evidence, and bounded cluster unions.

## Known limitations

Fusion is irreversible inside this primitive. High-stakes integrations should use conservative identity rules and separate appeal/finality mechanisms if needed.

HTTP content can change even though the registered URI is immutable. Consumers needing historical integrity should use content-addressed or otherwise stable sources.

RecordFuse determines identity, not truth. It does not provide sybil/spam resistance, authenticity guarantees, or credibility scoring.
