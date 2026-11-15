"""Run the frozen predictor on an inputs-only CSV; never score during inference."""
import argparse,csv,json,hashlib,sys,time,platform,importlib.metadata,io
from pathlib import Path
from datetime import datetime,timezone
from engine import Checker,MODEL_IDS
p=argparse.ArgumentParser()
p.add_argument('--inputs',required=True);p.add_argument('--output',required=True);p.add_argument('--cache',required=True)
p.add_argument('--batch-size',type=int,default=50);p.add_argument('--require-frozen',action='store_true')
a=p.parse_args();root=Path(__file__).resolve().parent
source_files=['__init__.py','engine.py','backbone.py','facts.py','terminology.py','backbone_config.json','features.py','coverage_rules.py','learned_head.json','run.py']
hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in source_files}
if a.require_frozen:
 manifest=json.loads((root/'frozen_manifest.json').read_text());assert hashes==manifest['files'],'Frozen checker changed'
raw=Path(a.inputs).read_bytes()
rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
assert set(rows[0])=={'case_id','english','chinese'},'Prediction input must contain no gold labels or rationales'
assert len({r['case_id'] for r in rows})==len(rows)
started=datetime.now(timezone.utc).isoformat()
checker=Checker(cache=a.cache)
results=[];output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
partial=output.with_suffix('.jsonl');partial.write_text('')
for i in range(0,len(rows),a.batch_size):
 batch=checker.predict_many(rows[i:i+a.batch_size]);results.extend(batch)
 with partial.open('a') as f:
  for r in batch:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 print('PREDICTIONS',len(results),'/',len(rows),flush=True)
metadata=dict(version='V11',started=started,completed=datetime.now(timezone.utc).isoformat(),
 inputs_sha256=hashlib.sha256(raw).hexdigest(),files=hashes,model_ids=MODEL_IDS,
 model_revisions=checker.revisions,device=checker.device,python=platform.python_version(),
 packages={p:importlib.metadata.version(p) for p in ['torch','transformers','sentence-transformers','sentencepiece','pandas','scipy','numpy','opencc-python-reimplemented']},
 predictions=len(results),v7_fallback_calls=0)
output.write_text(json.dumps(dict(metadata=metadata,results=results),ensure_ascii=False,indent=2))
print('V11 COMPLETE',len(results),flush=True)
