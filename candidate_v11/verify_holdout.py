"""Independent integrity and count verification, run only after prediction."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
r=Path(__file__).resolve().parent;d=r.parent/'holdout_v11'
read=lambda p:list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
gold=read(d/'v11_blind_1000.csv');inputs=read(d/'v11_blind_inputs.csv')
assert len(gold)==len(inputs)==1000
assert [{k:g[k] for k in ['case_id','english','chinese']} for g in gold]==inputs
assert set(inputs[0])=={'case_id','english','chinese'}
assert Counter(g['difficulty'] for g in gold)=={'routine':600,'difficult':300,'edge':100}
assert Counter(g['expected_status'] for g in gold)=={'clean':700,'issue':300}
assert Counter(g['source_language'] for g in gold)=={'en':600,'zh':400}
assert Counter(g['domain'] for g in gold)=={'school':300,'government':300,'public_email':200,'instructions':200}
assert len({g['family_id'] for g in gold})==100
assert set(Counter(g['family_id'] for g in gold).values())=={10}
for tier,n in [('routine',600),('difficult',300),('edge',100)]:
 subset=[g for g in gold if g['difficulty']==tier]
 assert Counter(g['expected_status'] for g in subset)=={'clean':n*.7,'issue':n*.3}
for family in {g['family_id'] for g in gold}:
 assert Counter(g['expected_status'] for g in gold if g['family_id']==family)=={'clean':7,'issue':3}
fm=json.loads((r/'frozen_manifest.json').read_text());dm=json.loads((d/'frozen_manifest.json').read_text())
for root,hashes in [(r,fm['files']),(d,dm['files_sha256'])]:
 for name,h in hashes.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,(root,name)
pred=json.loads((d/'v11_results.json').read_text());m=pred['metadata'];p={q['case_id']:q for q in pred['results']}
assert len(p)==len(pred['results'])==1000 and set(p)=={g['case_id'] for g in gold}
assert m['files']==fm['files']
assert m['inputs_sha256']==dm['files_sha256']['v11_blind_inputs.csv']
assert m['started']>fm['frozen_at'] and m['started']>dm['frozen_utc']
assert m['model_revisions']==fm['model_revisions']
metrics={}
for tier in ['overall','routine','difficult','edge']:
 c=Counter()
 for g in gold:
  if tier!='overall' and g['difficulty']!=tier:continue
  q=p[g['case_id']];assert bool(q['warnings'])==q['flagged'];assert q['v7_fallback'] is False
  truth=g['expected_status']=='issue';flag=q['flagged']
  c['tp' if truth and flag else 'fn' if truth else 'fp' if flag else 'tn']+=1
 metrics[tier]={k:c[k] for k in ['tp','tn','fp','fn']}|dict(n=sum(c.values()),accuracy=(c['tp']+c['tn'])/sum(c.values()))
verified=dict(checks='All source/data/model freezes, timestamps, exact input projection, IDs, family/class/domain/language/difficulty quotas and confusion counts verified',metrics=metrics,coverage=dict(Counter(q['coverage'] for q in p.values())),predictions_sha256=hashlib.sha256((d/'v11_results.json').read_bytes()).hexdigest())
(r/'holdout_independent_verification.json').write_text(json.dumps(verified,indent=2)+'\n')
print(json.dumps(verified,indent=2))
