import csv
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
metrics = json.loads((root/'metrics.json').read_text())
with (root/'case_comparison.csv').open(encoding='utf-8-sig',newline='') as file:
    rows = list(csv.DictReader(file))
by_tier = metrics['groups']
overall = by_tier['overall']['candidate']
paths = metrics['decision_paths']
agreement = sum(r['frozen_outcome']==r['candidate_outcome'] for r in rows)
lines = [
    '# V8 on 1,000 unseen synthetic notices', '',
    f"V8 accuracy was {overall['accuracy']:.1%}. V7 and V8 agreed on {agreement:,} of 1,000 decisions.",
    f"V8 caught {overall['TP']} of 300 incorrect notices and flagged {overall['FP']} of 700 clean notices.",
    f"Error recall was {overall['TP']/300:.1%} and the false-alarm rate was {overall['FP']/700:.1%}.",
    f"Decision paths recorded: {paths}.", '',
    '| Difficulty | V7 accuracy | V8 accuracy | V8 caught | V8 missed | V8 false alarms |',
    '|---|---:|---:|---:|---:|---:|',
]
for tier in ['routine','difficult','edge','overall']:
    a,b = (by_tier[tier][version] for version in ('frozen','candidate'))
    lines.append(f"| {tier.title()} | {a['accuracy']:.1%} | {b['accuracy']:.1%} | {b['TP']} | {b['FN']} | {b['FP']} |")
lines += ['', 'Both versions ran in Colab against the same checksum-verified CSV using shared model objects. Stable V8 source identity was verified against the previous source manifest.',
    '', 'The original 500-case score measured a development set. This benchmark uses 38 new scenario families with repeated structures within each family. The 70% clean share also yields 70% accuracy for an always-clean predictor, so error recall and false alarms should accompany accuracy.',
    '', '## Results by scenario family', '',
    '| Difficulty | Scenario | Cases | Caught | Missed | False alarms |',
    '|---|---|---:|---:|---:|---:|']
for tier in ('routine','difficult','edge'):
    families = {r['family_id']: r['topic'] for r in rows if r['difficulty']==tier}
    for family,topic in sorted(families.items()):
        c = by_tier[family]['candidate']
        lines.append(f"| {tier.title()} | {topic} | {sum(c[k] for k in ('TP','TN','FP','FN'))} | {c['TP']} | {c['FN']} | {c['FP']} |")
lines += ['', 'The per-case CSV supplies bilingual evidence and unedited checker warnings. Counts measure whether a warning appeared. Explanation correctness was not manually adjudicated.', '']
(root/'report.md').write_text('\n'.join(lines))
