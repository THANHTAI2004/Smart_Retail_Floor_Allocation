from smart_retail.application.workflow import canonical_hash, execute


def test_whole_baseline_reproduces_exactly(sample):
    first = execute(sample)
    second = execute(sample)
    assert canonical_hash(first) == canonical_hash(second)
    assert set(first["stages"]) == {"T1", "T2", "T3", "T4"}
    assert first["stages"]["T2"]["status"] == "OPTIMAL"
    assert first["input_sha256"] == canonical_hash(sample)
