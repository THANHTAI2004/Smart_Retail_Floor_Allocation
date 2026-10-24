"""Fresh C-receipt versus E presence/size audit, with verified parent manifest completion."""
import hashlib
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

ROOT=Path('E:/Smart_Retail_Floor_Allocation')
BASE=ROOT/'experiments'
SOURCE=Path('C:/Users/admin/Documents/SmartRetailBackups/20261024-consolidation')
OUT=BASE/'migration/C-to-E-final-audit'
OUT.mkdir(parents=True,exist_ok=True)


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while b:=stream.read(1024*1024):h.update(b)
    return h.hexdigest()


def audit_folder(receipt,target):
    manifest=json.loads(receipt.read_text(encoding='utf-8'))
    def one(pair):
        rel,expected=pair;p=Path(rel)
        assert not p.is_absolute() and '..' not in p.parts
        path=target/p
        try:
            stat=os.stat('\\\\?\\'+str(path))
            return None if stat.st_size==expected['bytes'] else {'path':str(path),'status':'SIZE_CHANGED','expected':expected['bytes'],'actual':stat.st_size}
        except FileNotFoundError:return {'path':str(path),'status':'MISSING'}
    with ThreadPoolExecutor(max_workers=8) as pool:issues=[x for x in pool.map(one,manifest['files'].items(),chunksize=128) if x]
    return {'target':str(target),'files':len(manifest['files']),'bytes':sum(v['bytes'] for v in manifest['files'].values()),'issues':issues}


def main():
    ledger=json.loads((BASE/'migration/consolidation.json').read_text(encoding='utf-8'))
    supplemental=[]
    for source in sorted((SOURCE/'paper-v2-results-original').iterdir()):
        if not source.is_file():continue
        target=BASE/'results/20261023-paper-v2'/source.name
        existed=target.exists()
        if not existed:
            temp=target.with_name(source.name+'.C-copying')
            shutil.copy2(source,temp);assert sha(source)==sha(temp)
            os.link(temp,target);temp.unlink()
        assert sha(source)==sha(target)
        supplemental.append({'file':source.name,'bytes':source.stat().st_size,'sha256':sha(target),'copied_now':not existed})
    campaigns=[]
    for item in ledger['campaigns']:
        receipt=BASE/'migration/receipts'/(item['campaign']+'.json')
        assert sha(receipt)==item['manifest_sha256']
        result=audit_folder(receipt,BASE/'results/20261023-paper-v2'/item['campaign']);campaigns.append(result)
        print(json.dumps({'campaign':item['campaign'],'checked':result['files'],'issues':len(result['issues'])}),flush=True)
    runtime=[]
    for receipt in sorted((BASE/'migration/receipts').glob('external-*.json')):
        relative=receipt.stem.removeprefix('external-')
        runtime.append(audit_folder(receipt,BASE/'runtime/external'/relative))
    flat=[]
    for source in (SOURCE/'runtime-original').iterdir():
        if source.is_file():
            target=BASE/'runtime/external'/source.name
            flat.append({'file':source.name,'exists':target.is_file(),'sha256_matches':target.is_file() and sha(source)==sha(target)})
    missing=[x for r in campaigns+runtime for x in r['issues'] if x['status']=='MISSING']
    changes=[x for r in campaigns+runtime for x in r['issues'] if x['status']=='SIZE_CHANGED']
    result={'checked_utc':datetime.now(UTC).isoformat(),'campaigns':len(campaigns),'campaign_files':sum(x['files'] for x in campaigns),'campaign_bytes':sum(x['bytes'] for x in campaigns),'campaign_issues':[i for r in campaigns for i in r['issues']],'runtime_files':sum(x['files'] for x in runtime),'runtime_issues':[i for r in runtime for i in r['issues']],'root_runtime_files':flat,'source_C_parent_manifests':supplemental,'missing_files':missing,'size_changes':changes,'method':'Fresh E file presence/size against SHA256-verified C-to-D receipt manifests; no fresh full-byte hash of all 108 GiB on E. Root manifests and standalone runtime files compared by SHA256.','original_C_backups':'PRESERVED'}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert not missing
    assert all(x['sha256_matches'] for x in flat)
    assert not result['campaign_issues']
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_C_parent_manifests','campaign_issues','runtime_issues','root_runtime_files']},indent=2),flush=True)


if __name__=='__main__':main()
