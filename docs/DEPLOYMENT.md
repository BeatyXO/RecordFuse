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

## Superseded pre-hardening deployment

`0x3A7ca437743B648d7c74841E9490A6ed43Ae5bB7` is retained as historical smoke evidence. It predates terminal canonical-pair finality and is not the canonical final deployment.

## Verified runtime evidence (2026-08-24)

- Network: Studionet
- Canonical smoke deployment address: `0x3A7ca437743B648d7c74841E9490A6ed43Ae5bB7`
- Deployment source: commit `acbfbff` (the deployable contract source is unchanged from `ed558f9`)
- Deployer: `0xca457Aa48836746D7058623092492962dA762848`
- Namespace transaction: `0xc15560e02cbb8593dfae6d0e83fd08ebd023613d555594a438d2f94b6f5e9ebb`
- Record transaction: `0xdf08b5b161b9b3123d0ad0bf25f9cad1811e51b1075eed14898d622a56b57d3d`
- Runtime result: both transactions were accepted with majority agreement; namespace and record views returned `ACTIVE` and canonical ID `1`.

This is deterministic registry smoke evidence. A live semantic merge transaction has not been claimed here.

## Hardened live semantic evidence

- Hardened deployment address: `0xbdDBcae297B7a816Fbb20274CFDdCFEdE71Ff841`
- Hardened contract source: commit `92fee3f` (contract blob remains unchanged in subsequent documentation/test commits)
- Namespace transaction: `0x78912ebadc56877fda8d3b4252418ef053098d6690dce82107b72870addd87cd`
- Record A transaction: `0x9f8a4af7ccfb425981612a250dc53507faeef69ed7b762dca8c1ad08580fce20`
- Record B transaction: `0x07fad802b2fe380989137640eff534eb96eeae8405f192b8e32d5048afc1b403`
- Proposal transaction: `0xf528ede485f6751a9ac25627df150377dbd62941c6ad506fce505666b04b1417`
- Resolve transaction: `0x4f1930860d13c5446bc2d681f25b830f0aaea63166e59cad2a500e12fdde0e34`
- Decision: `SAME_ENTITY`; validators reached majority agreement.
- Final state: proposal `FUSED`, canonical ID `1`, cluster members `1` and `2`.

The live evidence uses the committed public fixtures under `tests/fixtures/` and exercises web rendering, LLM reasoning, comparative consensus, and deterministic fusion.
