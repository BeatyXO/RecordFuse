import json

from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

RULE = "Two records are the same incident only when reliable public evidence ties them to the same incident identifier or the same service, region, and occurrence window."


def test_studionet_deterministic_registry_smoke(default_account):
    factory = get_contract_factory("RecordFuse")
    contract = factory.deploy(account=default_account)
    tx = contract.create_namespace(args=["Incidents", "service incident", RULE], account=default_account).transact()
    assert tx_execution_succeeded(tx)
    tx = contract.register_record(args=[1, "INC-A", "https://example.com/records/a", "EU API outage"], account=default_account).transact()
    assert tx_execution_succeeded(tx)
    namespace = json.loads(contract.namespace_of(args=[1]).call())
    record = json.loads(contract.record_of(args=[1]).call())
    assert namespace["status"] == "ACTIVE"
    assert record["canonical_id"] == "1"
