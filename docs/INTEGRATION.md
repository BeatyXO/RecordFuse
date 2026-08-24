# Integration Guide

Most consumers need only `same_entity` and `canonical_of` from the RecordFuse view interface.

```python
@gl.contract_interface
class IRecordFuse:
    class View:
        def same_entity(self, left_record_id: u256, right_record_id: u256) -> bool: ...
        def canonical_of(self, record_id: u256) -> u256: ...
    class Write:
        pass
```

Use a synchronous IC view call:

```python
fuse = IRecordFuse(record_fuse_address)
canonical = fuse.view().canonical_of(record_id)
```

A good namespace rule names identity-bearing facts and states what is insufficient. Avoid vague rules such as "merge records that look similar."

`external_ref` is deterministically unique inside a namespace; `canonical_id` represents semantic identity after consensus.
