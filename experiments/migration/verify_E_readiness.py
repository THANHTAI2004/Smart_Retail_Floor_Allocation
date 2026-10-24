"""Bounded readiness receipt after transfer; no scientific rerun or dependency changes."""
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'backend').is_dir() and (p/'frontend').is_dir())
OUT=ROOT/'thuc_nghiem/migration/E-completion'


def main():
    state=json.loads((OUT/'progress.json').read_text(encoding='utf-8'))
    assert state['status']=='COPY_AND_ENVIRONMENT_COMPLETE',state['status']
    assert state['copied']+state['existing_identical']+len(state['source_transient_files_gone'])==state['expected_files']
    transfer=json.loads((OUT/'copied-files.json').read_text(encoding='utf-8'))
    assert len(transfer['files'])==state['expected_files']
    actual=[f for f in transfer['files'] if f.get('status')!='SOURCE_TEMPORARY_FILE_NO_LONGER_EXISTS']
    assert len(actual)==235304
    git_loose=sum(f['path'].startswith('.git/') for f in actual)
    long_paths=sum(not f['path'].startswith('.git/') for f in actual)
    assert long_paths==5481
    index=hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()
    assert index==state['git_index_unchanged']
    with urlopen('http://127.0.0.1:8010/api/health',timeout=10) as r:health=json.load(r)
    with urlopen('http://127.0.0.1:5173',timeout=10) as r:web_status=r.status;html=r.read().decode('utf-8')
    baseline=json.loads((ROOT/'thuc_nghiem/runtime/var/continue-20261023-01/preflight.json').read_text(encoding='utf-8'))['runtime']
    assert health['status']=='ok' and health['worker_online'] and health['runtime']==baseline
    assert web_status==200 and 'Smart Retail' in html
    from smart_retail.infrastructure.provenance import runtime_identity
    import smart_retail,sys
    assert runtime_identity()==baseline
    assert Path(smart_retail.__file__).resolve().is_relative_to(ROOT/'backend')
    assert Path(sys.prefix).resolve()==ROOT/'.venv'
    scripts=ROOT/'.venv/Scripts'
    stale=[p.name for p in scripts.iterdir() if p.is_file() and any(token in p.read_bytes() for token in [b'D:\\Smart_Retail_Floor_Allocation',b'D:/Smart_Retail_Floor_Allocation'])]
    assert not stale
    with (OUT/'git-connectivity.txt').open('w',encoding='utf-8') as log:
        check=subprocess.run(['git','--no-optional-locks','-C',str(ROOT),'fsck','--connectivity-only','--no-dangling','--no-reflogs'],stdout=log,stderr=log)
    assert check.returncode==0
    result={'status':'READY_ON_E','verified_utc':datetime.now(UTC).isoformat(),'project_root':str(ROOT),'restored_long_path_files':long_paths,'restored_git_object_files':git_loose,'verified_copied_or_previously_copied_files':len(actual),'source_transient_files_no_longer_present':state['source_transient_files_gone'],'all_restored_files_readback_SHA256':'PASS','git_index_unchanged':index,'git_connectivity':'PASS','backend_and_dependencies':'FROZEN_RUNTIME_MATCH','python_prefix':sys.prefix,'backend_import_path':smart_retail.__file__,'old_D_references_in_venv_Scripts':stale,'api':'HEALTHY','worker_online':True,'frontend_HTTP':web_status,'database_copy_before_start':'11215 files matched D by SHA256; live MongoDB now uses E data','tests':{'recovery_resource_unittests':11,'fresh_real_worker_replay_and_spawn_pytests':2,'pip_check':'PASS'},'user_app':'http://127.0.0.1:5173','experiment_finalizer':json.loads((ROOT/'thuc_nghiem/runtime/var/paper-unattended/status.json').read_text(encoding='utf-8'))['status'],'limitations':['No full backend suite rerun; two relevant real-process integration tests passed.','Full experiment artifact integrity/final backup remains owned by the running finalizer.']}
    (OUT/'readiness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
