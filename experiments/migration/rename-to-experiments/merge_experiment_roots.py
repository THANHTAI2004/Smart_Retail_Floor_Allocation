"""Rename the single physical experiment root; no artifact copy or overwrite."""
import hashlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

import _winapi

ROOT=Path('E:/Smart_Retail_Floor_Allocation')
OLD=ROOT/'thuc_nghiem'
NEW=ROOT/'experiments'
SNAPSHOT=Path('C:/Users/admin/Documents/SmartRetailBackups/20261024-experiments-single-root')
SNAPSHOT.mkdir(parents=True,exist_ok=True)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path):
    target=SNAPSHOT/path.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target)
    assert sha(path)==sha(target)


def main():
    assert OLD.is_dir() and not OLD.is_junction()
    assert NEW.is_junction() and NEW.resolve()==OLD.resolve()
    index_before=sha(ROOT/'.git/index');snapshot(ROOT/'.git/index')
    for path in [ROOT/'.gitignore',ROOT/'HANDOFF.md',OLD/'README.md',OLD/'VI_TRI_DU_LIEU.md']:
        snapshot(path)
    active_files=list((OLD/'scripts').rglob('*.py'))+list((OLD/'docs/research').glob('*.md'))
    for path in active_files:
        if 'thuc_nghiem' in path.read_text(encoding='utf-8'):snapshot(path)
    operational=OLD/'runtime/var/paper-parallel/recovery/index.json';snapshot(operational)
    for path in [OLD/'runtime/var/paper-unattended/status.json',OLD/'runtime/var/paper-unattended/process.json',OLD/'runtime/var/paper-unattended/watcher.lock.json',OLD/'runtime/external/progress/process.json']:
        if path.exists():snapshot(path)
    old_links=json.loads((OLD/'migration/audit-D-to-E-20261024T093214Z/summary.json').read_text(encoding='utf-8'))['links']['E']
    assert NEW.parent==ROOT and NEW.is_junction()
    os.rmdir(NEW)  # Remove this junction only; it does not remove its target.
    assert OLD.parent==ROOT and not NEW.exists()
    os.rename(OLD,NEW)  # Same-volume atomic rename; all file contents stay in place.
    redirected=[]
    for item in old_links:
        if item['path']=='experiments':continue
        link=ROOT/item['path'];previous=Path(item['resolved_target'])
        assert previous.is_relative_to(OLD)
        target=NEW/previous.relative_to(OLD)
        assert link.absolute().is_relative_to(ROOT) and link.is_junction() and target.is_dir()
        os.rmdir(link);_winapi.CreateJunction(str(target),str(link))
        redirected.append({'path':str(link),'target':str(target)})
    edits=[]
    for previous in active_files:
        path=NEW/previous.relative_to(OLD)
        text=path.read_text(encoding='utf-8')
        if 'thuc_nghiem' in text:
            path.write_text(text.replace('thuc_nghiem','experiments'),encoding='utf-8')
            edits.append(str(path))
    guide=NEW/'VI_TRI_DU_LIEU.md'
    guide.write_text(guide.read_text(encoding='utf-8').replace('thuc_nghiem','experiments'),encoding='utf-8')
    op=NEW/'runtime/var/paper-parallel/recovery/index.json'
    rows=json.loads(op.read_text(encoding='utf-8'))
    for row in rows:
        row['config']=str(NEW/'runtime/var/paper-parallel/recovery/configs'/Path(row['config']).name)
        assert Path(row['config']).is_file()
    op.write_text(json.dumps(rows,indent=2),encoding='utf-8')
    ignore=ROOT/'.gitignore'
    lines=ignore.read_text(encoding='utf-8').splitlines()
    lines=[line for line in lines if not line.startswith('/thuc_nghiem/')]
    ignore.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # Small top-level hash/namespace receipts may record historic paths; never rewrite them.
    receipt={'status':'SINGLE_EXPERIMENTS_ROOT','completed_utc':datetime.now(UTC).isoformat(),'project':str(ROOT),'canonical_root':str(NEW),'previous_name_absent':not OLD.exists(),'operation':'Same-volume rename, no scientific artifact contents rewritten','redirected_local_aliases':redirected,'active_files_updated':edits,'config_paths_updated':len(rows),'external_prechange_snapshot':str(SNAPSHOT),'git_index_sha256_before':index_before,'git_index_sha256_after':sha(ROOT/'.git/index')}
    assert receipt['git_index_sha256_before']==receipt['git_index_sha256_after']
    assert not OLD.exists() and NEW.is_dir() and not NEW.is_junction()
    out=NEW/'migration/rename-to-experiments';out.mkdir(parents=True,exist_ok=True)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    shutil.copy2(Path(__file__),out/'merge_experiment_roots.py')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
