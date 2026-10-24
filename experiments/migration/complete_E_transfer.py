"""Fill audited gaps and regenerate E-local Python launchers without changing packages."""
import csv
import hashlib
import importlib.metadata
import json
import os
import shutil
import threading
import time
import venv
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

ROOT=Path('E:/Smart_Retail_Floor_Allocation')
OLD=Path('D:/Smart_Retail_Floor_Allocation')
AUDIT=ROOT/'thuc_nghiem/migration/audit-D-to-E-20261024T093214Z'
OUT=ROOT/'thuc_nghiem/migration/E-completion'
BACKUP=Path('C:/Users/admin/Documents/SmartRetailBackups/20261024-E-completion')
OUT.mkdir(parents=True,exist_ok=True);BACKUP.mkdir(parents=True,exist_ok=True)
state={'started_utc':datetime.now(UTC).isoformat(),'status':'PREPARING','copied':0,'existing_identical':0,'verified_bytes':0}
state['source_transient_files_gone']=[]
mutex=threading.Lock();last_saved=0.0


def write(name,data):
    p=OUT/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(data,indent=2),encoding='utf-8');t.replace(p)


def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as stream:
        while data:=stream.read(1024*1024):h.update(data)
    return h.hexdigest()


def snapshot(path):
    dst=BACKUP/path.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(path,dst)
    assert digest(path)==digest(dst),str(path)


def windows_path(path):return '\\\\?\\'+str(path)


def repair_environment():
    if (OUT/'environment.json').exists():
        assert all(str(OLD).encode() not in p.read_bytes() for p in (ROOT/'.venv/Scripts').iterdir() if p.is_file())
        return
    from pip._vendor.distlib.scripts import ScriptMaker
    env=ROOT/'.venv';scripts=env/'Scripts'
    for p in scripts.iterdir():
        if p.is_file():snapshot(p)
    snapshot(env/'pyvenv.cfg')
    builder=venv.EnvBuilder(with_pip=False)
    context=builder.ensure_directories(str(env));builder.create_configuration(context);builder.setup_scripts(context)
    maker=ScriptMaker(None,str(scripts));maker.executable=str(scripts/'python.exe');maker.clobber=True;maker.variants={''}
    generated=[]
    for dist in importlib.metadata.distributions():
        for ep in dist.entry_points:
            if ep.group in ('console_scripts','gui_scripts'):
                generated+=maker.make(f'{ep.name} = {ep.value}',options={'gui':ep.group=='gui_scripts'})
    for name in ['pip3.12']:
        if (scripts/(name+'.exe')).exists():generated+=maker.make(name+' = pip._internal.cli.main:main')
    for path in (env/'Lib/site-packages').glob('smart_retail-*.dist-info/direct_url.json'):
        snapshot(path);data=json.loads(path.read_text(encoding='utf-8'));data['url']=(ROOT/'backend').as_uri();path.write_text(json.dumps(data),encoding='utf-8')
    old_root=str(OLD).encode()
    stale=[p.name for p in scripts.iterdir() if p.is_file() and old_root in p.read_bytes()]
    assert not stale,stale
    write('environment.json',{'status':'E_LOCAL_LAUNCHERS_REGENERATED','entrypoint_outputs':generated,'stale_D_references_in_Scripts':stale,'libraries':'UNCHANGED','original_scripts_snapshot':str(BACKUP/'.venv/Scripts')})


def copy_one(row):
    global last_saved
    relative=Path(row['path']);assert not relative.is_absolute() and '..' not in relative.parts
    src=windows_path(OLD/relative);dst=windows_path(ROOT/relative)
    try:expected=digest(src)
    except FileNotFoundError:
        if relative.parts[:2]==('.git','objects') and relative.name.startswith('tmp_'):
            with mutex:state['source_transient_files_gone'].append(row['path'])
            return {'path':row['path'],'status':'SOURCE_TEMPORARY_FILE_NO_LONGER_EXISTS'}
        raise
    existed=os.path.exists(dst)
    if existed:assert digest(dst)==expected,f'Existing different file: {relative}'
    else:
        if shutil.disk_usage(ROOT).free<5*1024**3:raise RuntimeError('Less than 5 GiB available; original D intact')
        os.makedirs(os.path.dirname(dst),exist_ok=True)
        temporary=dst+'.E-copying'
        with open(src,'rb') as a,open(temporary,'xb') as b:
            shutil.copyfileobj(a,b,1024*1024)
        assert digest(temporary)==expected
        # Atomic no-clobber publication; another creator is checked rather than overwritten.
        try:os.link(temporary,dst)
        except FileExistsError:assert digest(dst)==expected
        os.unlink(temporary)
    with mutex:
        state['existing_identical' if existed else 'copied']+=1;state['verified_bytes']+=int(row['bytes'])
        if time.monotonic()-last_saved>10:write('progress.json',state);last_saved=time.monotonic()
    return {'path':row['path'],'bytes':int(row['bytes']),'sha256':expected}


def main():
    index_before=digest(ROOT/'.git/index');snapshot(ROOT/'.git/index')
    repair_environment();state['status']='COPYING_AUDITED_GAPS';write('progress.json',state)
    with (AUDIT/'missing-on-E.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    with (AUDIT/'long-path-missing.csv').open(encoding='utf-8-sig',newline='') as f:rows+=list(csv.DictReader(f))
    assert len({r['path'] for r in rows})==len(rows)
    with ThreadPoolExecutor(max_workers=8) as pool:verified=list(pool.map(copy_one,rows,chunksize=32))
    assert digest(ROOT/'.git/index')==index_before
    write('copied-files.json',{'files':verified,'original_D':'UNMODIFIED'})
    state.update(status='COPY_AND_ENVIRONMENT_COMPLETE',ended_utc=datetime.now(UTC).isoformat(),expected_files=len(rows),git_index_unchanged=index_before)
    write('progress.json',state);print(json.dumps(state,indent=2),flush=True)


if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        state.update(status='NEEDS_ATTENTION',error=traceback.format_exc());write('progress.json',state);raise
