import csv,json
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parent
metrics=json.loads((root/'metrics.json').read_text()); groups=metrics['groups']
rows=list(csv.DictReader((root/'case_comparison.csv').open(encoding='utf-8-sig')))
raw=json.loads((root/'v9_development_1000_results.json').read_text())
old=json.loads((root.parent/'holdout_1000/v8_holdout_1000_results.json').read_text())
assert len(raw['results'])==len(old['results'])==1000
assert all(a['case_id']==b['case_id'] for a,b in zip(raw['results'],old['results']))
reproduced=sum(any(x['why'] for x in a['frozen'])==any(x['why'] for x in b['candidate']) for a,b in zip(raw['results'],old['results']))
fixed=[r for r in rows if r['frozen_outcome'][0]=='F' and r['candidate_outcome'][0]=='T']
regressed=[r for r in rows if r['frozen_outcome'][0]=='T' and r['candidate_outcome'][0]=='F']
paths=metrics['decision_paths']; b=groups['overall']['candidate']
lines=['# V9 clause checking: 1,000-case development rerun','',f"V9 reached {b['accuracy']:.1%} notice-level accuracy, caught {b['TP']}/300 incorrect notices, missed {b['FN']}, and falsely flagged {b['FP']}/700 clean notices.",'','These cases previously formed V8’s unseen benchmark, but their failures informed V9. V9’s result is a development score, not held-out accuracy or a claim about real-world accuracy. The dataset has 38 repeated scenario families, not 1,000 independent structures.','', '| Difficulty | Cases | Accuracy V8 → V9 | Caught V8 → V9 | Missed V8 → V9 | False alarms V8 → V9 |','|---|---:|---:|---:|---:|---:|']
for tier in ['routine','difficult','edge','overall']:
 a,b=groups[tier]['frozen'],groups[tier]['candidate'];n=sum(a[k] for k in ['TP','TN','FP','FN'])
 lines.append(f"| {tier.title()} | {n} | {a['accuracy']:.1%} → {b['accuracy']:.1%} | {a['TP']} → {b['TP']} | {a['FN']} → {b['FN']} | {a['FP']} → {b['FP']} |")
lines+=['',f"Previously wrong decisions corrected: {len(fixed)}. Previously correct decisions made wrong: {len(regressed)}. Fresh baseline decisions reproduced {reproduced}/1000 previous V8 decisions.",'','## What changed','','- A clause-level parser extracts bilingual facts without requiring an entire notice to match a template. Recognised facts can appear alongside different headings, in a different order, or combined with other recognised clauses.','- Facts distinguish permission from obligation, refund exclusions, conditional submission channels, responsible actors, partial cancellation, time anchors, priority, inclusive thresholds, acknowledgement versus approval, and document custody.','- Additional concrete attributes cover gate colour, incoming/outgoing trays, front/back placement, and SMS/email delivery.','- Differences produce the compared values and the English and Chinese evidence spans.','- Unrecognised text, facts found in only one language, and repeated facts are retained for the V8 checker. V7 remains the underlying fallback for unsupported content.','- The neural model weights and similarity/contradiction thresholds are unchanged. This is a checking-logic improvement, not neural fine-tuning.','', '## Coverage and remaining dependence','',f"Recorded candidate decision paths (a notice may have more than one path): {paths}.",'','The clause recognisers remain phrase-specific. They remove whole-notice layout dependence for supported clauses, but do not provide a general semantic parser. Unsupported paraphrases, coreference, quotations, and exceptions still need further work. Residual review remains necessary even on notices with recognised facts.','', '## Remaining errors by family','','| Difficulty | Topic | Missed | False alarms |','|---|---|---:|---:|']
for fid in sorted({r['family_id'] for r in rows}):
 r=next(r for r in rows if r['family_id']==fid);c=groups[fid]['candidate']
 if c['FN'] or c['FP']:lines.append(f"| {r['difficulty']} | {r['topic']} | {c['FN']} | {c['FP']} |")
lines+=['','## Remaining individual failures','']
for r in rows:
 if r['candidate_outcome'][0]!='F':continue
 lines += [f"### {r['case_id']} — {r['candidate_outcome']} — {r['topic']}",f"English: {r['english']}",f"Chinese: {r['chinese']}",f"Expected: {r['expected_issue_or_clean_rationale']}",f"V9 warning: {r['candidate_warnings'] or '(none)'}",'']
lines+=['## Reproducibility','',f"Dataset SHA256: `{raw['metadata']['dataset_sha256']}`",f"Candidate source SHA256: `{raw['metadata']['candidate_sha256']}`",f"Run started: {raw['metadata']['started']}; completed: {raw['metadata']['completed']}",'','Both versions ran fresh in the same Colab process with shared model objects. Inference receives only the bilingual text; scoring labels and rationales are used after prediction. The original CSV and frozen V8 were preserved. Five targeted parser tests passed, covering clause composition/reordering, numeric boundaries, retention of added content, duplicate extraction, and a misleading prefixed claim.','', '## Next validation','','Freeze this version before testing again. A fresh evaluation should hold out entire phrasing and scenario families, include longer multi-clause notices and naturally authored formal Hong Kong Chinese, and score both the flag and its explanation. Report error recall and the false-alarm rate alongside accuracy; an always-clean checker already scores 70% on this class mix. Do not tune on the next holdout before reporting its initial score.','']
(root/'report.md').write_text('\n'.join(lines))
print('Report generated;',len(fixed),'fixed;',len(regressed),'regressed; baseline reproduced',reproduced)
print(Counter((r['topic'],r['candidate_outcome']) for r in rows if r['candidate_outcome'][0]=='F'))
