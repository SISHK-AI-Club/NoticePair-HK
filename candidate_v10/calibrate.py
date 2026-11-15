"""Select global decision thresholds only on old development content pairs."""
import ast,csv,json,re,collections
from pathlib import Path
from engine import Checker
root=Path(__file__).resolve().parent
n=next(n for n in ast.parse((root/'probe.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='body');exec(compile(ast.Module(body=[n],type_ignores=[]),'diagnostic','exec'))
old=list(csv.DictReader((root.parent/'holdout_v9/v9_unseen_1000.csv').open(encoding='utf-8-sig')))
sig=json.loads((root/'dev_signals.json').read_text());indices={(x['chinese'],x['english']):f'D{i:04}' for i,x in enumerate(sig)}
results={r['case_id']:r for r in json.loads((root/'dev_final_signals.json').read_text())['results']}
checker=Checker.__new__(Checker);base=json.loads((root/'config.json').read_text())
trials=[]
for support in [.4,.5,.65,.75,.85,.9]:
 for mt in [.75,.85,.9,.95]:
  c=dict(base,cross_support=support,mt_bidirectional=mt,mt_oneway=mt);checker.config=c
  counts=collections.Counter();families=collections.defaultdict(collections.Counter)
  for r in old:
   p=results[indices[body(r['chinese']),body(r['english'])]];s=p['signals']
   semantic=checker.semantic_decision(s)
   supported=[ss for ss in s['passages'] if ss['similarity']>=c['semantic_alignment_min'] and checker.semantic_decision(ss)]
   if supported:semantic=True
   elif len(s['passages'])>1 and not (min(s['cross'])>=c['whole_cross_min'] and min(s['translated'])>=c['whole_mt_min']):semantic=None
   flagged=any(w['kind']=='explicit_fact' for w in p['warnings']) or bool(semantic)
   o=('T' if flagged==(r['expected_status']=='issue') else 'F')+('P' if flagged else 'N');counts[o]+=1;families[r['family_id']][o]+=1
  rec=dict(config=c,counts=dict(counts),accuracy=(counts['TP']+counts['TN'])/1000,precision=counts['TP']/max(1,counts['TP']+counts['FP']),recall=counts['TP']/300,by_family=families)
  trials.append(rec)
  print('support',support,'MT',mt,dict(counts),'accuracy',rec['accuracy'])
# Pre-stated selection: aim for at most 1% clean false alarms, then maximise
# development accuracy. If no policy meets that target, minimise false alarms.
eligible=[t for t in trials if t['counts'].get('FP',0)<=7]
selected=max(eligible,key=lambda t:(t['accuracy'],t['recall'])) if eligible else min(trials,key=lambda t:(t['counts'].get('FP',0),-t['accuracy']))
(root/'calibration.json').write_text(json.dumps(dict(evaluation='old V9 content pairs; reference/layout removed; development only',selection_rule='FP<=7/700 then highest accuracy',selected=selected,trials=trials),indent=2))
(root/'config.json').write_text(json.dumps(selected['config'],indent=2)+'\n')
print('SELECTED',selected['config'],selected['counts'])
