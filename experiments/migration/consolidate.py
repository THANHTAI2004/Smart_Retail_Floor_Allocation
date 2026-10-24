"""Verified experiment consolidation. Originals remain in an external recovery snapshot."""

import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import _winapi

ROOT = Path('D:/Smart_Retail_Floor_Allocation')
DEST = ROOT / 'thuc_nghiem'
EXTERNAL = Path('C:/Users/admin/Documents/SmartRetailRuntime')
SNAPSHOT = Path(__file__).parent
JOURNAL = SNAPSHOT / 'progress.json'
mutex = threading.Lock()
state = {'started_utc': datetime.now(UTC).isoformat(), 'status': 'PREPARING', 'campaigns': [], 'verified_files': 0, 'verified_bytes': 0}
last_write = 0.0


def save(force=False):
    global last_write
    if force or time.monotonic() - last_write > 10:
        state['updated_utc'] = datetime.now(UTC).isoformat()
        tmp = JOURNAL.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, indent=2), encoding='utf-8')
        tmp.replace(JOURNAL)
        last_write = time.monotonic()


def junction(link, target):
    if link.is_junction():
        assert link.resolve() == target.resolve(), (link, target)
        return
    assert not link.exists(), link
    _winapi.CreateJunction(str(target), str(link))


def confined_move(source, target, allowed_source, allowed_target):
    assert source.absolute().is_relative_to(allowed_source.absolute())
    assert target.absolute().is_relative_to(allowed_target.absolute())
    assert not source.is_junction() and not source.is_symlink()
    assert not target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    os.rename(source, target)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while data := stream.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()


def list_files(root):
    files = []
    folders = []
    for folder, dirs, names in os.walk(root, followlinks=False):
        folders.append(Path(folder).relative_to(root))
        for name in dirs:
            p = Path(folder) / name
            if p.is_junction() or p.is_symlink():
                raise RuntimeError(f'Unexpected internal reparse point: {p}')
        for name in names:
            p = Path(folder) / name
            if p.is_symlink():
                raise RuntimeError(f'Unexpected file symlink: {p}')
            files.append(p)
    return files, folders


def compressed_directory(path):
    path.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(['compact.exe', '/C', '/I', '/Q', str(path)], capture_output=True)
    if result.returncode or not (path.stat().st_file_attributes & 0x800):
        raise RuntimeError(f'Cannot enable transparent NTFS compression: {path}')


def verified_copy(source, target, receipt_name):
    compressed_directory(target)
    files, directories = list_files(source)
    for relative in sorted(directories, key=lambda p: len(p.parts)):
        (target / relative).mkdir(parents=True, exist_ok=True)
    state.update(status='COPYING_AND_VERIFYING', source=str(source), target=str(target), source_files=len(files))
    save(True)
    def one(path):
        relative = path.relative_to(source)
        output = target / relative
        stat = path.stat()
        if output.exists():
            if output.stat().st_size != stat.st_size or sha(path) != sha(output):
                raise RuntimeError(f'Existing staged file differs: {output}')
            digest = sha(output)
        else:
            if stat.st_size > 1024**2 and shutil.disk_usage(DEST).free < 5 * 1024**3:
                raise RuntimeError('D: available space below 5 GiB; originals preserved')
            temporary = output.with_name(output.name + '.migration-copy')
            h = hashlib.sha256()
            with path.open('rb') as src, temporary.open('xb') as dst:
                while data := src.read(1024 * 1024):
                    h.update(data)
                    dst.write(data)
            digest = h.hexdigest()
            if temporary.stat().st_size != stat.st_size or sha(temporary) != digest:
                raise RuntimeError(f'Copied data checksum mismatch: {temporary}')
            os.utime(temporary, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            os.rename(temporary, output)
        with mutex:
            state['verified_files'] += 1
            state['verified_bytes'] += stat.st_size
            save()
        return relative.as_posix(), {'bytes': stat.st_size, 'sha256': digest}
    with ThreadPoolExecutor(max_workers=8) as pool:
        manifest = dict(pool.map(one, files, chunksize=16))
    receipt = DEST / 'migration' / 'receipts' / (receipt_name + '.json')
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({'source': str(source), 'destination': str(target), 'files': manifest}, separators=(',', ':')), encoding='utf-8')
    shutil.copy2(receipt, SNAPSHOT / receipt.name)
    return {'files': len(files), 'bytes': sum(x['bytes'] for x in manifest.values()), 'receipt': str(receipt), 'manifest_sha256': sha(receipt)}


def move_directory_with_alias(source, destination):
    if source.is_junction():
        assert source.resolve() == destination.resolve()
        return
    confined_move(source, destination, ROOT, DEST)
    junction(source, destination)


def move_file_with_alias(source, destination):
    assert source.is_file() and not destination.exists()
    destination.parent.mkdir(parents=True, exist_ok=True)
    before = sha(source)
    os.rename(source, destination)
    os.link(destination, source)
    assert sha(source) == sha(destination) == before


