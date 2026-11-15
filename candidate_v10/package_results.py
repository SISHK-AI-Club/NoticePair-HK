from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib
root=Path(__file__).resolve().parent;parent=root.parent;hold=parent/'holdout_v10'
manifest=json.loads((root/'frozen_manifest.json').read_text())
assert all(hashlib.sha256((root/f).read_bytes()).hexdigest()==h for f,h in manifest['files'].items())
selected=['engine.py','facts.py','terminology.py','config.json','run.py','frozen_manifest.json',
 'requirements.txt','requirements-lock.txt','README.md','Public_Notice_Check_V10_frozen.ipynb',
 'V10_report.md','old_v9_comparison.md','old_v9_comparison_metrics.json','old_v9_case_comparison.csv',
 'holdout_independent_verification.json','holdout_embedding_length_audit.json','evaluation_notes.md','test_facts.py']
files=[root/f for f in selected]
files += [p for p in hold.iterdir() if p.is_file() and p.name not in {'inference_cache.json','v10_results.jsonl'} and p.suffix in {'.py','.json','.csv','.md','.txt','.log','.tsv'}]
assert all(p.exists() for p in files)
target=root/'V10_code_data_results.zip'
with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,p.relative_to(parent))
with ZipFile(target) as z:assert z.testzip() is None
print(target,'files',len(files),'bytes',target.stat().st_size)
