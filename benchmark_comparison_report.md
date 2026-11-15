# Original versus alignment and normalisation revision

Completed in Google Colab on 14 November 2026. The revised notebook is a separate Drive copy:
https://colab.research.google.com/drive/1a1Lw-7snv5Df4roSv7KN4qc8DVAyxvDQ?authuser=3

## Result

The revision reduces false alarms and improves the specificity of several genuine detections. Overall notice-level accuracy is unchanged. It does not establish an improvement in general semantic reasoning.

| All 60 approved cases | Original | Revised |
|---|---:|---:|
| Notice-level accuracy | 46/60 (76.7%) | 46/60 (76.7%) |
| Issue notices receiving any warning | 30/40 (75.0%) | 27/40 (67.5%) |
| Clean notices receiving a false alarm | 4/20 (20.0%) | 1/20 (5.0%) |
| Warnings on the actual faulty passage, including generic warnings | 27/40 (67.5%) | 27/40 (67.5%) |
| Issues supported by specific mismatch evidence | 18/40 (45.0%) | 21/40 (52.5%) |
| Issue notices receiving no warning | 10/40 | 13/40 |
| Median recorded inference time per notice | 7.67 seconds | 12.99 seconds |

The 18 development cases have unchanged notice-level accuracy of 17/18 (94.4%).

| Original 42-case holdout: 28 issue notices, 14 clean notices | Original | Revised |
|---|---:|---:|
| Notice-level accuracy | 29/42 (69.0%) | 29/42 (69.0%) |
| Issue notices receiving any warning | 19/28 (67.9%) | 16/28 (57.1%) |
| Clean notices receiving a false alarm | 4/14 (28.6%) | 1/14 (7.1%) |
| Warnings on the actual faulty passage, including generic warnings | 16/28 (57.1%) | 16/28 (57.1%) |
| Issues supported by specific mismatch evidence | 9/28 (32.1%) | 12/28 (42.9%) |
| Precision of notice-level warnings | 19/23 (82.6%) | 16/17 (94.1%) |
| Median recorded inference time per notice | 8.21 seconds | 13.62 seconds |

**Metric definitions.** Notice-level accuracy credits any warning on an issue notice, even when its explanation concerns the wrong passage. This can overstate useful detection. The evidence review therefore separates `identified` (a specific relevant rule mismatch on the correct passage), `localized` (a generic contradiction/similarity warning on the faulty passage), and `missed` (no useful warning on that passage). An identified result need not fully explain the semantic consequence. For example, N13-2 exposes a 1-versus-2 difference without explicitly assigning those counts to carers. These are manual review labels, not calibrated model confidence scores.

**Evaluation limitation.** This is a regression comparison on the same approved synthetic dataset. Its original holdout has now been inspected and used to guide repairs, including a time-range correction. It is no longer an untouched holdout for this revision. The percentages do not estimate general English-to-Cantonese accuracy, and the supplied notices primarily use formal Hong Kong written Chinese rather than colloquial Cantonese. No new independent agent review was performed for this revision; the original review labels were retained and revised outputs were checked against the same rubric.

## Changes made

- Replaced independent sentence matches with a global one-to-one assignment. Numeric tokens are removed for alignment embeddings to reduce matching by coincidentally equal numbers. Original numbers remain available to the actual comparison.
- Added a minimum alignment score of 0.25 and explicit unmatched-passage review messages.
- Added targeted clause splitting for Chinese availability statements after commas, and English semicolons, while retaining attached conditions.
- Normalised Unicode punctuation and width, and English noon/midnight expressions.
- Added explicit clock-time comparison, including inherited morning/afternoon markers in Chinese ranges.
- Improved numeric handling for paired expressions such as both, explicit month contexts, Chinese weekdays and selected idioms, and the pronoun in “if one was issued”.
- Suppressed spurious negation differences for paired unless/除非 and under/未滿 constructions and selected Chinese expressions such as 不同.
- Retained the existing model families and weights loaded by the notebook, and the original similarity/contradiction decision thresholds of 0.40 and 0.30. No weight fine-tuning was performed. The new alignment threshold is separate.

All 60 cases were run in the copied Colab runtime. Two implementation defects found during verification were corrected, and the affected N10-C, N10-1 and N06-C, N06-1, N06-2 cases were recomputed and merged into the final results. There are exactly 60 unique case IDs, no execution-error records, and no missing IDs. Source syntax and the exported notebook's final implementation were checked. The CSV checksum is unchanged:
`eadcf4d7c6149e9656be2522f63977c25cb62fa6d0a206046ad96e8de746dfc1`.

## What improved

- **N08-C:** Noon and the walk-in availability clause now compare cleanly.
- **N08-1:** The output explicitly identifies 14:00 versus 12:00.
- **N08-2:** The walk-in clause now aligns correctly and exposes available versus unavailable places.
- **N10-C:** Sentence reordering, noon and the 9–11 a.m. range no longer trigger a false alarm.
- **N11-C:** Equivalent exception wording no longer triggers a negation warning.
- **N13-2:** The correct clause now reports the relevant one-versus-two discrepancy. The explanation still lacks typed quantities.
- **N07-2:** Both swapped telephone purposes are matched to their respective actions, producing a clearer diagnosis.

