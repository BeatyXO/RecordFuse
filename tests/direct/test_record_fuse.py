import json
import pytest

CONTRACT = "contracts/record_fuse.py"
LEFT_URI = "https://example.com/records/alpha"
RIGHT_URI = "https://example.com/records/beta"
THIRD_URI = "https://example.com/records/gamma"
RULE = "Two records are the same incident only when reliable evidence ties them to the same incident identifier or the same service, region, and occurrence window. Similar wording alone is insufficient."


def deploy(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    direct_vm.check_pickling = True
    return contract


def create_namespace(contract, direct_vm, sender, name="Incidents"):
    direct_vm.sender = sender
    return contract.create_namespace(name, "service incident", RULE)


def register(contract, direct_vm, sender, namespace_id, ref, uri, summary):
    direct_vm.sender = sender
    return contract.register_record(namespace_id, ref, uri, summary)


def seed_three(contract, direct_vm, sender):
    namespace_id = create_namespace(contract, direct_vm, sender)
    a = register(contract, direct_vm, sender, namespace_id, "INC-A", LEFT_URI, "EU API outage on 2026-08-20")
    b = register(contract, direct_vm, sender, namespace_id, "INC-B", RIGHT_URI, "European API unavailable on 2026-08-20")
    c = register(contract, direct_vm, sender, namespace_id, "INC-C", THIRD_URI, "Separate payment outage on 2026-08-21")
    return namespace_id, a, b, c


def mock_sources(direct_vm):
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*records/alpha.*", {"status": 200, "body": "Incident ID INC-42. EU API outage. Started 10:02 UTC."})
    direct_vm.mock_web(r".*records/beta.*", {"status": 200, "body": "Postmortem INC-42. EU API outage. Started 10:02 UTC."})
    direct_vm.mock_web(r".*records/gamma.*", {"status": 200, "body": "Incident ID PAY-9. Payments outage. Started 12:30 UTC."})


def mock_decision(direct_vm, decision, matched=None, conflicts=None, reason="test decision"):
    matched = matched or []; conflicts = conflicts or []
    direct_vm.mock_llm(r".*resolving whether two public records.*", json.dumps({"decision": decision, "reason": reason, "matched_identifiers": matched, "conflicting_identifiers": conflicts}))


def test_create_namespace_stores_immutable_identity_rule(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); namespace_id = create_namespace(contract, direct_vm, direct_alice)
    namespace = json.loads(contract.namespace_of(namespace_id))
    assert namespace["record_type"] == "service incident" and namespace["identity_rule"] == RULE and namespace["status"] == "ACTIVE"


@pytest.mark.parametrize("name,record_type,identity_rule", [("", "incident", RULE), ("Incidents", "", RULE), ("Incidents", "incident", "")])
def test_create_namespace_rejects_empty_required_fields(direct_deploy, direct_vm, direct_alice, name, record_type, identity_rule):
    contract = deploy(direct_deploy, direct_vm); direct_vm.sender = direct_alice
    with direct_vm.expect_revert("EXPECTED"): contract.create_namespace(name, record_type, identity_rule)


def test_register_record_starts_as_own_canonical_cluster(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); namespace_id = create_namespace(contract, direct_vm, direct_alice)
    record_id = register(contract, direct_vm, direct_alice, namespace_id, "INC-A", LEFT_URI, "outage")
    record = json.loads(contract.record_of(record_id))
    assert record["canonical_id"] == str(record_id) and record["members"] == [str(record_id)] and contract.record_by_external_ref(namespace_id, "INC-A") == record_id


def test_register_record_rejects_duplicate_external_ref(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); namespace_id = create_namespace(contract, direct_vm, direct_alice)
    register(contract, direct_vm, direct_alice, namespace_id, "INC-A", LEFT_URI, "outage")
    with direct_vm.expect_revert("EXPECTED"): register(contract, direct_vm, direct_alice, namespace_id, "INC-A", RIGHT_URI, "duplicate")


@pytest.mark.parametrize("uri", [
    "http://example.com/evidence",
    "https://user:pass@example.com/evidence",
    "https://localhost/evidence",
    "https://127.0.0.1/evidence",
    "https://10.0.0.8/evidence",
    "https://169.254.1.2/evidence",
    "https://192.168.1.10/evidence",
    "https://service.internal/evidence",
    "https://example.com:8443/evidence",
])
def test_register_record_rejects_non_public_evidence_urls(direct_deploy, direct_vm, direct_alice, uri):
    contract = deploy(direct_deploy, direct_vm); namespace_id = create_namespace(contract, direct_vm, direct_alice)
    with direct_vm.expect_revert("EXPECTED"): register(contract, direct_vm, direct_alice, namespace_id, "BAD", uri, "evidence")


def test_register_record_accepts_https_public_hostname(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); namespace_id = create_namespace(contract, direct_vm, direct_alice)
    assert register(contract, direct_vm, direct_alice, namespace_id, "GOOD", "https://example.com/evidence", "evidence") == 1


def test_pair_key_is_symmetric_and_terminal_guard_is_present(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    assert contract._pair_key(1, 2, 3) == contract._pair_key(1, 3, 2)
    assert "canonical pair already has a terminal decision" in open(CONTRACT, encoding="utf-8").read()


def test_propose_merge_rejects_cross_namespace_records(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); ns1 = create_namespace(contract, direct_vm, direct_alice, "One"); ns2 = create_namespace(contract, direct_vm, direct_alice, "Two")
    a = register(contract, direct_vm, direct_alice, ns1, "A", LEFT_URI, "a"); b = register(contract, direct_vm, direct_alice, ns2, "B", RIGHT_URI, "b")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("EXPECTED"): contract.propose_merge(a, b, "candidate")


def test_same_entity_consensus_fuses_clusters(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, b, _ = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    proposal_id = contract.propose_merge(a, b, "same incident"); mock_sources(direct_vm); mock_decision(direct_vm, "SAME_ENTITY", matched=["Incident ID INC-42", "same 10:02 UTC start"]); contract.resolve_merge(proposal_id)
    proposal = json.loads(contract.proposal_of(proposal_id))
    assert proposal["status"] == "FUSED" and contract.same_entity(a, b) is True and contract.canonical_of(b) == a


def test_same_entity_without_positive_identifier_fails_closed(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, b, _ = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    proposal_id = contract.propose_merge(a, b, "looks similar"); mock_sources(direct_vm); mock_decision(direct_vm, "SAME_ENTITY", matched=[]); contract.resolve_merge(proposal_id)
    assert json.loads(contract.proposal_of(proposal_id))["status"] == "INCONCLUSIVE" and contract.same_entity(a, b) is False


def test_distinct_entity_requires_conflict_and_keeps_clusters_separate(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, _, c = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    proposal_id = contract.propose_merge(a, c, "possibly separate"); mock_sources(direct_vm); mock_decision(direct_vm, "DISTINCT_ENTITY", conflicts=["INC-42 vs PAY-9"]); contract.resolve_merge(proposal_id)
    assert json.loads(contract.proposal_of(proposal_id))["status"] == "DISTINCT_ENTITY" and contract.same_entity(a, c) is False


def test_malformed_model_output_becomes_inconclusive(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, b, _ = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    proposal_id = contract.propose_merge(a, b, "candidate"); mock_sources(direct_vm); direct_vm.mock_llm(r".*resolving whether two public records.*", "not-json"); contract.resolve_merge(proposal_id)
    assert json.loads(contract.proposal_of(proposal_id))["status"] == "INCONCLUSIVE"


def test_unreadable_source_becomes_external_failure(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, b, _ = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    proposal_id = contract.propose_merge(a, b, "candidate"); direct_vm.clear_mocks(); direct_vm.mock_web(r".*records/.*", Exception("source unavailable")); contract.resolve_merge(proposal_id)
    assert json.loads(contract.proposal_of(proposal_id))["status"] == "EXTERNAL_FAILURE"


def test_retry_reopens_inconclusive_proposal(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, b, _ = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    proposal_id = contract.propose_merge(a, b, "candidate"); mock_sources(direct_vm); mock_decision(direct_vm, "INCONCLUSIVE"); contract.resolve_merge(proposal_id); contract.retry_unresolved(proposal_id)
    assert json.loads(contract.proposal_of(proposal_id))["status"] == "OPEN"


def test_fusion_is_transitive(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, b, c = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    p1 = contract.propose_merge(a, b, "same"); mock_sources(direct_vm); mock_decision(direct_vm, "SAME_ENTITY", matched=["shared identity"]); contract.resolve_merge(p1)
    direct_vm.clear_mocks(); p2 = contract.propose_merge(b, c, "same after new evidence"); mock_sources(direct_vm); mock_decision(direct_vm, "SAME_ENTITY", matched=["shared canonical identity"]); contract.resolve_merge(p2)
    assert contract.canonical_of(a) == a and contract.canonical_of(b) == a and contract.canonical_of(c) == a


def test_proposal_becomes_stale_when_record_changes_root(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, b, c = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    stale_candidate = contract.propose_merge(b, c, "candidate"); winning = contract.propose_merge(a, b, "same"); mock_sources(direct_vm); mock_decision(direct_vm, "SAME_ENTITY", matched=["shared identity"]); contract.resolve_merge(winning); contract.resolve_merge(stale_candidate)
    assert json.loads(contract.proposal_of(stale_candidate))["status"] == "STALE"


def test_non_creator_cannot_deactivate_namespace(direct_deploy, direct_vm, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); namespace_id = create_namespace(contract, direct_vm, direct_alice); direct_vm.sender = direct_bob
    with direct_vm.expect_revert("EXPECTED"): contract.deactivate_namespace(namespace_id)


def test_stats_track_core_state(direct_deploy, direct_vm, direct_alice):
    contract = deploy(direct_deploy, direct_vm); _, a, b, _ = seed_three(contract, direct_vm, direct_alice); direct_vm.sender = direct_alice
    proposal_id = contract.propose_merge(a, b, "same"); mock_sources(direct_vm); mock_decision(direct_vm, "SAME_ENTITY", matched=["INC-42"]); contract.resolve_merge(proposal_id); stats = json.loads(contract.stats())
    assert stats["active_namespaces"] == "1" and stats["total_records"] == "3" and stats["canonical_clusters"] == "2" and stats["fused_proposals"] == "1"
