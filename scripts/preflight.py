"""Small zero-dependency structural gate for reviewer-critical invariants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "contracts" / "record_fuse.py").read_text(encoding="utf-8")
EXAMPLE = (ROOT / "examples" / "canonical_record_consumer.py").read_text(encoding="utf-8")

CHECKS = {
    "single canonical contract": (len(list((ROOT / "contracts").glob("*.py"))) == 1),
    "comparative consensus": "prompt_comparative" in SOURCE,
    "bounded web evidence": "MAX_EVIDENCE" in SOURCE and "MAX_URI" in SOURCE,
    "terminal pair protection": "terminal decision" in SOURCE,
    "cluster-wide distinct constraints": "_clusters_conflict" in SOURCE and "distinct_pairs" in SOURCE,
    "symmetric pair key": "if left_value > right_value" in SOURCE,
    "bounded clusters": "MAX_CLUSTER_SIZE" in SOURCE,
    "immutable namespace rule": 'namespace["identity_rule"]' in SOURCE or '"identity_rule": identity_rule' in SOURCE,
    "https URL admission": 'startswith("https://")' in SOURCE,
    "fail-closed same decision": 'len(matched) == 0' in SOURCE,
    "fail-closed distinct decision": 'len(conflicts) == 0' in SOURCE,
    "deterministic canonicalization": "combined.sort()" in SOURCE,
    "consumer canonical view": "canonical_of" in EXAMPLE and "same_entity" in EXAMPLE,
}

failed = [name for name, passed in CHECKS.items() if not passed]
for name, passed in CHECKS.items():
    print(("PASS" if passed else "FAIL") + " - " + name)
print(f"{len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed")
raise SystemExit(1 if failed else 0)
