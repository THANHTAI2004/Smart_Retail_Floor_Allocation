"""Repair copied local aliases and operational paths; preserve scientific artifacts."""
import hashlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

import _winapi

ROOT = Path('E:/Smart_Retail_Floor_Allocation')
OLD = Path('D:/Smart_Retail_Floor_Allocation')
DATA = ROOT / 'thuc_nghiem'
BACKUP = Path('C:/Users/admin/Documents/SmartRetailBackups/20261024-E-relocation')
BACKUP.mkdir(parents=True, exist_ok=True)
changes = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path):
    relative = path.relative_to(ROOT)
    out = BACKUP / relative
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        shutil.copy2(path, out)
    assert sha(path) == sha(out), f'Previous snapshot conflicts: {path}'


def alias(relative, target):
    path = ROOT / relative
    assert target.resolve().is_relative_to(DATA.resolve()) and target.is_dir()
    if path.is_junction():
        assert path.resolve() == target.resolve()
        return
    if path.exists():
        assert not path.is_symlink()
        if any(path.iterdir()):
            preserved = DATA / 'migration/E-copy-legacy-directories' / relative
            assert not preserved.exists()
            preserved.parent.mkdir(parents=True, exist_ok=True)
            os.rename(path, preserved)
            changes.append({'preserved_nonempty_legacy_directory': str(preserved)})
        else:
            assert path.absolute().is_relative_to(ROOT)
            os.rmdir(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _winapi.CreateJunction(str(target), str(path))
    changes.append({'alias': str(path), 'target': str(target)})


def main():
    index_before = sha(ROOT / '.git/index')
    snapshot(ROOT / '.git/index')
    snapshot(ROOT / 'HANDOFF.md')
    for relative, target in [('experiments', DATA), ('docs/research', DATA/'docs/research'), ('scripts/paper_progress', DATA/'scripts/paper_progress')]:
        alias(relative, target)
    for path in (DATA/'runtime/var').iterdir():
        legacy=ROOT/'var'/path.name
        if path.is_dir():
            alias('var/'+path.name, path)
        elif legacy.exists():
            assert sha(legacy)==sha(path)
            snapshot(legacy)
            legacy.unlink()
            os.link(path,legacy)
    for path in (DATA/'scripts').glob('*.py'):
        legacy=ROOT/'scripts'/path.name
        if legacy.exists():
            assert sha(legacy)==sha(path), f'Different inherited script: {legacy}'
            snapshot(legacy)
            legacy.unlink()
            os.link(path, legacy)
    for path in (DATA/'scripts/tests').glob('test_*.py'):
        legacy=ROOT/'scripts/tests'/path.name
        if legacy.exists():
            assert sha(legacy)==sha(path)
            snapshot(legacy)
            legacy.unlink()
            os.link(path,legacy)
    for path in (ROOT/'.venv/Lib/site-packages').glob('*smart_retail*.pth'):
        snapshot(path)
        text=path.read_text(encoding='utf-8')
        updated=text.replace(str(OLD),str(ROOT)).replace(OLD.as_posix(),ROOT.as_posix())
        path.write_text(updated,encoding='utf-8')
        changes.append({'editable_install':str(path),'old_root':str(OLD),'new_root':str(ROOT)})
    operational = DATA/'runtime/var/paper-parallel/recovery/index.json'
    snapshot(operational)
    rows=json.loads(operational.read_text(encoding='utf-8'))
    for row in rows:
        row['config']=str(DATA/'runtime/var/paper-parallel/recovery/configs'/Path(row['config']).name)
        assert Path(row['config']).is_file()
    operational.write_text(json.dumps(rows,indent=2),encoding='utf-8')
    dashboard=DATA/'scripts/paper_progress/server.py'
    snapshot(dashboard)
    text=dashboard.read_text(encoding='utf-8')
    text=text.replace('ROOT = Path("D:/Smart_Retail_Floor_Allocation")', 'ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())')
    text=text.replace('RUNTIME = Path("C:/Users/admin/Documents/SmartRetailRuntime")','RUNTIME = ROOT / "thuc_nghiem/runtime/external"')
    dashboard.write_text(text,encoding='utf-8')
    guide=DATA/'VI_TRI_DU_LIEU.md'
    snapshot(guide)
    guide.write_text(guide.read_text(encoding='utf-8').replace(str(OLD),str(ROOT)),encoding='utf-8')
    assert sha(ROOT/'.git/index')==index_before
    receipt={'status':'OPERATIONAL_PATHS_RELOCATED','checked_utc':datetime.now(UTC).isoformat(),'project_root':str(ROOT),'previous_project_untouched':str(OLD),'scientific_artifacts':'UNCHANGED','index_sha256_before_and_after':index_before,'external_snapshot':str(BACKUP),'changes':changes}
    (DATA/'migration/E-relocation.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
