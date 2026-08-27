# Security and Failure Model

False-positive fusion is more damaging than a false negative because fusion changes canonical identity for every downstream consumer. RecordFuse therefore fails closed.

Protections include immutable identity rules, prompt-injection treatment of web content as evidence only, positive-evidence requirements for `SAME_ENTITY`, conflict-evidence requirements for `DISTINCT_ENTITY`, stale proposal handling, namespace isolation, bounded evidence, and bounded cluster unions.

Terminal pair finality prevents consensus shopping: a symmetric canonical pair with a terminal `DISTINCT_ENTITY` decision cannot be reopened by reversing arguments or submitting another proposal. Only `INCONCLUSIVE` and `EXTERNAL_FAILURE` remain retryable through the explicit retry path.

Distinct constraints are preserved at record-pair level and checked across complete candidate clusters. This prevents a sequence of individually valid merges from turning any previously distinct pair into `same_entity`.

## Known limitations

Fusion is irreversible inside this primitive. High-stakes integrations should use conservative identity rules and separate appeal/finality mechanisms if needed.

HTTP content can change even though the registered URI is immutable. Consumers needing historical integrity should use content-addressed or otherwise stable sources.

URL admission is a deterministic safety floor, not a complete SSRF defense. RecordFuse requires HTTPS, rejects credentials, explicit ports, localhost, private/link-local IPv4, and obvious internal suffixes; DNS rebinding and hostile remote content remain network/provider concerns.

RecordFuse determines identity, not truth. It does not provide sybil/spam resistance, authenticity guarantees, or credibility scoring.
