"""Package frozen code, benchmark references and evaluated outputs, without caches."""
from pathlib import Path
import json,zipfile,hashlib
r=Path(__file__).resolve().parent;base=r.parent;data=base/'holdout_v11'
fm=json.loads((r/'frozen_manifest.json').read_text());dm=json.loads((data/'frozen_manifest.json').read_text())
for folder,hashes in [(r,fm['files']),(data,dm['files_sha256'])]:
 for name,expected in hashes.items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==expected
required=[r/'V11_report.md',data/'v11_results.json',data/'metrics.json',data/'warning_audit.csv',data/'miss_audit.csv',r/'holdout_independent_verification.json']
assert all(p.exists() for p in required),[str(p) for p in required if not p.exists()]
candidate_names=[*fm['files'],'frozen_manifest.json','README.md','V11_report.md','Public_Notice_Check_V11_frozen.ipynb',
 'build_notebook.py','train.py','dev_records.json','training_report.json','development_selection_metrics.json','integration_check.json',
 'smoke_inputs.csv','smoke_results.json','compare_v10.py','verify_holdout.py','holdout_independent_verification.json','package_results.py']
paths=[r/n for n in candidate_names]
paths += [p for p in data.iterdir() if p.is_file() and p.suffix in {'.csv','.json','.md','.py','.txt','.tsv'} and p.name not in {'inference_cache.json'}]
old=base/'candidate_v10'
paths += [old/n for n in ['engine.py','facts.py','terminology.py','config.json','run.py','frozen_manifest.json']]
assert len(paths)==len(set(paths))
delivery={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(r/'delivery_manifest.json').write_text(json.dumps(delivery,indent=2)+'\n');paths.append(r/'delivery_manifest.json')
zip_path=r/'V11_code_data_results.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for p in paths:archive.write(p,str(p.relative_to(base)))
with zipfile.ZipFile(zip_path) as archive:assert archive.testzip() is None
print('Verified bundle:',zip_path,'bytes:',zip_path.stat().st_size,'files:',len(paths))
