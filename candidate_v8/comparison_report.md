# V8 versus frozen V7 — 500-case development comparison

Both checkers ran fresh in Google Colab on the same 500 approved rows, sharing identical loaded LaBSE and multilingual NLI model objects. The CSV was checksum-verified and unchanged. V8 was developed using this benchmark, so its scores below are development results, not held-out accuracy.

[Live Colab comparison](https://colab.research.google.com/drive/19fEgOSfMX9qLheQsT6N9HL0E0S0a12LW?authuser=3)

## Classification results

| Difficulty | Cases (incorrect / clean) | V7 accuracy | V8 accuracy | V7 caught / missed | V8 caught / missed | V7 false alarms | V8 false alarms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Routine | 300 (90 / 210) | 99.0% | 99.7% | 90 / 0 | 90 / 0 | 3 | 1 |
| Difficult | 150 (45 / 105) | 74.0% | 99.3% | 43 / 2 | 45 / 0 | 37 | 1 |
| Edge | 50 (15 / 35) | 46.0% | 94.0% | 15 / 0 | 15 / 0 | 27 | 3 |

Overall accuracy: **86.2% → 99.0%**.
Incorrect notices caught: **148/150 → 150/150**. Misses: **2 → 0**. False alarms: **67/350 → 5/350**.
Error recall: 98.7% → 100.0%. False-alarm rate among clean notices: 19.1% → 1.4%.
Precision of issue flags: 68.8% → 96.8%.
Classification transitions: {'unchanged classification': 436, 'improved': 64}.

## Did warnings identify the actual issue?

A specific warning must name a real discrepancy in the bilingual pair and give the conflicting values or relationship. A generic contradiction score or missing-counterpart message alone does not receive this credit. Specificity is evaluated per notice; one correct explanation does not imply every ancillary message is useful.

| Warning outcome on 150 incorrect notices | Frozen V7 | V8 |
|---|---:|---:|
| Specific actual issue | 98 | 150 |
| Generic warning only | 42 | 0 |
| Alignment warning only | 8 | 0 |
| No warning | 2 | 0 |

The comparison CSV includes each source pair, gold rationale, both sets of warnings, classification outcomes, evidence, and review ratings. Structured warnings are checked against the bilingual facts. Unchanged fallback warnings retain the previous reviewed rating after verifying identical warning text apart from the neutral deadline label. The independent AI-assisted review covered all 150 incorrect notices; this has not been adjudicated by a bilingual human reviewer.

The retained fallback also emits 63 generic contradiction messages alongside correct numeric warnings. They are redundant supporting messages, not the only explanation for any detected issue. Full audit notes are in `warning_audit.md`.

## The two repaired misses

### F297

English: For the equipment loan, submit your request after creating an account.

Chinese: 辦理器材借用時，請先提交申請，再開立帳戶。

V7: FN. V8: TP.

action order differs: English create account before submit request; Chinese submit request before create account. Evidence — English [For the equipment loan, submit your request after creating an account.]; Chinese [辦理器材借用時，請先提交申請，再開立帳戶。]

### F398

English: A receipt for the studio induction is valid until the end of the month after it was issued.

Chinese: 工作室簡介的收據有效至發出當月月底。

V7: FN. V8: TP.

receipt expiry differs: English end of following month; Chinese end of issue month. Evidence — English [A receipt for the studio induction is valid until the end of the month after it was issued.]; Chinese [工作室簡介的收據有效至發出當月月底。]

## What changed

1. **Whole-notice structure.** Supported complete notices are parsed independently in each language, so a sentence split or reordered correction no longer creates a false missing-counterpart warning.
2. **Role-specific facts.** Current versus superseded dates/rooms, general versus audience-specific times, and action-to-person duties are compared separately. Matching unordered number sets cannot hide swapped roles.
3. **Explicit relationships.** Checks compare action order, expiry at the end of the issue/following month, group booking obligations, contact-update prerequisites, and staff exceptions.
4. **Contextual normalization.** 最後一日 within a month-end expression is treated as a boundary, not an extra numeric quantity. “Closed unless staffed” and “open only when staffed” share a necessary-condition representation.
5. **Evidence in warnings.** New discrepancies report the exact fact, both language values, and the source text. Inherited reply/RSVP warnings use the neutral label “deadline” rather than incorrectly asserting “application deadline.” Correction dates in structured output use MM-DD notation.
6. **Conservative fallback.** Both full notices must fit a supported structure. Unknown clauses, mixed exception connectors, embedded instructions, or unsupported formats go through V7. Topic similarity/NLI checks remain. An uncertain isolated subject with no explicit fact discrepancy defers to V7’s full-notice assessment, preventing the new subject check from introducing a regression. Reporting, arriving, and entering remain distinct.

No pretrained model weights were trained or fine-tuned. Existing model thresholds remain similarity 0.40 and contradiction 0.65. This is a parser and decision-rule revision.

## Validation and reproducibility

- All 500 IDs and the CSV checksum were verified. CSV SHA256: `2bad8349bcfaf4b48358b7aa23e1fa19321e45a8c38332ea9cdd01bfeccc165d`.
- Candidate source SHA256: `c0a5a44ed3800368d5d8d99898a1d71d0d7e4116d4ae6f954d5d9bb93d2d06ac`.
- Fresh frozen-warning differences against the earlier saved run: 0. These are raw warning-text comparisons, including rounded model scores.
- Decision paths: {'structured_notice': 274, 'frozen_fallback': 214, 'uncertain_subject_fallback': 12}.
- Fourteen local regression tests passed, covering action reversals, month-end wording, mutated passive duties, group obligations, correction roles, audience swaps, extra clauses, unsupported conditions, reporting versus arrival, clock boundaries, and full-context fallback for uncertain subjects.
- Original CSV, saved frozen outputs, and the frozen notebook were preserved. Only the completed frozen runtime was released to satisfy Colab’s session limit.
- The historical run did not capture model commit revisions. This fresh comparison controls that limitation by sharing the exact same loaded model objects between versions; package versions and model identifiers are in the raw result metadata.

## What this score does and does not establish

This result tests fixes on known data. The dataset contains 35 template families, with repeated semantic constructions. The new finite grammar covers the difficult and edge constructions after those failures were inspected. Consequently even a perfect result here is not evidence of 100% accuracy on unseen government or school notices.

The generator also used alternate Chinese formulations only for clean cases. The added regression tests deliberately introduce errors into several alternate layouts, but they do not remove that dataset limitation. F048 and F075 additionally change month digits as well as correction roles; the original labels remain “issue,” and the original CSV was left unchanged.

For the next evaluation, freeze this revision and use independently authored bilingual notices with unseen structures, mixed clauses, new entity names, additions/omissions, scope changes, permission versus obligation, and both clean and incorrect examples for every paraphrase style. Keep all variants of a document/template in one split, and obtain bilingual human adjudication of the labels and warning explanations. Do not tune against that new holdout.

## Files

- `v8_500_results.json`: full raw Colab predictions and run metadata.
- `case_comparison.csv`: all 500 cases, warnings, outcomes, and issue-specificity ratings.
- `comparison_metrics.json`: machine-readable totals and strata.
- `V8_structured_notice_comparison.ipynb`: downloadable Colab runner.
- `structured_notice.py`, `adapter.py`: readable implementation.
- `source_manifest.json`, `test_results.txt`: source hashes and local validation record.

## Remaining false alarms

| Case | Difficulty | Notice | Warning |
|---|---|---|---|
| F103 | edge | orientation session schedule / General arrival: 3 p.m. / * Performers report at 5 p.m. instead. | Needs review: no confident Chinese counterpart |
| F153 | edge | orientation session schedule / General arrival: 4 p.m. / * Performers report at 6 p.m. instead. | Needs review: no confident Chinese counterpart |
| F180 | difficult | For the orientation session, class teachers check the list and prefects distribute the materials. | Needs review: no confident English counterpart |
| F361 | routine | The sports team briefing starts at 2 p.m. | the two versions may contradict each other (74%) |
| F379 | edge | sports team briefing schedule / General arrival: 9 p.m. / * Performers report at 6 p.m. instead. | the two versions may contradict each other (94%) |

These residual warnings come from the original full-notice fallback for uncertain subjects. The title-level ambiguity is unresolved; no automatic bilingual glossary or case-specific exception was added to force a perfect score.
