import json

from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

RULE = "Two records are the same incident only when reliable public evidence ties them to the same incident identifier or the same service, region, and occurrence window."
LIVE_BASE = "https://raw.githubusercontent.com/BeatyXO/RecordFuse/main/tests/fixtures/"


def test_studionet_deterministic_registry_smoke(default_account):
    factory = get_contract_factory("RecordFuse")
    contract = factory.deploy(account=default_account)
    print(f"DEPLOYMENT_ADDRESS={contract.address}")
    tx = contract.create_namespace(args=["Incidents", "service incident", RULE]).transact()
    print(f"NAMESPACE_TX={tx}")
    assert tx_execution_succeeded(tx)
    tx = contract.register_record(args=[1, "INC-A", "https://example.com/records/a", "EU API outage"]).transact()
    print(f"RECORD_TX={tx}")
    assert tx_execution_succeeded(tx)
    namespace = json.loads(contract.namespace_of(args=[1]).call())
    record = json.loads(contract.record_of(args=[1]).call())
    assert namespace["status"] == "ACTIVE"
    assert record["canonical_id"] == "1"


def test_studionet_same_entity_live_consensus(default_account):
    factory = get_contract_factory("RecordFuse")
    contract = factory.deploy(account=default_account)
    print(f"LIVE_DEPLOYMENT_ADDRESS={contract.address}")
    namespace_tx = contract.create_namespace(args=["Live incidents", "service incident", RULE]).transact()
    left_tx = contract.register_record(args=[1, "RF-A", LIVE_BASE + "incident_same_a.txt", "Payments API incident RF-SHARED-42"]).transact()
    right_tx = contract.register_record(args=[1, "RF-B", LIVE_BASE + "incident_same_b.txt", "Payments API incident RF-SHARED-42"]).transact()
    proposal_tx = contract.propose_merge(args=[1, 2, "same incident identity evidence"]).transact()
    proposal_id = int(proposal_tx["consensus_data"]["leader_receipt"][0]["result"]["payload"]["readable"])
    resolve_tx = contract.resolve_merge(args=[proposal_id]).transact(wait_retries=100)
    print(f"LIVE_PROPOSAL_ID={proposal_id}")
    print(f"LIVE_RESOLVE_RECEIPT={resolve_tx}")
    proposal = json.loads(contract.proposal_of(args=[proposal_id]).call())
    cluster = json.loads(contract.cluster_of(args=[1]).call())
    print(f"LIVE_NAMESPACE_TX={namespace_tx.get('hash')}")
    print(f"LIVE_LEFT_TX={left_tx.get('hash')}")
    print(f"LIVE_RIGHT_TX={right_tx.get('hash')}")
    print(f"LIVE_PROPOSAL_RESULT={proposal_tx}")
    print(f"LIVE_RESOLVE_TX={resolve_tx.get('hash')}")
    print(f"LIVE_PROPOSAL={json.dumps(proposal, sort_keys=True)}")
    print(f"LIVE_CLUSTER={json.dumps(cluster, sort_keys=True)}")
    assert proposal["status"] == "FUSED"
    assert contract.same_entity(args=[1, 2]).call() is True
    assert contract.canonical_of(args=[1]).call() == contract.canonical_of(args=[2]).call()
    assert set(cluster["members"]) == {"1", "2"}
