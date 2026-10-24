"""Finish duplicate cleanup: match retained files by verified content and remove empty dirs."""
import ctypes
import importlib.util
import json
import os
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT=Path('E:/Smart_Retail_Floor_Allocation')
OUT=ROOT/'experiments/migration/duplicate-cleanup'


def save(data):
    p=OUT/'completion.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(data,indent=2),encoding='utf-8');t.replace(p)


def main():
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    while True:
        state=json.loads((OUT/'progress.json').read_text(encoding='utf-8'))
        if state['status']=='NEEDS_ATTENTION':save({'status':'NEEDS_ATTENTION','primary_worker':state});return
        if state['status'].startswith('FINISHED'):break
        time.sleep(30)
    save({'status':'MATCHING_RETAINED_FILES_BY_CONTENT','primary_worker':state})
    reverse={};sizes=set();retained={}
    with (OUT/'file-actions.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            r=json.loads(line)
            if r['action']=='DELETED':
                reverse.setdefault((r['bytes'],r['sha256']),r['target']);sizes.add(r['bytes'])
            elif r['action']=='RETAINED':retained[r['source']]=r
    script=ROOT/'experiments/migration/cleanup_verified_duplicates.py'
    spec=importlib.util.spec_from_file_location('post_cleanup_verified_engine',script)
    engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    engine.OUT=OUT/'post-pass';engine.OUT.mkdir(exist_ok=True)
    mappings={}
    engine.candidates=lambda root,path:[mappings[str(path)]] if str(path) in mappings else []
    with (engine.OUT/'file-actions.jsonl').open('w',encoding='utf-8') as log:
        engine.LOG=log
        for source in retained:
            path=Path(source)
            try:
                st=os.stat(engine.extended(path),follow_symlinks=False)
                if st.st_file_attributes & 0x400 or st.st_size not in sizes:continue
                digest,_=engine.hash_file(path)
                target=reverse.get((st.st_size,digest))
                if not target:continue
                root=next((p for p in engine.SOURCES if path.is_relative_to(p)),None)
                if root is None:continue
                mappings[str(path)]=Path(target)
                engine.one((root,path))
            except (FileNotFoundError,PermissionError):continue
        engine.LOG=None;engine.save(True)
    # Empty-only removal with checked absolute roots; never follow junctions.
    removed_dirs=0;directory_errors=[]
    for source_root in engine.SOURCES:
        if not source_root.is_dir():continue
        stack=[(source_root,False)]
        while stack:
            directory,visited=stack.pop()
            assert directory.absolute().is_relative_to(source_root) and directory.drive.upper()!='E:'
            try:
                attrs=os.stat(engine.extended(directory),follow_symlinks=False).st_file_attributes
                if attrs & 0x400:continue
                if visited:
                    try:os.rmdir(engine.extended(directory));removed_dirs+=1
                    except OSError:pass  # Nonempty directories retain unique/unproven files.
                else:
                    stack.append((directory,True))
                    with os.scandir(engine.extended(directory)) as it:
                        for entry in it:
                            st=entry.stat(follow_symlinks=False)
                            if entry.is_dir(follow_symlinks=False) and not st.st_file_attributes & 0x400:
                                stack.append((Path(entry.path.removeprefix('\\\\?\\')),False))
            except OSError as exc:directory_errors.append({'path':str(directory),'error':str(exc)})
    after=engine.disk_free_snapshot()
    result={'status':'FINISHED_WITH_UNIQUE_OR_UNPROVEN_FILES_RETAINED','ended_utc':datetime.now(UTC).isoformat(),'primary_worker':state,'additional_duplicates_deleted':engine.STATE['deleted'],'additional_logical_bytes_deleted':engine.STATE['deleted_logical_bytes'],'empty_directories_removed':removed_dirs,'directory_errors':directory_errors,'free_after':after,'free_change_since_start':{p:after[p]-state['free_before'][p] if after[p] is not None and state['free_before'].get(p) is not None else None for p in after},'primary_E_data':'PRESERVED; every deleted source file matched an independent E file by SHA256','retention_rule':'Different versions, files without proven E copies, inaccessible files and reparse data are retained.'}
    save(result)


if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        save({'status':'NEEDS_ATTENTION','error':traceback.format_exc()});raise
    finally:ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
