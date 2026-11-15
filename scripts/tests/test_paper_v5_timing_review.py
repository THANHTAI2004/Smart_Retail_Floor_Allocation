# Vai trò: Kiểm thử chỉ chấp nhận cảnh báo thời gian đã duyệt có đúng checksum, vẫn chặn kết quả sai.
# Các assertion mô tả hành vi mong đợi; kết quả chỉ được xác nhận sau khi chạy test.
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_paper_v5_parallel as runner  # noqa: E402


@pytest.fixture
# Hàm record: xử lý bước record trong phạm vi module hiện tại.
def record(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'REVIEWED_TIMINGS', {})
    root = tmp_path / 'paper-v5-w1-medium-part17'
    path = root / 'records/job.json'
    path.parent.mkdir(parents=True)
    value = {'status': 'SUCCEEDED', 'joint_status': 'EVALUATION_LIMIT',
             'validation': {'status': 'PASS'}, 'evaluation_status': 'COMPLETED',
             'wall_s': 2487.67, 'run_id': 'reviewed-job'}
    path.write_text(json.dumps(value))
    spec = SimpleNamespace(max_jobs=6, max_wall_s=28800)
    return root, path, value, spec


# Hàm approve: xử lý bước approve trong phạm vi module hiện tại.
def approve(root, path):
    runner.REVIEWED_TIMINGS[f'{root.name}/records/{path.name}'] = {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'reason': 'Reviewed completed full-budget run and independent validation',
    }


# Hàm test_default_still_stops: kiểm tra kịch bản default still stops bằng các assertion trong thân hàm.
def test_default_still_stops(record):
    root, _, _, spec = record
    with pytest.raises(RuntimeError, match='Medium wall'):
        runner.inspect_records(spec, root)


# Hàm test_exact_review_and_changed_record: kiểm tra kịch bản exact review and changed record bằng các assertion trong thân hàm.
def test_exact_review_and_changed_record(record):
    root, path, value, spec = record
    approve(root, path)
    assert runner.inspect_records(spec, root) == [value]
    value['wall_s'] += 1
    path.write_text(json.dumps(value))
    with pytest.raises(RuntimeError, match='Medium wall'):
        runner.inspect_records(spec, root)


@pytest.mark.parametrize('field,value', [('status', 'FAILED'),
                                        ('joint_status', 'SEARCH_TIME_LIMIT'),
                                        ('evaluation_status', 'FAILED'),
                                        ('validation', {'status': 'FAIL'})])
# Hàm test_review_does_not_bypass_invalid_outcomes: kiểm tra kịch bản review does not bypass invalid outcomes bằng các assertion trong thân hàm.
def test_review_does_not_bypass_invalid_outcomes(record, field, value):
    root, path, data, spec = record
    data[field] = value
    path.write_text(json.dumps(data))
    approve(root, path)
    with pytest.raises(RuntimeError, match='Job requires review'):
        runner.inspect_records(spec, root)


# Hàm test_new_record_still_stops: kiểm tra kịch bản new record still stops bằng các assertion trong thân hàm.
def test_new_record_still_stops(record):
    root, path, value, spec = record
    approve(root, path)
    (path.parent / 'new.json').write_text(json.dumps(value))
    with pytest.raises(RuntimeError, match='Medium wall'):
        runner.inspect_records(spec, root)


# Hàm test_campaign_limit_still_stops: kiểm tra kịch bản campaign limit still stops bằng các assertion trong thân hàm.
def test_campaign_limit_still_stops(record):
    root, path, _, spec = record
    approve(root, path)
    spec.max_wall_s = 10000
    with pytest.raises(RuntimeError, match='Projected campaign wall'):
        runner.inspect_records(spec, root)
