"""Recalculate metrics and preserve the manual explanation review for all 60 cases."""
import csv, json
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out=root/'candidate_v5'
cases=list(csv.DictReader((root/'public_notice_benchmark.csv').open(encoding='utf-8-sig')))
versions={
 'original':root/'public_notice_original_predictions.jsonl',
 'v4':root/'public_notice_v4_predictions.jsonl',
 'v5':out/'public_notice_v5_predictions.jsonl',
}
results={}
for v,path in versions.items():
 records=[json.loads(l) for l in path.read_text().splitlines()]
 assert len(records)==len({r['case_id'] for r in records})==60
 assert not any('error' in r for r in records)
 assert {r['case_id'] for r in records}=={c['case_id'] for c in cases}
 results[v]={r['case_id']:r for r in records}
def flagged(r):return any(x['why'] for x in r['rows'])
metrics={}
for v in versions:
 metrics[v]={}
 for split in ['all','dev','holdout']:
  cnt=Counter()
  for c in cases:
   if split!='all' and c['split']!=split:continue
   truth=c['expected_status']=='issue';pred=flagged(results[v][c['case_id']])
   cnt[('T' if truth==pred else 'F')+('P' if pred else 'N')]+=1
  m={k:cnt[k] for k in ['TP','FN','FP','TN']}
  m.update(accuracy=(cnt['TP']+cnt['TN'])/sum(cnt.values()),recall=cnt['TP']/(cnt['TP']+cnt['FN']),precision=cnt['TP']/(cnt['TP']+cnt['FP']))
  metrics[v][split]=m
(out/'comparison_metrics.json').write_text(json.dumps(metrics,indent=2))
review=[]
for c in cases:
 k=c['case_id'];r=dict(c)
 for v in versions:r[v+'_flagged']=flagged(results[v][k])
 r['newly_caught_vs_v4']=r['v5_flagged'] and not r['v4_flagged']
 r['v5_warnings']=' | '.join(x['why'] for x in results['v5'][k]['rows'] if x['why'])
 r['v5_semantic_evidence']=json.dumps([e for x in results['v5'][k]['rows'] for e in x.get('semantic_evidence',[])],ensure_ascii=False)
 # Manual review: each warning was compared with the bilingual text and planted issue.
 if c['expected_status']=='clean':
  r['explanation_review']='correct_clean' if not r['v5_flagged'] else 'false_alarm'
 elif not r['v5_flagged']:r['explanation_review']='missed'
 elif k=='N13-2':r['explanation_review']='ambiguous_numeric_warning'
 elif k=='N18-2':r['explanation_review']='generic_warning_on_faulty_passage'
 else:r['explanation_review']='specific_issue_identified'
 r['review_note']={
  'N13-2':'Numeric warning says 2 exists only in English; it does not distinguish second ticket from both carers, so no strict explanation credit.',
  'N18-2':'Contradiction warning locates a faulty passage but does not explain allocation priority versus earlier registration eligibility.',
  'N15-2':'Misses issuer of proof versus the person named on it.',
  'N16-1':'Misses original/copy requirements assigned to opposite people.',
  'N16-2':'Misses added original-slot restriction on proxy collection.',
 }.get(k,'')
 review.append(r)
with (out/'v5_case_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(review[0]));w.writeheader();w.writerows(review)
print(json.dumps({k:v['all'] for k,v in metrics.items()},indent=2))
print('Explanation review:',dict(Counter(r['explanation_review'] for r in review)))
print('Newly caught:',[r['case_id'] for r in review if r['newly_caught_vs_v4']])
assert metrics['v5']['all']['TP']==37 and metrics['v5']['all']['FP']==0
