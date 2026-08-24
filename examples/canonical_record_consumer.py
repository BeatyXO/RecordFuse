# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


@gl.contract_interface
class IRecordFuse:
    class View:
        def same_entity(self, left_record_id: u256, right_record_id: u256) -> bool:
            pass

        def canonical_of(self, record_id: u256) -> u256:
            pass

    class Write:
        pass


class CanonicalRecordConsumer(gl.Contract):
    record_fuse: Address
    canonical_by_key: TreeMap[str, u256]

    def __init__(self, record_fuse: Address) -> None:
        self.record_fuse = record_fuse if isinstance(record_fuse, Address) else Address(record_fuse)
        self.canonical_by_key = TreeMap[str, u256]()

    @gl.public.write
    def import_record(self, local_key: str, record_id: u256) -> None:
        if len(local_key) == 0 or len(local_key) > 120:
            raise gl.vm.UserError("EXPECTED: invalid local key")
        fuse = IRecordFuse(self.record_fuse)
        self.canonical_by_key[local_key] = fuse.view().canonical_of(record_id)

    @gl.public.write
    def require_same_entity(self, left_record_id: u256, right_record_id: u256) -> None:
        fuse = IRecordFuse(self.record_fuse)
        if not fuse.view().same_entity(left_record_id, right_record_id):
            raise gl.vm.UserError("EXPECTED: records are not canonically fused")

    @gl.public.view
    def canonical_for(self, local_key: str) -> u256:
        return self.canonical_by_key.get(local_key, u256(0))
