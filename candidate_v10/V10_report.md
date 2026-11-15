# V10: build, frozen holdout and matched V9 comparison

**V10 did not reach the 90% fresh-holdout target.** It scored **79.7%**, with **101 of 300 errors flagged, 199 missed and 4 false alarms among 700 clean notices**. Its warning precision is high, but its error recall is too low for the intended checking task.

V10 was built and frozen before the new evaluation. The requested **GPT-6.1 Sol testing agent at medium reasoning** authored and evaluated the independent holdout. The checker itself uses local pretrained models. The completed benchmark ran locally on CPU using cached models; the downloadable notebook contains the frozen code for Colab.

## Fresh test: the result that answers the 90% question

| Difficulty | Cases | Accuracy | Errors caught | Errors missed | Clean false alarms |
|---|---:|---:|---:|---:|---:|
| Overall | 1000 | 79.7% | 101 | 199 | 4 |
| Routine | 600 | 83.0% | 81 | 99 | 3 |
| Difficult | 300 | 75.0% | 15 | 75 | 0 |
| Edge | 100 | 74.0% | 5 | 25 | 1 |

- **Error recall:** 101/300 = **33.7%**. Roughly two-thirds of the incorrect notices passed without an alarm.
- **Warning precision:** 101/105 = **96.2%**. Most flagged notices really contained an error.
- **Clean false-alarm rate:** 4/700 = **0.57%**.
- **Warnings identifying the actual discrepancy:** **64/300 issue cases (21.3%)**, or 64/101 flagged issue cases (63.4%), under the testing agent’s stricter audit.
- **V7 fallback:** **0 calls across all 1,000 cases**. All cases had complete input coverage.
- **Family-cluster bootstrap interval for accuracy:** **78.4%–81.0%**. This describes variation within the synthetic family mix; it is not a population guarantee.

Accuracy is `(correct clean decisions + correctly flagged issue notices) / all notices`. With 70% clean data, accepting everything would score 70% while catching no errors. That is why recall and warning quality matter alongside the headline percentage.

**Scope:** 100 synthetic scenario families, three authored linguistic frames per family, 600 routine / 300 difficult / 100 edge cases and 700 clean / 300 incorrect pairs. The longest English notice is 162 characters and the longest Chinese notice is 49 characters. These are short formal notices, not full multi-paragraph emails. Difficulty labels and gold translations are agent-authored, without independent human validation.

## What changed from V9

1. **A single contextual checking path replaces V7 fallback.** Unknown wording is passed directly through the V10 comparison, rather than requiring a recognised notice template first.
2. **Bilingual fact checks use typed values and evidence.** Units, dates, times, selected properties and explicit obligations are compared only when the property is resolved on both sides. Equivalent conversions such as 1 metre / 100 centimetres are accepted. Bare negation counts and Chinese characters embedded in ordinary words no longer trigger discrepancies.
3. **Alignment supports reordered and differently segmented text.** Unmatched sentences are attached to related passage groups. A different sentence count alone does not cause an alarm.
4. **A translation cross-check supplements the original bilingual comparison.** Each Chinese sentence is translated separately with NLLB. Internal OpenCC conversion and a published terminology glossary stabilise that step; source evidence stays in the original Traditional Chinese.
5. **Stronger evidence is required before semantic alarms.** The bilingual and back-translation comparisons must support the same passage. Weak translation quality is filtered, and isolated document-level scores need stronger corroboration.
6. **Warnings expose their evidence.** Explicit checks state differing values. Semantic warnings show both passages, the machine back-translation and textual differences. The test audit separately checks whether those details explain the real error.

The pretrained weights were not fine-tuned in V10. This revision changes the comparison architecture, factual checks and decision thresholds. The selected thresholds were calibrated on 195 distinct content pairs extracted from the earlier V9 benchmark, weighted to its original 1,000 rows. Reference/layout decorations were removed for that development diagnostic. The exact, unstripped matched comparison below is a separate completed run.

## Same old notices: V9 versus V10

Both versions here are evaluated on the exact previous 1,000 cases, including their original headings and identifiers. V10 used this dataset during development, so this table measures improvement on reused data, not new-case accuracy.

| Difficulty | V9 accuracy | V10 accuracy | V9 caught / missed / false alarms | V10 caught / missed / false alarms |
|---|---:|---:|---:|---:|
| Overall | 77.5% | 94.7% | 238 / 62 / 163 | 247 / 53 / 0 |
| Routine | 76.5% | 97.5% | 131 / 49 / 92 | 165 / 15 / 0 |
| Difficult | 79.7% | 91.3% | 78 / 12 / 49 | 64 / 26 / 0 |
| Edge | 77.0% | 88.0% | 29 / 1 / 22 | 18 / 12 / 0 |

On the old set, false alarms changed from **163 to 0**, and errors caught changed from **238 to 247**. V10 fixed **209** decisions and regressed **37**. This development comparison and the 79.7% new-set result must remain separate.

## What it missed, and why the warnings still need work

| Error group | Errors caught | Errors missed |
|---|---:|---:|
| Scope | 10 | 39 |
| Exceptions | 0 | 29 |
| Procedure | 6 | 22 |
| Conditions | 3 | 17 |
| Actor | 7 | 13 |
| Timing | 6 | 13 |
| Omissions | 0 | 8 |

