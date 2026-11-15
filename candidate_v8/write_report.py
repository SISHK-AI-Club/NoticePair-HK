from pathlib import Path
import json,csv
from collections import Counter
r=Path(__file__).resolve().parent
m=json.loads((r/'comparison_metrics.json').read_text())
run=json.loads((r/'v8_500_results.json').read_text())
rows=list(csv.DictReader((r/'case_comparison.csv').open(encoding='utf-8-sig')))
pct=lambda n,d:f'{100*n/d:.1f}%'
lines=['# V8 versus frozen V7 — 500-case development comparison','',
'Both checkers ran fresh in Google Colab on the same 500 approved rows, sharing identical loaded LaBSE and multilingual NLI model objects. The CSV was checksum-verified and unchanged. V8 was developed using this benchmark, so its scores below are development results, not held-out accuracy.','',
'[Live Colab comparison](https://colab.research.google.com/drive/19fEgOSfMX9qLheQsT6N9HL0E0S0a12LW?authuser=3)','',
'## Classification results','',
'| Difficulty | Cases (incorrect / clean) | V7 accuracy | V8 accuracy | V7 caught / missed | V8 caught / missed | V7 false alarms | V8 false alarms |',
'|---|---:|---:|---:|---:|---:|---:|---:|']
for d in ['routine','difficult','edge']:
 a=m['by_difficulty']['frozen'][d];b=m['by_difficulty']['candidate'][d];n=sum(a.values());issues=a.get('TP',0)+a.get('FN',0);clean=n-issues
 lines.append(f"| {d.title()} | {n} ({issues} / {clean}) | {pct(a.get('TP',0)+a.get('TN',0),n)} | {pct(b.get('TP',0)+b.get('TN',0),n)} | {a.get('TP',0)} / {a.get('FN',0)} | {b.get('TP',0)} / {b.get('FN',0)} | {a.get('FP',0)} | {b.get('FP',0)} |")
a=m['counts']['frozen'];b=m['counts']['candidate']
lines+=['',f"Overall accuracy: **{pct(a['TP']+a['TN'],500)} → {pct(b.get('TP',0)+b.get('TN',0),500)}**.",
 f"Incorrect notices caught: **{a['TP']}/150 → {b.get('TP',0)}/150**. Misses: **{a.get('FN',0)} → {b.get('FN',0)}**. False alarms: **{a.get('FP',0)}/350 → {b.get('FP',0)}/350**.",
 f"Error recall: {pct(a['TP'],150)} → {pct(b.get('TP',0),150)}. False-alarm rate among clean notices: {pct(a.get('FP',0),350)} → {pct(b.get('FP',0),350)}.",
 f"Precision of issue flags: {pct(a['TP'],a['TP']+a['FP'])} → {pct(b.get('TP',0),b.get('TP',0)+b.get('FP',0))}.",
 f"Classification transitions: {m['classification_changes']}.",'',
'## Did warnings identify the actual issue?','',
'A specific warning must name a real discrepancy in the bilingual pair and give the conflicting values or relationship. A generic contradiction score or missing-counterpart message alone does not receive this credit. Specificity is evaluated per notice; one correct explanation does not imply every ancillary message is useful.','',
'| Warning outcome on 150 incorrect notices | Frozen V7 | V8 |','|---|---:|---:|']
for key,label in [('specific','Specific actual issue'),('generic','Generic warning only'),('alignment_only','Alignment warning only'),('missed','No warning')]:
 lines.append(f"| {label} | {m['warning_ratings']['frozen'].get(key,0)} | {m['warning_ratings']['candidate'].get(key,0)} |")
lines+=['','The comparison CSV includes each source pair, gold rationale, both sets of warnings, classification outcomes, evidence, and review ratings. Structured warnings are checked against the bilingual facts. Unchanged fallback warnings retain the previous reviewed rating after verifying identical warning text apart from the neutral deadline label. The independent AI-assisted review covered all 150 incorrect notices; this has not been adjudicated by a bilingual human reviewer.','',
'## The two repaired misses','']
for cid in ['F297','F398']:
 x=next(x for x in rows if x['case_id']==cid)
 lines += [f"### {cid}",'',f"English: {x['english']}",'',f"Chinese: {x['chinese']}",'',f"V7: {x['frozen_outcome']}. V8: {x['candidate_outcome']}.",'',x['candidate_warnings'],'']
