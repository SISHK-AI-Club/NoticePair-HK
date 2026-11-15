"""Local semantic-rule replay only; fresh Colab inference is stored separately."""
import csv, copy, json
from collections import Counter
from pathlib import Path
from semantic_checks import semantic_evidence, semantic_reasons
root=Path(__file__).resolve().parent.parent
cases={c['case_id']:c for c in csv.DictReader((root/'public_notice_benchmark.csv').open(encoding='utf-8-sig'))}
results=[json.loads(x) for x in (root/'public_notice_v4_predictions.jsonl').read_text().splitlines()]
for result in results:
    result['evaluation_type']='local replay of saved V4 matched rows, not fresh model inference'
    for row in result['rows']:
        z,e=row['chinese'],row['english']
        row['semantic_evidence']=semantic_evidence(z,e) if z and e and z!='(whole notice)' else []
        added=semantic_reasons(z,e) if row['semantic_evidence'] else []
        row['why']='; '.join(filter(None,[row['why']]+added))
        if row['why']:row['status']='⚠️ Check'
out=root/'candidate_v5'/'v5_saved_output_replay.jsonl'
out.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in results))
for split in ['dev','holdout','all']:
    cnt=Counter()
    for r in results:
        c=cases[r['case_id']]
        if split!='all' and c['split']!=split:continue
        truth=c['expected_status']=='issue';pred=any(x['why'] for x in r['rows'])
        cnt[('T' if truth==pred else 'F')+('P' if pred else 'N')]+=1
    print(split,dict(cnt),(cnt['TP']+cnt['TN'])/sum(cnt.values()))
print('Missed',[r['case_id'] for r in results if cases[r['case_id']]['expected_status']=='issue' and not any(x['why'] for x in r['rows'])])
