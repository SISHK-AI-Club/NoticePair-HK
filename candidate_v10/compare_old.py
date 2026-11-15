"""Matched V9/V10 comparison on the exact old, now-reused 1,000-case set."""
from pathlib import Path
import csv,io,json,hashlib
from collections import Counter,defaultdict
root=Path(__file__).resolve().parent
raw=(root.parent/'holdout_v9/v9_unseen_1000.csv').read_bytes()
rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
old_payload=json.loads((root.parent/'holdout_v9/v9_unseen_1000_results.json').read_text())
new_payload=json.loads((root/'old_v9_full_results.json').read_text())
assert old_payload['metadata']['dataset_sha256']==hashlib.sha256(raw).hexdigest()
assert old_payload['metadata']['candidate_sha256']==json.loads((root.parent/'candidate_v9/manifest.json').read_text())['source_sha256']
inputs_raw=(root/'old_v9_full_inputs.csv').read_bytes()
assert new_payload['metadata']['inputs_sha256']==hashlib.sha256(inputs_raw).hexdigest()
projected=list(csv.DictReader(io.StringIO(inputs_raw.decode('utf-8-sig'))))
assert projected==[{k:r[k] for k in ['case_id','chinese','english']} for r in rows]
old={r['case_id']:r for r in old_payload['results']};new={r['case_id']:r for r in new_payload['results']}
assert len(rows)==len(old)==len(new)==1000
assert set(old)==set(new)=={r['case_id'] for r in rows}
manifest=json.loads((root/'frozen_manifest.json').read_text())
assert new_payload['metadata']['files']==manifest['files']
counts={v:defaultdict(Counter) for v in ['v9','v10']};changes=Counter();export=[];paths=Counter();coverage=Counter()
for r in rows:
 case=r['case_id'];truth=r['expected_status']=='issue'
 op=any(w.get('why','') for w in old[case]['warnings']);np=bool(new[case]['flagged'])
 outcomes={}
 for name,pred in [('v9',op),('v10',np)]:
  o=('T' if truth==pred else 'F')+('P' if pred else 'N');outcomes[name]=o
  for group in ['overall',r['difficulty'],r['topic']]:counts[name][group][o]+=1
 change='unchanged' if op==np else ('fixed' if np==truth else 'regressed')
 changes[change]+=1;changes[outcomes['v9']+' -> '+outcomes['v10']]+=1
 paths[new[case]['decision_path']]+=1;coverage[new[case]['coverage']]+=1
 export.append(dict(**r,v9_outcome=outcomes['v9'],v10_outcome=outcomes['v10'],change=change,v9_warnings=json.dumps(old[case]['warnings'],ensure_ascii=False),v10_warnings=json.dumps(new[case]['warnings'],ensure_ascii=False)))
with (root/'old_v9_case_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=export[0].keys());w.writeheader();w.writerows(export)
metrics=dict(evaluation='same exact original 1000 cases; now development data for V10, not held out',
 dataset_sha256=hashlib.sha256(raw).hexdigest(),counts=counts,changes=changes,paths=paths,coverage=coverage,
 candidate_sha256=manifest['candidate_sha256'])
(root/'old_v9_comparison_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
lines=['# Matched comparison on the previous V9 benchmark','',
'These are the exact same 1,000 notices used for the prior frozen V9 result, including their original headings, reference identifiers and formatting. V10 was developed using this data, so its score here is **development evidence**, not held-out accuracy.','',
'| Difficulty | V9 accuracy | V10 accuracy | V9 caught / missed / false alarms | V10 caught / missed / false alarms |',
'|---|---:|---:|---:|---:|']
for group in ['overall','routine','difficult','edge']:
 a,b=counts['v9'][group],counts['v10'][group]
 fmt=lambda c:f"{c['TP']} / {c['FN']} / {c['FP']}"
 acc=lambda c:f"{100*(c['TP']+c['TN'])/sum(c.values()):.1f}%"
 lines.append(f'| {group.title()} | {acc(a)} | {acc(b)} | {fmt(a)} | {fmt(b)} |')
lines+=['',f"V10 fixed {changes['fixed']} notice decisions and regressed {changes['regressed']}. Decision paths: {dict(paths)}. Coverage: {dict(coverage)}.",'',
'An incorrect notice with any warning counts as caught in this table. That does not establish that the warning explains the actual issue. The fresh holdout report includes a separate warning-quality audit.','',
'| Scenario family | V10 missed | V10 false alarms |','|---|---:|---:|']
for family,c in counts['v10'].items():
 if family not in ['overall','routine','difficult','edge'] and (c['FN'] or c['FP']):lines.append(f"| {family} | {c['FN']} | {c['FP']} |")
(root/'old_v9_comparison.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:dict(v['overall']) for k,v in counts.items()}));print(dict(changes))
