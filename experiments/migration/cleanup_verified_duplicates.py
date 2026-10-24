"""Delete only byte-identical outside-E project copies. Never traverse reparse dirs."""
import ctypes
import hashlib
import itertools
import json
import os
import shutil
import stat
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

PRIMARY=Path('E:/Smart_Retail_Floor_Allocation')
SOURCES=[Path('C:/Users/admin/Documents/SmartRetailBackups'),Path('D:/Smart_Retail_Floor_Allocation')]
OUT=PRIMARY/'experiments/migration/duplicate-cleanup'
OUT.mkdir(parents=True,exist_ok=True)
LOCK=threading.Lock()
HASH_CACHE={}
PARENT_CACHE={}
E_DEVICE=PRIMARY.stat().st_dev
def disk_free_snapshot():
    values={}
    for drive in ['C:/','D:/','E:/']:
        try:values[drive]=shutil.disk_usage(drive).free
        except OSError:values[drive]=None
    return values

STATE={'started_utc':datetime.now(UTC).isoformat(),'status':'RUNNING','primary':str(PRIMARY),'source_roots':[str(p) for p in SOURCES],'checked':0,'deleted':0,'deleted_logical_bytes':0,'retained':0,'errors':0,'free_before':disk_free_snapshot()}
LAST_SAVE=0.0
LOG=None


def stamp(s):return s.st_size,s.st_mtime_ns,s.st_ino,s.st_dev
def extended(p):return '\\\\?\\'+str(p)


def save(force=False):
    global LAST_SAVE
    if force or time.monotonic()-LAST_SAVE>10:
        STATE['updated_utc']=datetime.now(UTC).isoformat()
        STATE['free_now']=disk_free_snapshot()
        p=OUT/'progress.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(STATE,indent=2),encoding='utf-8');t.replace(p)
        if LOG:LOG.flush()
        LAST_SAVE=time.monotonic()


def evidence(row):
    with LOCK:
        LOG.write(json.dumps(row,ensure_ascii=True,separators=(',',':'))+'\n')
        STATE['checked']+=1
        if row['action']=='DELETED':STATE['deleted']+=1;STATE['deleted_logical_bytes']+=row['bytes']
        else:STATE['retained']+=1
        if row['action']=='ERROR':STATE['errors']+=1
        save()


def hash_file(path):
    h=hashlib.sha256()
    with open(extended(path),'rb') as stream:
        before=os.fstat(stream.fileno())
        while block:=stream.read(1024*1024):h.update(block)
        after=os.fstat(stream.fileno())
    if stamp(before)!=stamp(after):raise RuntimeError('File changed while hashing')
    return h.hexdigest(),after


def primary_digest(path):
    parent=str(path.parent)
    with LOCK:resolved=PARENT_CACHE.get(parent)
    if resolved is None:
        resolved=path.parent.resolve()
        if not resolved.is_relative_to(PRIMARY):raise RuntimeError('Target resolves outside primary E project')
        with LOCK:PARENT_CACHE[parent]=resolved
    path=resolved/path.name
    current=os.stat(extended(path),follow_symlinks=False)
    if current.st_file_attributes & 0x400 or current.st_dev!=E_DEVICE:raise RuntimeError('Target is not an independent regular file on E')
    key=str(path)
    with LOCK:cached=HASH_CACHE.get(key)
    if cached and cached[0]==stamp(current):return path,cached[1],current
    digest,after=hash_file(path)
    with LOCK:HASH_CACHE[key]=(stamp(after),digest)
    return path,digest,after


def rebase(relative):
    parts=relative.parts
    if parts and parts[0]=='thuc_nghiem':return PRIMARY/'experiments'/Path(*parts[1:])
    return PRIMARY/relative


def candidates(root,path):
    rel=path.relative_to(root)
    if root.drive.upper()=='D:':return [rebase(rel)]
    parts=rel.parts
    if len(parts)<2:return []
    group=parts[0];tail=Path(*parts[1:]);bits=tail.parts
    if group=='20261024-consolidation':
        if bits[0]=='paper-v2-results-original':return [PRIMARY/'experiments/results/20261023-paper-v2'/Path(*bits[1:])]
        if bits[0]=='runtime-original':return [PRIMARY/'experiments/runtime/external'/Path(*bits[1:])]
        if tail.name=='progress.json':return [PRIMARY/'experiments/migration/consolidation.json']
        if tail.name.endswith('.json') and (tail.name.startswith('paper-') or tail.name.startswith('external-')):return [PRIMARY/'experiments/migration/receipts'/tail.name]
        if tail.name in ['consolidate.py','export_databases.py']:return [PRIMARY/'experiments/migration'/tail.name]
    if group.startswith('20261024-E-') or group=='20261024-experiments-single-root':return [rebase(tail)]
    return [rebase(tail),PRIMARY/'experiments/runtime/external'/group/tail]