def main():
    awake = bool(ctypes.windll.kernel32.SetThreadExecutionState(0x80000001))
    if not awake:
        raise RuntimeError('Keep-awake request failed')
    try:
        assert ROOT.is_dir() and (ROOT / 'backend').is_dir()
        if DEST.exists():
            assert not any(DEST.iterdir()), 'Destination must initially be empty; never overwrite inherited work'
            os.rmdir(DEST)
        # Same-volume atomic move; no file contents rewritten.
        confined_move(ROOT / 'experiments', DEST, ROOT, ROOT)
        junction(ROOT / 'experiments', DEST)
        (DEST / 'migration').mkdir()
        shutil.copy2(Path(__file__), DEST / 'migration' / 'consolidate.py')
        compressed_directory(DEST / '.migration-staging')
        campaign_parent = DEST / 'results/20261023-paper-v2'
        original_parent = EXTERNAL / 'paper-v2-results'
        names = sorted(p.name for p in original_parent.iterdir() if p.is_dir())
        for name in names:
            source = original_parent / name
            final = campaign_parent / name
            assert final.is_junction() and final.resolve() == source.resolve()
            staged = DEST / '.migration-staging' / name
            verified = verified_copy(source, staged, name)
            # os.rmdir removes this junction itself, never its C: target.
            assert final.absolute().is_relative_to(campaign_parent.absolute()) and final.is_junction()
            os.rmdir(final)
            os.rename(staged, final)
            state['campaigns'].append({'campaign': name, 'destination': str(final), **verified})
            save(True)
            print(json.dumps({'campaign_verified_and_relocated': name, **verified}), flush=True)
        # Preserve the verified external originals as a recoverable backup.
        confined_move(original_parent, SNAPSHOT / 'paper-v2-results-original', EXTERNAL, SNAPSHOT)
        junction(original_parent, campaign_parent)
        # The remaining external runtime files are small; avoid duplicating the junction.
        external_copy = DEST / 'runtime/external'
        compressed_directory(external_copy)
        stats = []
        for item in sorted(EXTERNAL.iterdir()):
            if item.name == 'paper-v2-results':
                continue
            if item.is_dir():
                stats.append(verified_copy(item, external_copy / item.name, 'external-' + item.name))
            elif item.is_file():
                target = external_copy / item.name
                shutil.copy2(item, target)
                assert sha(item) == sha(target)
        state['external_runtime_copies'] = stats
        junction(external_copy / 'paper-v2-results', campaign_parent)
        # Retire the old external runtime as a named backup, then retain its path as an alias.
        os.rmdir(EXTERNAL / 'paper-v2-results')
        confined_move(EXTERNAL, SNAPSHOT / 'runtime-original', EXTERNAL.parent, SNAPSHOT)
        junction(EXTERNAL, external_copy)
        var = ROOT / 'var'
        for item in list(var.iterdir()):
            if item.name == 'continue-20261023-01' or item.name.startswith('paper-'):
                target = DEST / 'runtime/var' / item.name
                if item.is_dir():
                    move_directory_with_alias(item, target)
                else:
                    move_file_with_alias(item, target)
        move_directory_with_alias(ROOT / 'docs/research', DEST / 'docs/research')
        scripts = ['build_paper_configs.py', 'check_experiment_readiness.py', 'paper_recovery.py', 'paper_resource_guard.py', 'run_paper_campaigns.py', 'run_paper_parallel.py', 'summarize_paper_results.py', 'verify_experiment_release.py', 'watch_paper_campaigns.py']
        for name in scripts:
            move_file_with_alias(ROOT / 'scripts' / name, DEST / 'scripts' / name)
        move_directory_with_alias(ROOT / 'scripts/paper_progress', DEST / 'scripts/paper_progress')
        for name in ['test_paper_recovery.py', 'test_paper_resource_guard.py']:
            move_file_with_alias(ROOT / 'scripts/tests' / name, DEST / 'scripts/tests' / name)
        for path in [DEST / 'run_campaign.py', *list((DEST / 'scripts').glob('*.py')), *list((DEST / 'scripts/tests').glob('*.py'))]:
            text = path.read_text(encoding='utf-8')
            for old in ['ROOT = Path(__file__).resolve().parents[1]', 'ROOT = Path(__file__).resolve().parents[2]']:
                if old in text:
                    # Write in place so the old hard-link alias keeps the same contents.
                    text = text.replace(old, 'ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())')
            path.write_text(text, encoding='utf-8')
        shutil.copy2(JOURNAL, DEST / 'migration' / 'copy-progress.json')
        state.update(status='FILES_CONSOLIDATED', ended_utc=datetime.now(UTC).isoformat(), external_backup=str(SNAPSHOT), primary=str(DEST))
        save(True)
        shutil.copy2(JOURNAL, DEST / 'migration' / 'consolidation.json')
        print('FILES_CONSOLIDATED', flush=True)
    except Exception:
        import traceback
        state.update(status='NEEDS_ATTENTION', error=traceback.format_exc())
        save(True)
        raise
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__ == '__main__':
    main()
