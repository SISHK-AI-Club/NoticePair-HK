"""Join frozen Colab predictions to the approved labels."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
dataset = root / 'public_notice_holdout_120.csv'
cases = list(csv.DictReader(dataset.open(encoding='utf-8-sig')))
run = json.loads((root / 'heldout120_results.json').read_text())
assert hashlib.sha256(dataset.read_bytes()).hexdigest() == run['metadata']['csv_sha256']
pred = {r['case_id']: r['rows'] for r in run['results']}
assert len(pred) == len(run['results']) == 120
assert set(pred) == {c['case_id'] for c in cases}
counts = Counter()
review = []
for case in cases:
    warnings = [r for r in pred[case['case_id']] if r['why']]
    truth = case['expected_status'] == 'issue'
    flagged = bool(warnings)
    outcome = ('T' if truth == flagged else 'F') + ('P' if flagged else 'N')
    counts[case['difficulty'], outcome] += 1
    review.append({**case, 'outcome': outcome, 'warning_review': '',
                   'warnings': '\n'.join(f"{r['english']} ⇄ {r['chinese']} | {r['why']}" for r in warnings)})
    if outcome != 'TN':
        print(case['case_id'], outcome, case['difficulty'], case['expected_issue_or_clean_rationale'])
        print(review[-1]['warnings'])
totals = {key: sum(counts[t,key] for t in ('easy','moderate','hard')) for key in ('TP','FN','FP','TN')}
assert totals == run['metadata']['counts']
for t in ('easy','moderate','hard'):
    print(t, {k: counts[t,k] for k in totals})
print(totals)
with (root / 'heldout_case_review.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(review[0]))
    writer.writeheader()
    writer.writerows(review)
