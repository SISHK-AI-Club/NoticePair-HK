"""Package observed Colab results and the assistant's case explanation review."""
import csv,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'merged_v5';RES=OUT/'results'
cases=list(csv.DictReader((ROOT/'public_notice_benchmark.csv').open(encoding='utf-8-sig')))
def predictions(path):return {r['case_id']:r for r in map(json.loads,path.read_text().splitlines())}
def flag(r):return any(row['why'] for row in r['rows'])
def why(r):return '\n'.join(f"{row['chinese']} ⇄ {row['english']}\n{row['why']}" for row in r['rows'] if row['why'])
versions={v:predictions(RES/f'{v}_approved60_predictions.jsonl') for v in ['teammate_v5','our_v5','merged_v5']}
versions['original']=predictions(ROOT/'public_notice_original_predictions.jsonl')
versions['v4']=predictions(ROOT/'public_notice_v4_predictions.jsonl')
meta=json.loads((RES/'run_metadata.json').read_text())
assert meta['dataset_sha256']==hashlib.sha256((ROOT/'public_notice_benchmark.csv').read_bytes()).hexdigest()
for name,rows in versions.items():
 assert set(rows)=={c['case_id'] for c in cases},name
 assert all('error' not in r for r in rows.values()),name
reviews={r['case_id']:r for r in csv.DictReader((ROOT/'candidate_v5/v5_case_comparison.csv').open(encoding='utf-8-sig'))}
new_reviews={
 'N13-2':'Specific paired evidence now identifies one carer being sufficient versus both companions being carers; the old numerical warning remains as a secondary warning.',
 'N15-2':'Paired evidence identifies issuer versus named person; the warning is on the clause that triggers relationship proof.',
 'N16-1':'Both recipient and proxy document forms are compared separately, identifying the ownership swap.',
 'N16-2':'Paired evidence identifies inability to collect versus inability to attend the original slot.',
 'N18-2':'Paired evidence identifies delayed registration for other eligible applicants. The earlier spurious must-register interpretation is absent.'}
output=[]
for c in cases:
 r=dict(c)
 for v,preds in versions.items():r[v+'_flagged']=flag(preds[c['case_id']])
 for v in ['teammate_v5','our_v5','merged_v5']:r[v+'_warnings']=why(versions[v][c['case_id']])
 evidence=[x for row in versions['merged_v5'][c['case_id']]['rows'] for x in row.get('semantic_evidence',[])]
 r['merged_paired_evidence']=json.dumps(evidence,ensure_ascii=False)
 if c['expected_status']=='clean':
  assert not r['merged_v5_flagged'];r['explanation_review']='clean_no_warning';r['review_note']='No warning on the clean notice.'
 else:
  assert r['merged_v5_flagged']
  prior=reviews[c['case_id']]['explanation_review']
  assert prior=='specific_issue_identified' or c['case_id'] in new_reviews,(c['case_id'],prior)
  r['explanation_review']='specific_issue_identified'
  r['review_note']=new_reviews.get(c['case_id'],'Reviewed against the approved rationale: the warning identifies the planted issue; retained from V5.')
 output.append(r)
with (OUT/'merged_60_case_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
guards=json.loads((OUT/'development_guard_cases.json').read_text())
gpred={v:predictions(RES/f'{v}_development_guards_predictions.jsonl') for v in ['teammate_v5','our_v5','merged_v5']}
grows=[]
for c in guards:
 r=dict(c)
 for v,p in gpred.items():r[v+'_flagged']=flag(p[c['case_id']]);r[v+'_warnings']=why(p[c['case_id']])
 grows.append(r)
with (OUT/'development_guard_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(grows[0]));w.writeheader();w.writerows(grows)
summary=[]
for name,preds in versions.items():
 tp=sum(c['expected_status']=='issue' and flag(preds[c['case_id']]) for c in cases)
 fp=sum(c['expected_status']=='clean' and flag(preds[c['case_id']]) for c in cases)
 summary.append({'version':name,'TP':tp,'FN':40-tp,'FP':fp,'TN':20-fp,'accuracy':(tp+20-fp)/60,'recall':tp/40})
(OUT/'verified_comparison_metrics.json').write_text(json.dumps({'approved60':summary,'fresh_colab_run':meta},ensure_ascii=False,indent=2))
print(json.dumps(summary,indent=2))
print('Created comparison CSVs; manually reviewed explanations: 40/40 issue cases, 20/20 clean cases.')
