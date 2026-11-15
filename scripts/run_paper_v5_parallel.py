# Vai trò: Chạy Paper V5 trên ba slot độc lập, mỗi campaign một worker và mỗi lượt một job.
# Kiểm tra drift, integrity và trạng thái trước khi nhận thêm việc.
"""Run immutable Paper V5 campaigns in three isolated, one-job process slots."""
import argparse
import hashlib
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from paper_resource_guard import Sampler

from smart_retail.application.experiments.reports import report
from smart_retail.application.experiments.storage import read, verify_integrity, write
from smart_retail.contracts.experiments import CampaignSpec
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.workers.resources import is_alive

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / 'experiments/configs/paper-v5'
RESULTS = ROOT / 'experiments/results/paper-v5'
REPORTS = ROOT / 'experiments/reports/paper-v5'
ALLOWED = {'COMPLETED', 'EVALUATION_LIMIT', 'CONVERGED_LOCAL', 'ITERATION_LIMIT', 'NEIGHBORHOOD_EXHAUSTED'}
REVIEWED_TIMINGS = {}


# Hàm now: lấy thời điểm hiện tại theo cách chuẩn hóa trong hàm.
def now():
    return datetime.now(UTC).isoformat()


# Kiểm tra trạng thái, validation và thời gian của record trước khi tiếp nhận thêm job.
def inspect_records(spec, root):
    records = []
    for path in (root / 'records').glob('*.json'):
        r = read(path)
        records.append(r)
        if (r['status'] != 'SUCCEEDED' or r.get('joint_status') not in ALLOWED
                or r.get('validation', {}).get('status') != 'PASS'
                or r.get('evaluation_status') != 'COMPLETED'):
            raise RuntimeError(f"Job requires review: {root.name}/{r['run_id']}: {r['status']} {r.get('joint_status')}")
        if 'w1-medium' in root.name and r['wall_s'] >= 2430:
            key = f'{root.name}/records/{path.name}'
            reviewed = REVIEWED_TIMINGS.get(key)
            if (reviewed is None or not reviewed.get('reason')
                    or reviewed.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest()):
                raise RuntimeError(f"Medium wall near training limit: {r['run_id']} {r['wall_s']} s")
    if records and sum(r['wall_s'] for r in records) / len(records) * spec.max_jobs >= 0.9 * spec.max_wall_s:
        raise RuntimeError(f'Projected campaign wall near limit: {root.name}')
    return records