def walk(root):
    def scan_error(exc):
        evidence({'source':str(getattr(exc,'filename',root)),'action':'ERROR','reason':'SCAN_ERROR','error':str(exc)})
    for folder,dirs,files in os.walk(extended(root),followlinks=False,onerror=scan_error):
        kept=[]
        for name in dirs:
            p=Path(folder)/name
            try:
                if not p.stat(follow_symlinks=False).st_file_attributes & 0x400:kept.append(name)
            except FileNotFoundError:pass
        dirs[:]=kept
        for name in files:
            p=Path(str(Path(folder)/name).removeprefix('\\\\?\\'))
            if p.absolute().is_relative_to(root) and p.drive.upper()!='E:':yield root,p


def one(item):
    root,source=item
    row={'source':str(source),'action':'RETAINED','reason':'NO_MATCHING_E_FILE'}
    try:
        assert source.absolute().is_relative_to(root) and root in SOURCES and source.drive.upper()!='E:'
        before=os.stat(extended(source),follow_symlinks=False)
        if before.st_file_attributes & 0x400:row['reason']='SOURCE_REPARSE_POINT';evidence(row);return
        options=[p for p in candidates(root,source) if p.is_absolute() and p.is_relative_to(PRIMARY)]
        for target in options:
            try:dest_stat=os.stat(extended(target),follow_symlinks=False)
            except FileNotFoundError:continue
            if dest_stat.st_size!=before.st_size:row['reason']='DIFFERENT_SIZE_OR_VERSION';continue
            target,dest_hash,dest_after=primary_digest(target)
            source_hash,source_after=hash_file(source)
            if source_hash!=dest_hash:row['reason']='DIFFERENT_CONTENT_OR_VERSION';continue
            if stamp(os.stat(extended(source),follow_symlinks=False))!=stamp(source_after) or stamp(os.stat(extended(target),follow_symlinks=False))!=stamp(dest_after):
                row['reason']='FILE_CHANGED_BEFORE_DELETE';break
            # The confirmed counterpart on E is the recoverable copy; delete only this source file.
            for attempt in range(4):
                if stamp(os.stat(extended(source),follow_symlinks=False))!=stamp(source_after) or stamp(os.stat(extended(target),follow_symlinks=False))!=stamp(dest_after):
                    row['reason']='FILE_CHANGED_DURING_DELETE_RETRY';evidence(row);return
                try:os.unlink(extended(source));break
                except PermissionError:
                    if attempt==3:raise
                    if before.st_file_attributes & 1:os.chmod(extended(source),stat.S_IWRITE|stat.S_IREAD)
                    time.sleep(0.2*(attempt+1))
            row.update(action='DELETED',reason='SHA256_EQUAL',target=str(target),sha256=dest_hash,bytes=before.st_size)
            evidence(row);return
        evidence(row)
    except FileNotFoundError:
        row['reason']='SOURCE_OR_TARGET_CHANGED_OR_GONE';evidence(row)
    except Exception as exc:
        row.update(action='ERROR',reason=type(exc).__name__,error=str(exc));evidence(row)


def main():
    global LOG
    assert PRIMARY==Path.cwd().resolve() and PRIMARY.drive.upper()=='E:'
    active=[p for p in SOURCES if p.is_dir() and not p.is_junction()]
    assert all(p.drive.upper()!='E:' for p in SOURCES)
    prior_retained=set()
    progress=OUT/'progress.json'
    if progress.exists():
        previous=json.loads(progress.read_text(encoding='utf-8'))
        if previous.get('status')=='NEEDS_ATTENTION' and (OUT/'file-actions.jsonl').exists():
            STATE.update(previous);STATE.update(status='RUNNING',resumed_utc=datetime.now(UTC).isoformat());STATE.pop('error',None)
            with (OUT/'file-actions.jsonl').open(encoding='utf-8') as old:
                for line in old:
                    record=json.loads(line)
                    if record['action'] in ('RETAINED','ERROR'):prior_retained.add(record['source'])
    STATE['missing_source_roots_skipped']=[str(p) for p in SOURCES if p not in active]
    index=hashlib.sha256((PRIMARY/'.git/index').read_bytes()).hexdigest()
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:
        with (OUT/'file-actions.jsonl').open('a',encoding='utf-8') as stream:
            LOG=stream;save(True)
            with ThreadPoolExecutor(max_workers=8) as pool:
                for root in active:
                    STATE['current_root']=str(root)
                    iterator=(item for item in walk(root) if str(item[1]) not in prior_retained)
                    while batch:=list(itertools.islice(iterator,512)):
                        list(pool.map(one,batch))
                        with LOCK:save(True)
        STATE.update(status='FINISHED_WITH_RETAINED_NONIDENTICAL_FILES',ended_utc=datetime.now(UTC).isoformat(),primary_git_index_before=index,primary_git_index_after=hashlib.sha256((PRIMARY/'.git/index').read_bytes()).hexdigest())
        LOG=None;save(True)
        print(json.dumps(STATE,indent=2),flush=True)
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        LOG=None
        STATE.update(status='NEEDS_ATTENTION',error=traceback.format_exc());save(True);raise
