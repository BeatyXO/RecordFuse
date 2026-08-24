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

## Verified runtime evidence (2026-08-24)

- Network: Studionet
- Canonical smoke deployment address: `0x3A7ca437743B648d7c74841E9490A6ed43Ae5bB7`
- Deployment source: commit `acbfbff` (the deployable contract source is unchanged from `ed558f9`)
- Deployer: `0xca457Aa48836746D7058623092492962dA762848`
- Namespace transaction: `0xc15560e02cbb8593dfae6d0e83fd08ebd023613d555594a438d2f94b6f5e9ebb`
- Record transaction: `0xdf08b5b161b9b3123d0ad0bf25f9cad1811e51b1075eed14898d622a56b57d3d`
- Runtime result: both transactions were accepted with majority agreement; namespace and record views returned `ACTIVE` and canonical ID `1`.

This is deterministic registry smoke evidence. A live semantic merge transaction has not been claimed here.