# Hàm main: điểm vào, đọc tùy chọn và điều phối các bước của công cụ.
def main():
    global CONFIGS, RESULTS, REPORTS, REVIEWED_TIMINGS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--configs', type=Path, default=CONFIGS)
    parser.add_argument('--results', type=Path, default=RESULTS)
    parser.add_argument('--reports', type=Path, default=REPORTS)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--timing-review', type=Path,
                        help='Explicit reviewed record hashes; new timing alerts still stop execution')
    args = parser.parse_args()
    REVIEWED_TIMINGS = read(args.timing_review)['records'] if args.timing_review else {}
    CONFIGS, RESULTS, REPORTS = (p.resolve() for p in (args.configs, args.results, args.reports))
    rows = read(CONFIGS / 'index.json')
    specs = {r['config']: CampaignSpec.model_validate(read(CONFIGS / r['config'])) for r in rows}
    assert len(rows) == 68 and sum(r['jobs'] for r in rows) == 1008
    # Chế độ này chỉ xác thực thiết kế và số job; chưa tạo worker hay chạy solver.
    if args.check_only:
        print({'campaigns': len(rows), 'jobs': 1008, 'slots': 3, 'workers_per_campaign': 1, 'slice_jobs': 1})
        return
    state = args.state.resolve()
    state.mkdir(parents=True, exist_ok=True)
    lock = state / 'runner.lock.json'
    if lock.exists() and is_alive(read(lock)['pid']):
        raise RuntimeError('Parallel coordinator already running')
    if any(is_alive(read(p)['pid']) for p in RESULTS.glob('*/.supervisor.lock')):
        raise RuntimeError('Previous campaign supervisors must drain first')
    write(lock, {'pid': os.getpid(), 'started_utc': now()})
    # Giữ nhận diện nguồn và dependency làm mốc để phát hiện thay đổi trong suốt đợt chạy.
    baseline = runtime_identity()
    config_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in CONFIGS.glob('*.json')}
    write(state / 'runtime.json', baseline)
    write(state / 'configs.json', config_hashes)
    sampler, slots, active, journal = Sampler(), 3, {}, []

    # Hàm event: xử lý bước event trong phạm vi module hiện tại.
    def event(**entry):
        journal.append({'utc': now(), **entry})
        write(state / 'journal.json', journal)
        print(now(), entry, flush=True)

    try:
        # Chạy khối ablation W2 trước so sánh chính W1 theo thứ tự thiết kế Paper V5.
        for block in ('W2', 'W1'):
            pending = []
            for row in (r for r in rows if r['block'] == block):
                spec = specs[row['config']]
                root = RESULTS / spec.name
                if root.exists():
                    integrity = verify_integrity(root)
                    inspect_records(spec, root)
                    event(action='RESUME_INTEGRITY_PASS', campaign=root.name, **integrity)
                if not (root / 'checkpoint.json').exists() or read(root / 'checkpoint.json')['status'] != 'COMPLETED':
                    pending.append(row)
            while pending or active:
                resources = sampler.sample()
                if runtime_identity() != baseline:
                    raise RuntimeError('Source/dependency drift; admission stopped')
                if any(hashlib.sha256((CONFIGS/n).read_bytes()).hexdigest() != h for n, h in config_hashes.items()):
                    raise RuntimeError('Configuration drift; admission stopped')
                stopping = (state / 'stop.request').exists()
                if (state / 'cancel.request').exists():
                    raise RuntimeError('Immediate stop requested')
                if stopping:
                    pending.clear()
                total, statuses = 0, Counter()
                for row in rows:
                    rs = inspect_records(specs[row['config']], RESULTS / specs[row['config']].name)
                    total += len(rs)
                    statuses.update(r['status'] for r in rs)
                for pid, item in list(active.items()):
                    code = item['process'].poll()
                    if code is None:
                        continue
                    item['stream'].close()
                    root, row = item['root'], item['row']
                    checkpoint = read(root / 'checkpoint.json')
                    verify_integrity(root)
                    for name, digest in item['before'].items():
                        if hashlib.sha256((root/'records'/name).read_bytes()).hexdigest() != digest:
                            raise RuntimeError('A completed record changed')
                    event(action='EXIT', campaign=root.name, pid=pid, exit_code=code, checkpoint=checkpoint)
                    del active[pid]
                    if code or checkpoint['status'] not in {'COMPLETED', 'PAUSED_PARTIAL'}:
                        raise RuntimeError(f'Campaign requires review: {root.name}; see {item["log"]}')
                    if checkpoint['status'] == 'PAUSED_PARTIAL' and not stopping:
                        pending.insert(0, row)
                while pending and len(active) < slots and not stopping:
                    row = pending.pop(0)
                    spec = specs[row['config']]
                    root = RESULTS / spec.name
                    assert all(item['root'] != root for item in active.values())
                    log = state / f'{spec.name}-{time.time_ns()}.log'
                    stream = log.open('xb')
                    command = [sys.executable, '-u', '-m', 'smart_retail.application.experiments.cli',
                               'resume' if root.exists() else 'run', '--config', str(CONFIGS/row['config']),
                               '--output', str(root), '--max-new-jobs', '1']
                    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'records').glob('*.json')}
                    process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream, stderr=stream,
                                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    active[process.pid] = {'process': process, 'stream': stream, 'root': root, 'row': row, 'before': before, 'log': str(log)}
                    event(action='START', campaign=spec.name, pid=process.pid, log=str(log))
                write(state/'status.json', {'status': 'DRAINING' if stopping else 'RUNNING', 'updated_utc': now(),
                      'coordinator_pid': os.getpid(), 'slots': slots, 'max_slots': 3, 'workers_per_campaign': 1,
                      'block': block, 'resources': resources, 'completed_records': total, 'record_statuses': dict(statuses),
                      'active': [{'pid': pid, 'campaign': v['root'].name} for pid,v in active.items()], 'pending': len(pending)})
                if active:
                    time.sleep(5)
            if (state/'stop.request').exists():
                write(state/'stopped.json', {'status': 'DRAINED_STOP', 'utc': now()})
                return
        for block in ('W2', 'W1'):
            roots = [RESULTS/specs[r['config']].name for r in rows if r['block'] == block]
            for root in roots:
                verify_integrity(root)
                assert read(root/'checkpoint.json')['status'] == 'COMPLETED'
            if not (REPORTS/block).exists():
                report(roots, REPORTS/block)
            event(action='VERIFIED_REPORTED', block=block)
        write(state/'finished.json', {'status': 'COMPLETED_INTEGRITY_VERIFIED', 'utc': now(), 'campaigns':68, 'jobs':1008})
        write(state/'status.json', read(state/'finished.json'))
    except BaseException as exc:
        write(state/'error.json', {'error': f'{type(exc).__name__}: {exc}', 'utc': now(), 'active_pids':list(active)})
        for pid, item in active.items():
            if item['process'].poll() is None:
                subprocess.run(['taskkill','/PID',str(pid),'/T','/F'],capture_output=True)
        write(state/'status.json', {'status':'STOPPED_NEEDS_REVIEW', 'utc':now(), 'error': f'{type(exc).__name__}: {exc}'})
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
