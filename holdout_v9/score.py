import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

root = Path(__file__).resolve().parent
dataset = root/'v9_unseen_1000.csv'
rows = list(csv.DictReader(dataset.open(encoding='utf-8-sig', newline='')))
run = json.loads((root/'v9_unseen_1000_results.json').read_text())
metadata = run['metadata']
manifest = json.loads((root.parent/'candidate_v9/manifest.json').read_text())
assert metadata['candidate_sha256'] == manifest['source_sha256']
assert metadata['dataset_sha256'] == hashlib.sha256(dataset.read_bytes()).hexdigest()
assert len(run['results']) == len(rows) == 1000

groups = defaultdict(Counter)
for row, result in zip(rows, run['results'], strict=True):
    assert row['case_id'] == result['case_id']
    warnings = [entry['why'] for entry in result['warnings'] if entry['why']]
    flagged = bool(warnings)
    truth = row['expected_status'] == 'issue'
    outcome = ('T' if truth == flagged else 'F') + ('P' if flagged else 'N')
    for key in ('overall', row['difficulty'], row['family_id']):
        groups[key][outcome] += 1
    row.update(outcome=outcome, warnings='\n'.join(warnings),
               decision_paths=', '.join(sorted({w.get('decision_path','unknown') for w in result['warnings']})))

for tier, counts in metadata['counts'].items():
    assert groups[tier] == Counter(counts)
with (root/'case_results.csv').open('w',encoding='utf-8-sig',newline='') as file:
    writer = csv.DictWriter(file, fieldnames=rows[0])
    writer.writeheader()
    writer.writerows(rows)

lines = ['# Frozen V9 on 1,000 new synthetic notices', '',
         '| Group | Cases | Accuracy | Caught | Missed | False alarms |',
         '|---|---:|---:|---:|---:|---:|']
topics = {row['family_id']: row['topic'] for row in rows}
for key in ['overall','routine','difficult','edge',*sorted(topics)]:
    c = groups[key]
    n = sum(c.values())
    lines.append(f"| {topics.get(key,key.title())} | {n} | {(c['TP']+c['TN'])/n:.1%} | {c['TP']} | {c['FN']} | {c['FP']} |")
lines.extend(['',f"Decision paths: {metadata['paths']}.",
              '', 'The 1,000 rows represent 32 synthetic scenario families with repeated wording and layout variants within each family. The score measures this benchmark mix. Notice-level detection credits any warning on an incorrect notice.',
              '',f"Dataset SHA-256: `{metadata['dataset_sha256']}`",
              '',f"Frozen V9 SHA-256: `{metadata['candidate_sha256']}`"])
(root/'report.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines[:8]))
