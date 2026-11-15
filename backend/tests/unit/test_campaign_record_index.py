# Kiểm tra thao tác đọc/so sánh bản ghi bằng tệp tạm; không dùng MongoDB hay worker.
import json

import pytest

from smart_retail.application.experiments import cli


# Tạo một record tối thiểu; các trường là dữ liệu giả của bài test.
def record(key, status="SUCCEEDED", *, digest="result", error=None):
    return {
        "job_key": key,
        "run_id": key,
        "status": status,
        "input_sha256": "input",
        "result_sha256": digest,
        "error": error,
    }


# Ghi fixture vào tmp_path; đây không phải khởi tạo campaign hay thực thi solver.
def write_record(root, filename, value, result=None):
    directory = root / "records"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / filename).write_text(json.dumps(value), encoding="utf-8")
    if result is not None:
        artifact = root / "artifacts" / value["run_id"]
        artifact.mkdir(parents=True, exist_ok=True)
        (artifact / "result.json").write_text(json.dumps(result), encoding="utf-8")


# Tách kiểm tra integrity khỏi fixture tối thiểu, đồng thời ghi lại thứ tự gọi.
@pytest.fixture
def verified(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "verify_integrity", lambda root: calls.append(root))
    return calls


# Hai thư mục không có record phải cho bảng rỗng, vẫn xác minh đủ hai phía.
def test_empty_records_keep_report_contract(tmp_path, verified):
    left, right = tmp_path / "left", tmp_path / "right"
    result = cli.compare(left, right)
    assert result["rows"] == []
    assert (result["atol"], result["rtol"]) == (1e-8, 1e-9)
    assert verified == [cli.normalize_fs_path(left), cli.normalize_fs_path(right)]


# Bảng cần giữ job chỉ có ở một phía và sắp theo job_key như trước.
def test_union_preserves_unmatched_jobs_and_sorted_rows(tmp_path, verified):
    left, right = tmp_path / "left", tmp_path / "right"
    write_record(left, "a.json", record("z"))
    write_record(right, "z.json", record("a"))
    rows = cli.compare(left, right)["rows"]
    assert rows == [
        {"job_key": "a", "present_in_both": False},
        {"job_key": "z", "present_in_both": False},
    ]


# Khác byte kết quả vẫn có thể tương đương số trong dung sai đã khai báo.
def test_success_retains_numeric_and_byte_comparisons(tmp_path, verified):
    left, right = tmp_path / "left", tmp_path / "right"
    write_record(left, "job.json", record("job", digest="one"), {"score": [1.0, True]})
    write_record(right, "job.json", record("job", digest="two"), {"score": [1.0 + 1e-10, True]})
    row = cli.compare(left, right)["rows"][0]
    # Byte identity và tương đương số là hai kết luận riêng.
    assert row["byte_identical_result"] is False
    assert row["numerically_equivalent"] is True
    assert row["same_input_hash"] is True and row["same_status"] is True


# Bao phủ cả mã lỗi giống nhau, khác nhau và thông tin lỗi vắng mặt.
@pytest.mark.parametrize(
    "left_error,right_error,same",
    [
        ({"code": "TIMEOUT"}, {"code": "TIMEOUT"}, True),
        ({"code": "TIMEOUT"}, {"code": "SEARCH_EXHAUSTED"}, False),
        (None, None, True),
    ],
)
def test_failed_records_keep_failure_codes(tmp_path, verified, left_error, right_error, same):
    left, right = tmp_path / "left", tmp_path / "right"
    write_record(left, "job.json", record("job", "FAILED", digest=None, error=left_error))
    write_record(right, "job.json", record("job", "FAILED", digest=None, error=right_error))
    row = cli.compare(left, right)["rows"][0]
    assert row["numerically_equivalent"] is None
    assert row["same_failure_code"] is same
    # Hai digest cùng None vẫn không phải cùng byte kết quả.
    assert row["byte_identical_result"] is False


# Giữ đúng chính sách khóa trùng: record đọc sau ghi đè record đọc trước.
def test_duplicate_key_keeps_existing_glob_order(tmp_path, verified):
    left, right = tmp_path / "left", tmp_path / "right"
    write_record(left, "first.json", record("same", "FAILED", error={"code": "ONE"}))
    # Giữ thứ tự glob thực tế, không tự thêm sorted vào refactor.
    write_record(left, "second.json", record("same", "FAILED", error={"code": "TWO"}))
    paths = list((left / "records").glob("*.json"))
    # Đọc fixture trực tiếp để không dùng helper mới làm oracle cho chính nó.
    expected = json.loads(paths[-1].read_text(encoding="utf-8"))
    write_record(right, "only.json", expected)
    assert cli.compare(left, right)["rows"][0]["same_failure_code"] is True


# Không nuốt KeyError của record hỏng vì sẽ làm thay đổi hành vi lỗi hiện có.
def test_invalid_record_keeps_key_error(tmp_path, verified):
    root = tmp_path / "left"
    write_record(root, "broken.json", {"run_id": "bad"})
    with pytest.raises(KeyError, match="job_key"):
        cli.compare(root, tmp_path / "right")


# Integrity phải thất bại trước bất kỳ lượt đọc record nào.
def test_integrity_failure_precedes_record_reads(tmp_path, monkeypatch):
    reads = []
    monkeypatch.setattr(cli, "read", lambda path: reads.append(path))

    # Lỗi giả đại diện checksum không hợp lệ, không đụng dữ liệu lịch sử.
    def reject(path):
        raise ValueError("integrity rejected")

    monkeypatch.setattr(cli, "verify_integrity", reject)
    with pytest.raises(ValueError, match="integrity rejected"):
        cli.compare(tmp_path / "left", tmp_path / "right")
    assert reads == []