**The decision rule confuses contradiction detection with translation equivalence.** For example, T0033 says that a booth has a portable speaker in English and headphones in Chinese. Those statements could both be true in the world, but they are different instructions/content. A contradiction classifier can treat them as compatible and still miss the translation error. Exceptions and omitted requirements are especially vulnerable to this distinction.
**The translation step is not the only bottleneck.** The testing agent found that the material contrast survived in the full back-translation for **146 of 199 misses**. For example, T0965 changed permission to use a photograph in an event summary into permission to use it on a paid billboard. T0652 omitted a supervisor’s seal check before restarting a machine cycle. Neither was flagged.
**Back-translation can introduce false evidence.** T0039 was a clean instruction to close a caliper’s jaws; its back-translation instead referred to adding a number of claws. Two other false alarms involved equivalent wording about planting seeds, and the fourth involved translating a Resume button label as Restore.
**A correct flag is not necessarily a correct explanation.** The agent reviewed all 110 warnings: 68 warnings isolated the actual discrepancy, 36 were partial, two explained an unsupported/different issue, and four were on clean notices. The 68 concrete warnings cover 64 distinct issue cases. Primary-agent spot checks covered 18 warning judgements and 16 missed-case examples, in addition to independently recomputing the scores and verifying provenance. These are AI reviews, not human validation.

## How to improve the next version

1. **Train for material equivalence, not just contradiction.** Start with a supervised layer using the original bilingual texts and all three NLI outputs—entailment, neutral and contradiction—in both directions. Treat missing information, changed permissions and changed scope as positive error examples even when both statements are logically compatible. Compare a simple learned classifier with direct fine-tuning of the bilingual sequence-pair encoder. Use family-separated validation to choose between them.
2. **Make the missed categories the development priority.** Add reviewed contrast pairs for exception conditions, only/at-least/all/any scope, omitted clauses, and who must do what. Include clean paraphrases with different word order and grammatical negation. These should vary across independent scenarios, rather than repeating a small collection of exact sentences.
3. **Keep the original bilingual evidence authoritative.** A flawed supporting translation should not erase a discrepancy visible in the original texts. Assess each comparison path’s reliability and learn how to combine the evidence. Use the translation-quality signal as a reliability feature, with an explicit uncertain-review outcome where appropriate.
4. **Attach values to their roles.** Extract the actor, action, object, quantity, timing and condition together. A warning about 70 millilitres should identify whether that amount describes water, powder or another object. Train or validate the evidence span extraction separately from the binary issue decision.
5. **Choose an operating point using both recall and false alarms.** At the current four false alarms, V10 would need to catch at least **204/300 errors** to reach 90% overall accuracy—**103 more than it caught**. A stronger practical target would also require high error recall, for example at least 85%, while keeping the clean false-alarm rate at or below 1%. Select that trade-off on validation data before freezing another test.
6. **Broaden and independently review the evidence base.** Use earlier synthetic datasets as development material, keep entire scenario families together during train/validation splits, and add bilingual human-reviewed real school/government notices. Test long, multi-paragraph emails and cross-paragraph exceptions separately. A future V11 may learn from these V10 failures, but it then needs a new untouched holdout for its headline score.

These are proposed next steps, not improvements already implemented or a promise that another model will reach 90%. V10 remains frozen with its measured results.

## Reproduce and inspect

Both the predictor code and held-out data were hashed before evaluation. The predictor receives only case IDs and bilingual input text. The source-language column was removed through a verified projection; all 1,000 IDs and text pairs were preserved. The gold labels were joined only for scoring. The frozen code hashes matched after inference, and the results contain a prediction for every case.

For Colab, open the frozen notebook and provide `v10_runner_inputs.csv` in its benchmark cell. For a local run, follow the README. The CPU holdout took 24 minutes 11 seconds; this batch runtime includes the local execution conditions and is not an interactive latency benchmark.

- [Frozen Colab notebook](</Users/aidenp/Desktop/Veritas AI Hackathon/candidate_v10/Public_Notice_Check_V10_frozen.ipynb>)
- [Checker README and reproduction instructions](</Users/aidenp/Desktop/Veritas AI Hackathon/candidate_v10/README.md>)
- [Full held-out dataset and annotations](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v10/v10_blind_1000.csv>)
- [Three-column prediction inputs](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v10/v10_runner_inputs.csv>)
- [All 1,000 held-out results](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v10/case_results.csv>)
- [Detailed testing-agent report](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v10/report.md>)
- [Warning audit](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v10/warning_audit.csv>) and [miss audit](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v10/miss_audit.csv>)
- [Exact old-data comparison](</Users/aidenp/Desktop/Veritas AI Hackathon/candidate_v10/old_v9_comparison.md>)
- [Independent score/provenance verification](</Users/aidenp/Desktop/Veritas AI Hackathon/candidate_v10/holdout_independent_verification.json>)

The NLLB component is a research model with a noncommercial licence and is not intended for production deployment. The prototype would need a suitable component/licence review before product deployment. [NLLB model card](https://huggingface.co/facebook/nllb-200-distilled-600M).
