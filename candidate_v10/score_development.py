"""Diagnostic scoring on old notices with reference/layout decorations removed.
These weighted results are development evidence, not a fresh holdout score.
"""
import ast,csv,json,re,sys,collections
from pathlib import Path
root=Path(__file__).resolve().parent
n=next(n for n in ast.parse((root/'probe.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='body')
exec(compile(ast.Module(body=[n],type_ignores=[]),'diagnostic_body','exec'))
old=list(csv.DictReader((root.parent/'holdout_v9/v9_unseen_1000.csv').open(encoding='utf-8-sig')))
sig=json.loads((root/'dev_signals.json').read_text())
indexes={(x['chinese'],x['english']):f'D{i:04}' for i,x in enumerate(sig)}
path=Path(sys.argv[1]);payload=json.loads(path.read_text());pred={r['case_id']:r for r in payload['results']}
counts=collections.defaultdict(collections.Counter);bad={}
for r in old:
 p=pred[indexes[body(r['chinese']),body(r['english'])]]
 outcome=('T' if p['flagged']==(r['expected_status']=='issue') else 'F')+('P' if p['flagged'] else 'N')
 for key in ['overall',r['difficulty'],r['topic']]:counts[key][outcome]+=1
 if outcome in ('FP','FN'):bad.setdefault((outcome,r['topic']),dict(reference=r,prediction=p))
for k,c in counts.items():print(k,dict(c),round(100*(c['TP']+c['TN'])/sum(c.values()),2))
path.with_name(path.stem+'_score.json').write_text(json.dumps(dict(evaluation='195 distinct content pairs extracted from old V9 data; weighted to original 1000; stripped layout; development only',counts=counts,errors=[dict(outcome=k[0],topic=k[1],**v) for k,v in bad.items()]),ensure_ascii=False,indent=2))
