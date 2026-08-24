# Deployment and Validation

## Prerequisites

- Python 3.12+
- `genlayer-test`
- `genvm-linter`

```bash
pip install -r requirements.txt
genvm-lint check contracts/record_fuse.py
pytest tests/direct/ -v
```

`gltest.config.yaml` points StudioNet at `https://studio.genlayer.com/api`.

Run the integration smoke test with:

```bash
gltest tests/integration/test_record_fuse_studionet.py -v -s --network studionet
```

Suggested manual demo: deploy RecordFuse, create an incident namespace, register two public sources describing the same incident, propose a merge, resolve it, then inspect `proposal_of`, `canonical_of`, and `cluster_of`.
