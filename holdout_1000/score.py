import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
dataset = root/'v8_holdout_1000.csv'
with dataset.open(encoding='utf-8-sig',newline='') as file:
    rows = list(csv.DictReader(file))
run = json.loads((root/'v8_holdout_1000_results.json').read_text())
manifest = json.loads((root.parent/'candidate_v8/source_manifest.json').read_text())
assert run['metadata']['dataset_sha256'] == hashlib.sha256(dataset.read_bytes()).hexdigest()
assert run['metadata']['candidate_sha256'] == manifest['candidate_sha256']
assert len(rows)==len(run['results'])==1000
counts = Counter()
paths = Counter()
details = []
for row, prediction in zip(rows,run['results'],strict=True):
    assert row['case_id']==prediction['case_id']
    detail = dict(row)
    for model in ('frozen','candidate'):
        warnings = [r['why'] for r in prediction[model] if r['why']]
        outcome = ('T' if bool(warnings)==(row['expected_status']=='issue') else 'F') + ('P' if warnings else 'N')
        for bucket in ('overall',row['difficulty'],row['family_id'],row['domain']):
            counts[model,bucket,outcome] += 1
        detail[model+'_outcome'] = outcome
        detail[model+'_warnings'] = '\n'.join(warnings)
    paths.update({r.get('decision_path','unknown') for r in prediction['candidate']})
    details.append(detail)
with (root/'case_comparison.csv').open('w',encoding='utf-8-sig',newline='') as file:
    output = csv.DictWriter(file,fieldnames=details[0])
    output.writeheader()
    output.writerows(details)
summary = {}
for group in ['overall','routine','difficult','edge',*sorted({r['family_id'] for r in rows})]:
    summary[group] = {}
    for model in ('frozen','candidate'):
        c = {k:counts[model,group,k] for k in ('TP','TN','FP','FN')}
        summary[group][model] = dict(**c, accuracy=(c['TP']+c['TN'])/sum(c.values()))
(root/'metrics.json').write_text(json.dumps(dict(groups=summary,decision_paths=paths),indent=2))
for group in ('overall','routine','difficult','edge'):
    print(group,summary[group])
print(paths)