lines+=['## What changed','',
'1. **Whole-notice structure.** Supported complete notices are parsed independently in each language, so a sentence split or reordered correction no longer creates a false missing-counterpart warning.',
'2. **Role-specific facts.** Current versus superseded dates/rooms, general versus audience-specific times, and action-to-person duties are compared separately. Matching unordered number sets cannot hide swapped roles.',
'3. **Explicit relationships.** Checks compare action order, expiry at the end of the issue/following month, group booking obligations, contact-update prerequisites, and staff exceptions.',
'4. **Contextual normalization.** 最後一日 within a month-end expression is treated as a boundary, not an extra numeric quantity. “Closed unless staffed” and “open only when staffed” share a necessary-condition representation.',
'5. **Evidence in warnings.** New discrepancies report the exact fact, both language values, and the source text. Inherited reply/RSVP warnings use the neutral label “deadline” rather than incorrectly asserting “application deadline.” Correction dates in structured output use MM-DD notation.',
'6. **Conservative fallback.** Both full notices must fit a supported structure. Unknown clauses, mixed exception connectors, embedded instructions, or unsupported formats go through V7. Topic similarity/NLI checks remain. An uncertain isolated subject with no explicit fact discrepancy defers to V7’s full-notice assessment, preventing the new subject check from introducing a regression. Reporting, arriving, and entering remain distinct.','',
'No pretrained model weights were trained or fine-tuned. Existing model thresholds remain similarity 0.40 and contradiction 0.65. This is a parser and decision-rule revision.','',
'## Validation and reproducibility','',
 f"- All 500 IDs and the CSV checksum were verified. CSV SHA256: `{run['metadata']['dataset_sha256']}`.",
 f"- Candidate source SHA256: `{run['metadata']['candidate_sha256']}`.",
 f"- Fresh frozen-warning differences against the earlier saved run: {len(m['baseline_warning_drift'])}. These are raw warning-text comparisons, including rounded model scores.",
 f"- Decision paths: {m['paths']}.",
'- Fourteen local regression tests passed, covering action reversals, month-end wording, mutated passive duties, group obligations, correction roles, audience swaps, extra clauses, unsupported conditions, reporting versus arrival, clock boundaries, and full-context fallback for uncertain subjects.',
'- Original CSV, saved frozen outputs, and the frozen notebook were preserved. Only the completed frozen runtime was released to satisfy Colab’s session limit.',
'- The historical run did not capture model commit revisions. This fresh comparison controls that limitation by sharing the exact same loaded model objects between versions; package versions and model identifiers are in the raw result metadata.','',
'## What this score does and does not establish','',
'This result tests fixes on known data. The dataset contains 35 template families, with repeated semantic constructions. The new finite grammar covers the difficult and edge constructions after those failures were inspected. Consequently even a perfect result here is not evidence of 100% accuracy on unseen government or school notices.',
'',
'The generator also used alternate Chinese formulations only for clean cases. The added regression tests deliberately introduce errors into several alternate layouts, but they do not remove that dataset limitation. F048 and F075 additionally change month digits as well as correction roles; the original labels remain “issue,” and the original CSV was left unchanged.',
'',
'For the next evaluation, freeze this revision and use independently authored bilingual notices with unseen structures, mixed clauses, new entity names, additions/omissions, scope changes, permission versus obligation, and both clean and incorrect examples for every paraphrase style. Keep all variants of a document/template in one split, and obtain bilingual human adjudication of the labels and warning explanations. Do not tune against that new holdout.',
'',
'## Files','',
'- `v8_500_results.json`: full raw Colab predictions and run metadata.',
'- `case_comparison.csv`: all 500 cases, warnings, outcomes, and issue-specificity ratings.',
'- `comparison_metrics.json`: machine-readable totals and strata.',
'- `V8_structured_notice_comparison.ipynb`: downloadable Colab runner.',
'- `structured_notice.py`, `adapter.py`: readable implementation.',
'- `source_manifest.json`, `test_results.txt`: source hashes and local validation record.','']
lines+=['## Remaining false alarms','', '| Case | Difficulty | Notice | Warning |','|---|---|---|---|']
for x in rows:
    if x['candidate_outcome']=='FP':
        lines.append('| '+x['case_id']+' | '+x['difficulty']+' | '+x['english'].replace('\n',' / ')+' | '+x['candidate_warnings'].replace('\n',' / ')+' |')
lines+=['','These residual warnings come from the original full-notice fallback for uncertain subjects. The title-level ambiguity is unresolved; no automatic bilingual glossary or case-specific exception was added to force a perfect score.','']
(r/'comparison_report.md').write_text('\n'.join(lines))
print(r/'comparison_report.md')
