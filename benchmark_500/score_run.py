import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
dataset = root / 'formal_bilingual_benchmark_500.csv'
cases = list(csv.DictReader(dataset.open(encoding='utf-8-sig')))
run = json.loads((root / 'formal500_results.json').read_text())
assert hashlib.sha256(dataset.read_bytes()).hexdigest() == run['metadata']['csv_sha256']
pred = {r['case_id']: r['rows'] for r in run['results']}
assert len(pred) == len(run['results']) == 500
assert set(pred) == {c['case_id'] for c in cases}
counts, patterns = Counter(), Counter()
review = []
for case in cases:
    warnings = [r for r in pred[case['case_id']] if r['why']]
    truth = case['expected_status'] == 'issue'
    flagged = bool(warnings)
    outcome = ('T' if truth == flagged else 'F') + ('P' if flagged else 'N')
    counts[case['difficulty'], outcome] += 1
    reasons = [w['why'] for w in warnings]
    rating = {'TN':'clean_no_warning','FN':'missed','FP':'false_alarm'}.get(outcome,'review')
    if outcome == 'TP':
        vals = re.search(r'changes from (\d+) to (\d+)', case['expected_issue_or_clean_rationale'])
        if vals:
            # Credit typed time/date differences or a numeric warning that identifies both changed values.
            specific = any(('numbers differ' in why and all(f'[{v}]' in why for v in vals.groups())) or
                           ('clock times differ' in why) or
                           ('deadline differs' in why) for why in reasons)
            if specific:
                rating = 'specific'
        signatures = tuple(re.sub(r'\d+%|(?<=similarity )-?\d+\.\d+', '#', w) for w in reasons)
        patterns[case['family_id'],rating,signatures] += 1
    review.append({**case, 'outcome': outcome, 'warning_review': rating,
                   'warnings': '\n'.join(f"{r['english']} ⇄ {r['chinese']} | {r['why']}" for r in warnings)})
totals = {k: sum(counts[t,k] for t in ('routine','difficult','edge')) for k in ('TP','FN','FP','TN')}
assert totals == run['metadata']['counts']
for t in ('routine','difficult','edge'):
    print(t, {k:counts[t,k] for k in totals})
print(totals)
for (family,rating,signature),n in patterns.items():
    if rating=='review':
        print(family,n,signature)
with (root / 'case_review.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(review[0]))
    writer.writeheader()
    writer.writerows(review)
