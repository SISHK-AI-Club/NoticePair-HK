"""Score exported Colab predictions; reference labels enter only here."""
import csv,json,hashlib,re
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parent
bench=root.parent/'benchmark_500'
raw=(bench/'formal_bilingual_benchmark_500.csv').read_bytes()
cases=list(csv.DictReader((bench/'formal_bilingual_benchmark_500.csv').open(encoding='utf-8-sig')))
run=json.loads((root/'v8_500_results.json').read_text())
assert run['metadata']['dataset_sha256']==hashlib.sha256(raw).hexdigest()
assert run['metadata']['candidate_sha256']==json.loads((root/'source_manifest.json').read_text())['candidate_sha256']
previous={r['case_id']:r for r in csv.DictReader((bench/'case_review.csv').open(encoding='utf-8-sig'))}
old_raw={r['case_id']:r['rows'] for r in json.loads((bench/'formal500_results.json').read_text())['results']}
results={r['case_id']:r for r in run['results']}
assert len(results)==len(run['results'])==500
assert set(results)=={r['case_id'] for r in cases}
review=[];counts={n:Counter() for n in ['frozen','candidate']};tiers={n:{d:Counter() for d in ['routine','difficult','edge']} for n in counts}
warning_ratings={n:Counter() for n in counts};changed=[];baseline_drift=[]
for case in cases:
    cid=case['case_id'];r=results[cid];row=dict(case)
    if [x['why'] for x in old_raw[cid]] != [x['why'] for x in r['frozen']]:baseline_drift.append(cid)
    for name in counts:
        warnings=[x for x in r[name] if x['why']]
        truth=case['expected_status']=='issue';flagged=bool(warnings)
        outcome=('T' if truth==flagged else 'F')+('P' if flagged else 'N')
        counts[name][outcome]+=1;tiers[name][case['difficulty']][outcome]+=1
        row[name+'_outcome']=outcome
        row[name+'_warnings']='\n'.join(x['why'] for x in warnings)
        if outcome!='TP':rating={'FP':'false_alarm','FN':'missed','TN':'clean_no_warning'}[outcome]
        elif name=='frozen':rating=previous[cid]['warning_review']
        elif any(x.get('decision_path')=='structured_notice' for x in r[name]):
            # Typed disagreement must exist; a subject-model warning alone is not specific.
            rating='specific' if any(x.get('semantic_evidence') for x in warnings) else 'generic'
        else:
            # Frozen fallback exactly preserves warning semantics; verify before reuse.
            assert row['candidate_warnings']==row['frozen_warnings'].replace('application deadline differs:', 'deadline differs:'),cid
            rating=previous[cid]['warning_review']
        warning_ratings[name][rating]+=1;row[name+'_warning_review']=rating
    row['candidate_path']='; '.join(sorted({x.get('decision_path','') for x in r['candidate']}))
    row['candidate_evidence']=json.dumps([e for x in r['candidate'] for e in x.get('semantic_evidence',[])],ensure_ascii=False)
    row['comparison']='improved' if row['frozen_outcome'].startswith('F') and row['candidate_outcome'].startswith('T') else 'regression' if row['frozen_outcome'].startswith('T') and row['candidate_outcome'].startswith('F') else 'unchanged classification'
    if row['comparison']!='unchanged classification':changed.append(cid)
    review.append(row)
with (root/'case_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(review[0]));w.writeheader();w.writerows(review)
summary=dict(counts=counts,by_difficulty=tiers,warning_ratings=warning_ratings,classification_changes=Counter(r['comparison'] for r in review),baseline_warning_drift=baseline_drift,paths=Counter(r['candidate_path'] for r in review))
assert all(dict(counts[n])==run['metadata']['counts'][n] for n in counts)
(root/'comparison_metrics.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
for r in review:
 if r['candidate_outcome'].startswith('F'):print('ERROR',r['case_id'],r['candidate_outcome'],r['candidate_warnings'])
