"""Read-only project inventories and source-content comparison; never follow reparse dirs."""
import csv
import hashlib
import json
import os
import subprocess
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

SOURCE = Path('D:/Smart_Retail_Floor_Allocation')
TARGET = Path('E:/Smart_Retail_Floor_Allocation')
REUSE = os.environ.get('PROJECT_AUDIT_REUSE')
OUT = Path(REUSE) if REUSE else TARGET/'thuc_nghiem/migration'/('audit-D-to-E-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ'))
OUT.mkdir(parents=True,exist_ok=bool(REUSE))


def category(relative):
    parts=relative.parts
    if parts[0]=='.git':return 'git_metadata'
    if parts[0]=='.venv' or 'node_modules' in parts:return 'environment'
    if any(p in {'__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.hypothesis','.playwright-mcp'} for p in parts) or 'frontend/dist' in relative.as_posix():return 'generated_cache'
    if parts[0]=='var':return 'runtime'
    if parts[0]=='thuc_nghiem' and len(parts)>1:
        return {'results':'experiment_data','reports':'experiment_reports','runtime':'experiment_runtime','databases':'experiment_databases','migration':'migration_receipts','backups':'final_backup','.migration-staging':'migration_staging'}.get(parts[1],'source_and_assets')
    return 'source_and_assets'


def inventory(root):
    files={};links=[];folders=set();errors=[];stack=[root]
    last=time.monotonic()
    while stack:
        directory=stack.pop()
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    p=Path(entry.path); rel=p.relative_to(root)
                    try:
                        st=entry.stat(follow_symlinks=False)
                        if st.st_file_attributes & 0x400:
                            links.append({'path':rel.as_posix(),'resolved_target':str(p.resolve()),'within_own_project':p.resolve().is_relative_to(root.resolve())})
                        elif entry.is_dir(follow_symlinks=False):
                            folders.add(rel.as_posix()); stack.append(p)
                        elif entry.is_file(follow_symlinks=False):
                            files[rel.as_posix()]={'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'category':category(rel)}
                    except OSError as exc:errors.append({'path':str(p),'error':str(exc)})
        except OSError as exc:errors.append({'path':str(directory),'error':str(exc)})
        if time.monotonic()-last>15:
            print(json.dumps({'inventory':str(root),'files':len(files),'remaining_directories':len(stack)}),flush=True);last=time.monotonic()
    return {'files':files,'directories':sorted(folders),'links':links,'errors':errors}


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while data:=stream.read(1024*1024):h.update(data)
    return h.hexdigest()


def table(name,rows):
    columns=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader();writer.writerows(rows)


def main():
    indices_before={str(r):digest(r/'.git/index') for r in [SOURCE,TARGET]}
    if REUSE:
        a=json.loads((OUT/'D-inventory.json').read_text(encoding='utf-8'))
        b=json.loads((OUT/'E-inventory.json').read_text(encoding='utf-8'))
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            a,b=list(pool.map(inventory,[SOURCE,TARGET]))
        (OUT/'D-inventory.json').write_text(json.dumps(a,separators=(',',':')),encoding='utf-8')
        (OUT/'E-inventory.json').write_text(json.dumps(b,separators=(',',':')),encoding='utf-8')
    missing=[];size_differences=[];hash_differences=[];hash_checked=0
    for relative,item in a['files'].items():
        current=b['files'].get(relative)
        if current is None:missing.append({'path':relative,**item});continue
        if current['bytes']!=item['bytes']:size_differences.append({'path':relative,'category':item['category'],'D_bytes':item['bytes'],'E_bytes':current['bytes']})
    hash_paths=[r for r,v in a['files'].items() if v['category']=='source_and_assets' and r in b['files']]
    def compare(relative):
        return relative,digest(SOURCE/relative),digest(TARGET/relative)
    with ThreadPoolExecutor(max_workers=8) as pool:
        for relative,old,new in pool.map(compare,hash_paths):
            hash_checked+=1
            if old!=new:hash_differences.append({'path':relative,'D_sha256':old,'E_sha256':new})
    extras=[{'path':r,**v} for r,v in b['files'].items() if r not in a['files']]
    groups=defaultdict(lambda:{'D_files':0,'D_bytes':0,'E_files':0,'E_bytes':0})
    for side,inv in [('D',a),('E',b)]:
        for item in inv['files'].values():groups[item['category']][side+'_files']+=1;groups[item['category']][side+'_bytes']+=item['bytes']
    git={}
    for side,root in [('D',SOURCE),('E',TARGET)]:
        git[side]={'HEAD':subprocess.check_output(['git','--no-optional-locks','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'index_sha256_before':indices_before[str(root)],'index_sha256_after':digest(root/'.git/index')}
    assert all(g['index_sha256_before']==g['index_sha256_after'] for g in git.values()),'Concurrent index change: preserve and report'
    summary={'checked_utc':datetime.now(UTC).isoformat(),'source':str(SOURCE),'target':str(TARGET),'D_regular_files':len(a['files']),'E_regular_files':len(b['files']),'D_logical_bytes':sum(x['bytes'] for x in a['files'].values()),'E_logical_bytes':sum(x['bytes'] for x in b['files'].values()),'missing_on_E':len(missing),'missing_by_category':dict(Counter(x['category'] for x in missing)),'size_differences':len(size_differences),'size_differences_by_category':dict(Counter(x['category'] for x in size_differences)),'source_asset_SHA256_checked':hash_checked,'source_asset_SHA256_differences':hash_differences,'E_extra_files':len(extras),'groups':dict(groups),'git':git,'links':{'D':a['links'],'E':b['links']},'read_errors':a['errors']+b['errors'],'limitations':['Directory reparse points are recorded and not recursively traversed; their canonical local directories are inventoried separately.','Complete file presence and size comparison; SHA256 comparison covers source/config/docs/assets, not every large experiment artifact or cached dependency.','Live E finalizer may add/modify reports, logs, status and backup files during the audit.']}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    table('missing-on-E.csv',missing);table('different-size.csv',size_differences);table('different-source-sha256.csv',hash_differences);table('extra-on-E.csv',extras)
    print('AUDIT_REPORT',str(OUT),flush=True)
    print(json.dumps({k:v for k,v in summary.items() if k not in {'links','groups','limitations'}},indent=2),flush=True)


if __name__=='__main__':main()
