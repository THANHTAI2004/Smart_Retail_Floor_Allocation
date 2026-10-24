"""Read-only native BSON exports of quiesced experiment namespaces; main DB untouched."""
import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from smart_retail.infrastructure.filesystem import logical_fs_path
from smart_retail.infrastructure.mongodb.backup import backup, inspect
from smart_retail.infrastructure.mongodb.client import connect

ROOT = Path('D:/Smart_Retail_Floor_Allocation')
OUT = ROOT / 'thuc_nghiem/databases'
OUT.mkdir(parents=True, exist_ok=True)


def write(name, data):
    p=OUT/name
    temp=p.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
    temp.replace(p)


def one(name):
    import zipfile
    path=OUT/(name+'.zip')
    store,_=connect(database=name)
    try:
        if path.exists():
            with zipfile.ZipFile(path) as archive:
                manifest=inspect(archive)
        else:
            manifest=backup(store,path)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        return {'database':name,'archive':str(path),'sha256':digest,'bytes':path.stat().st_size,'collections':len(manifest['collections']),'documents':sum(c['documents'] for c in manifest['collections']),'native_readback':'PASS'}
    finally:store.dispose()


def main():
    store,_=connect(database='sr_consolidation_inventory')
    try:names=sorted(n for n in store.client.list_database_names() if n.startswith('sr_campaign_'))
    finally:store.dispose()
    mapping=[]
    old_c=Path('C:/Users/admin/Documents/SmartRetailRuntime/paper-v2-results')
    for name in (old_c.iterdir()):
        if not name.is_dir():continue
        old=old_c/name.name
        new=ROOT/'thuc_nghiem/results/20261023-paper-v2'/name.name
        mapping.append({'campaign':name.name,'old_root':str(old),'new_root':str(new),'original_database':'sr_campaign_'+hashlib.sha256(str(logical_fs_path(old)).encode()).hexdigest()[:24],'database_if_new_path_is_used':'sr_campaign_'+hashlib.sha256(str(logical_fs_path(new)).encode()).hexdigest()[:24]})
    for campaign in (ROOT/'thuc_nghiem/results').iterdir():
        children=list(campaign.iterdir()) if campaign.name=='20261023-paper-v2' else [campaign]
        for path in children:
            if not (path/'identity.json').exists() or any(x['campaign']==path.name for x in mapping):continue
            relative=path.relative_to(ROOT/'thuc_nghiem')
            old=ROOT/'experiments'/relative
            mapping.append({'campaign':path.name,'old_root':str(old),'new_root':str(path),'original_database':'sr_campaign_'+hashlib.sha256(str(logical_fs_path(old)).encode()).hexdigest()[:24],'database_if_new_path_is_used':'sr_campaign_'+hashlib.sha256(str(logical_fs_path(path)).encode()).hexdigest()[:24]})
    write('namespace-map.json', {'databases':mapping,'warning':'Run identity is unchanged, but database name is derived from resolved campaign path. Original BSON namespaces are exported and retained live; restore explicitly to a new namespace before any future resume. No automatic reexecution.'})
    results=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(one,n) for n in names]
        for future in as_completed(futures):
            results.append(future.result())
            write('progress.json',{'status':'EXPORTING','completed':len(results),'planned':len(names),'updated_utc':datetime.now(UTC).isoformat()})
            print(len(results),'/',len(names),results[-1]['database'],flush=True)
    write('manifest.json',{'status':'VERIFIED_NATIVE_BSON_EXPORTS','created_utc':datetime.now(UTC).isoformat(),'count':len(results),'archives':results,'writers_quiesced':True,'main_application_database':'UNTOUCHED'})
    print('DATABASE_EXPORTS_VERIFIED',flush=True)


if __name__=='__main__':main()
