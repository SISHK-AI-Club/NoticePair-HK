"""Independent arithmetic and provenance checks after the holdout run finishes."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parent;data=root.parent/'holdout_v10'
read=lambda p:list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
gold=read(data/'v10_blind_1000.csv');original=read(data/'v10_blind_inputs.csv');inputs=read(data/'v10_runner_inputs.csv')
assert [{k:r[k] for k in ['case_id','english','chinese']} for r in original]==inputs
assert [{k:r[k] for k in ['case_id','english','chinese']} for r in gold]==inputs
assert len(gold)==1000 and len({r['family_id'] for r in gold})==100
assert set(Counter(r['family_id'] for r in gold).values())=={10}
assert Counter(r['difficulty'] for r in gold)=={'routine':600,'difficult':300,'edge':100}
assert Counter(r['expected_status'] for r in gold)=={'clean':700,'issue':300}
assert Counter(r['source_language'] for r in gold)=={'en':600,'zh':400}
raw=(data/'v10_results.json').read_bytes();prediction=json.loads(raw)
frozen=json.loads((root/'frozen_manifest.json').read_text())
assert prediction['metadata']['files']==frozen['files']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen['files'].items())
assert prediction['metadata']['inputs_sha256']==hashlib.sha256((data/'v10_runner_inputs.csv').read_bytes()).hexdigest()
pred={r['case_id']:r for r in prediction['results']}
assert len(pred)==len(prediction['results'])==1000
assert set(pred)=={r['case_id'] for r in gold}
report=json.loads((data/'metrics.json').read_text())
results={}
for tier in ['overall','routine','difficult','edge']:
 counts=Counter()
 for r in gold:
  if tier!='overall' and r['difficulty']!=tier:continue
  p=pred[r['case_id']];assert bool(p['warnings'])==p['flagged'];assert p['v7_fallback'] is False
  truth=r['expected_status']=='issue';flag=p['flagged']
  counts[('T' if truth==flag else 'F')+('P' if flag else 'N')]+=1
 scores=report['overall'] if tier=='overall' else report['by_difficulty'][tier]
 for label in ['TP','TN','FP','FN']:assert counts[label]==scores[label.lower()]
 assert abs((counts['TP']+counts['TN'])/sum(counts.values())-scores['accuracy'])<1e-12
 results[tier]=dict(counts)
verified=dict(independent_check='IDs, source text identity, frozen code hashes, quota integrity and confusion counts independently verified',counts=results,predictions_sha256=hashlib.sha256(raw).hexdigest())
(root/'holdout_independent_verification.json').write_text(json.dumps(verified,indent=2)+'\n')
print(json.dumps(verified,indent=2))
