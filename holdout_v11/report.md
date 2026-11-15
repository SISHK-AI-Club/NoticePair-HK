# Frozen V11 holdout evaluation

V11 scored **84.6% accuracy** across 1,000 new synthetic bilingual notices. It flagged 177 of 300 material discrepancies and raised 31 flags on 700 clean pairs. The audit found that **135 of 300 material discrepancies (45.0%)** had a warning that explained the concrete change.

| Difficulty | Cases | Accuracy | Family-cluster 95% accuracy interval | True positives | True negatives | False positives | False negatives | Precision | Recall | Clean false-alarm rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Routine | 600 | 89.2% | 84.5–93.2% | 132 | 403 | 17 | 48 | 88.6% | 73.3% | 4.0% |
| Difficult | 300 | 80.7% | 77.0–84.7% | 35 | 207 | 3 | 55 | 92.1% | 38.9% | 1.4% |
| Edge | 100 | 69.0% | 63.0–75.0% | 10 | 59 | 11 | 20 | 47.6% | 33.3% | 15.7% |
| Overall | 1,000 | 84.6% | 81.5–87.4% | 177 | 669 | 31 | 123 | 85.1% | 59.0% | 4.4% |

The 10,000 bootstrap draws resampled entire families within each domain and difficulty tier. Overall family-cluster intervals were 76.0–94.4% for precision, 51.3–66.3% for recall and 1.4–8.0% for the clean false-alarm rate. A checker that never flags would score 70.0% accuracy and detect no issues. All 1,000 cases completed with full-notice coverage. There were zero unresolved cases and zero fallback calls.

## Warning and miss review

The test agent reviewed all 208 warnings and all 123 misses. A warning earned credit only when its stated facts, machine gloss or structured edit made the actual changed requirement explicit. Quoting a sentence containing the gold evidence was insufficient.

| Difficulty | All issues | Flagged issues | Concrete issue identified | Share of all issues |
|---|---:|---:|---:|---:|
| Routine | 180 | 132 | 103 | 57.2% |
| Difficult | 90 | 35 | 29 | 32.2% |
| Edge | 30 | 10 | 3 | 10.0% |
| Overall | 300 | 177 | 135 | 45.0% |

Of 177 flags on issue pairs, 135 identified the issue, 21 were partial or generic and 21 warned about the wrong issue. For example, K0138 flagged the agreed drum-cover instruction while missing the change in inventory section. K0042 pointed to a fragment of a missing retention rule without explaining the omitted disputed-transcript procedure. K0678 identified a specific instruction about removing personal notes from a photocopy before lending it by showing the full instruction missing after shared material. K0026 gave the correct two screw lengths.

Of 123 misses, 83 still had a back-translation that exposed the change, 30 had a gloss that obscured it and 10 omitted the same requirement as the translated notice. K0252 retained the contrast between access only during a demonstration and access except during a demonstration in the gloss, yet raised no flag. K0134 changed “without written permission” into “with written permission” in its gloss, hiding the actual discrepancy.

The test agent sampled 24 predicted-clean cases with clean frozen labels, two per domain and difficulty stratum. It found 21 equivalent and three with wording concerns. The separately recorded label concerns affect 31 cases across five families. They include ambiguous transfer reversal wording in English, unnumbered indicator definitions, sequencing of a spray test, unspecified portfolio privacy in Chinese and a singleton English piano-delivery notice that omits the item. The counts above use the frozen labels. Benchmark authorship and the bilingual content audit were performed by AI and have not been validated by a human reviewer.

## Freeze and run

V11 source was frozen at 03:38:28 UTC on 15 November 2026. Gold, the generator and the input-only CSV were frozen at 03:39:29 UTC. The runner loaded the frozen source and started at 03:39:50 UTC. All 1,000 predictions finished at 04:08:35 UTC. The input schema was exactly case ID, English and Chinese. Neither the model nor the benchmark labels changed during the run. The test agent began reviewing saved batches while later predictions ran, without sending judgments or examples to the predictor.

The four earlier benchmarks contributed 3,500 old pairs to the overlap check. No normalized complete notice matched exactly. The largest normalized similarity in the 12 closest character TF-IDF neighbors per notice was 0.7000 in English and 0.4242 in Chinese. The test agent confirmed that the closest pairs describe different scenarios. Actual LaBSE tokenization had maxima of 73 English and 113 Chinese tokens, below the 256-token context in both languages.

The benchmark represents 100 synthetic scenario families. Variants share subject matter and the core operational rule. Family-cluster intervals account for that dependence within the synthetic test. Accuracy on real notices remains unmeasured.

## Evidence files

- [Benchmark documentation](README.md), [freeze manifest](frozen_manifest.json), [gold cases](v11_blind_1000.csv) and [blind inputs](v11_blind_inputs.csv).
- [Frozen predictions](v11_results.json), [case outcomes](case_results.csv) and [machine-readable metrics](metrics.json).
- [Warning audit](warning_audit.csv), [miss audit](miss_audit.csv), [true-negative sample](true_negative_audit.csv) and [frozen-label concerns](label_concerns.csv).
- [V10 decision replay on the same saved signals](v10_comparison.json) and [targeted scope, exception and omission diagnostics](targeted_diagnostics.json).