The three additional evidence-supported issues are N08-1, N08-2 and N13-2. N08-1 and N13-2 previously had generic/localized warnings. N08-2 previously lacked a useful warning on the actual faulty clause.

## Remaining false alarm and regression

**N13-C remains a false alarm.** “A second ticket” and “one additional ticket” express the same entitlement, but the numeric parser compares untyped sets and reports an extra 1 in Chinese. The same clean clause also adds an unnecessary warning to N13-1. The table counts clean-notice false positives; it is not a count of every unnecessary individual warning inside issue notices.

**N20-2 is a genuine regression.** The original generic contradiction warning localized the unusable same-address exception; the revision produces no warning. Normalising 不同 removes an unreliable lexical cue, but the model does not recover the underlying condition conflict.

N11-1 and N11-2 also lose notice-level warnings. Their original warnings were based on equivalent exception wording and did not identify the changed obligation or paper-submission permission. The revision removes that misleading signal while leaving the actual errors undetected. Together with N20-2, these explain the drop from 19 to 16 warned issue notices in the original holdout; three fewer clean false alarms keep accuracy unchanged.

## Misses and next implementation priorities

The revised checker fails to usefully flag these 12 original-holdout issues:

| Case | Missed meaning change |
|---|---|
| N09-2 | Fee-waiver eligibility moves from members to volunteers |
| N11-1 | Required online submission becomes optional |
| N11-2 | Applicants without approval gain a paper-submission option |
| N12-2 | “No. 8 or higher” becomes “higher than No. 8” |
| N14-2 | Reply deadline starts at issuance rather than receipt |
| N15-1 | Two required documents become either document |
| N15-2 | Person named on a document becomes its issuer |
| N16-1 | Original/copy requirements switch between people |
| N16-2 | Proxy eligibility narrows to the original time slot |
| N17-2 | Required induction moves from new role to former role |
| N20-1 | Per-household limit becomes per-address limit |
| N20-2 | The same-address exception requires different addresses |

Four further original-holdout issues receive only generic warnings: N13-1, N14-1, N18-2 and N19-1. Development case N04-2 also remains unflagged; its original-ID requirement becomes optional.

1. **Compare structured facts and conditions.** Extract actor, action, object, obligation, eligibility condition, exception, quantity role, and time role from each version, with exact evidence spans. Compare those fields and describe the practical consequence. This targets the missed must/may, and/or, owner/issuer, new/former, inclusive/exclusive and conditional-scope distinctions.
2. **Replace raw number sets with typed quantities.** Distinguish total tickets from additional tickets, cardinals from ordinals, carer counts from ticket counts, dates from times, and phone numbers from quantities. This should address N13-C without globally suppressing meaningful numeric differences.
3. **Expand alignment beyond one-to-one matching.** The current splitting rules are narrow. General notices may merge or split propositions differently across languages. Add supported one-to-many/many-to-one clause groups, preserve conditions, and show low-confidence alignments for human review.
4. **Use a separate development collection for further changes.** Keep these 60 as a visible regression suite. Build a newly approved, independently worded evaluation set with family-level separation before claiming further held-out gains. Include clean paraphrases that exercise every new rule as well as actual errors.
5. **Consider model fine-tuning only after defining the target output.** Suitable labels should include correct alignment, specific error category, paired evidence spans and explanation. Training solely on clean/issue labels would reward incidental warnings. Include hard clean pairs, subtle semantic errors and an explicit uncertainty option. Choose thresholds on development data and score the frozen model once on the new evaluation set.

The additional embedding work makes this run slower. The timing figures come from separate Colab CPU runs with no repeated timing trials, so they indicate observed latency rather than a controlled performance benchmark. Cache/reuse embeddings if the revised approach is retained.

## Saved artifacts and rerunning

- `Public_Notice_Check_v3_alignment.ipynb`: exported saved Colab copy.
- `alignment_normalisation.py`: exact revised implementation extracted from the notebook.
- `public_notice_v3_final_predictions.jsonl`: final 60 revised raw outputs.
- `public_notice_original_predictions.jsonl`: original 60 raw outputs.
- `benchmark_comparison_60_cases.csv`: all approved texts, rationales, old/new warning status, review verdicts and raw warning evidence.
- `compare_benchmark.py`: reproducible notice-level scoring and completeness checks.

The final benchmark cell resumes from its existing JSONL file. For a fresh experiment after further edits, choose a new output filename rather than resuming the previous version's results. After a Colab session reset, upload `public_notice_benchmark.csv` and run the notebook in order. Keep gold rationales out of the model inputs; the runner passes only the Chinese and English texts to `check_notice`.
