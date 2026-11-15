# V10 independent blind holdout evaluation

The frozen V10 checker scored **79.7% accuracy** on 1,000 fresh test pairs. It flagged **101 of 300 notices with a material translation discrepancy** and **4 of 700 clean notices**. Warnings identified the actual gold discrepancy in **64 of 300 issue cases** under review by the Sol testing agent.

**Scope.** These are short synthetic notices, with a maximum of 162 English characters and 49 Chinese characters, or 34 and 51 LaBSE tokens respectively. Difficulty tiers were assigned by the author. The benchmark provides no performance estimate for full multi-paragraph official emails.

## Notice-level detection

An issue is the positive class. A flag is the checker’s request for review. Recall is the share of issue notices flagged, and the clean false alarm rate is the share of clean notices flagged. If a case had several warnings, it still contributes once to this table. An always-clean baseline would attain 70% accuracy and zero recall on this test.

| Split | Cases | True positives | True negatives | False alarms | Misses | Accuracy | Precision | Recall | F1 | Clean false alarm rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Overall** | 1000 | 101 | 696 | 4 | 199 | 79.7% | 96.2% | 33.7% | 49.9% | 0.6% |
| Routine | 600 | 81 | 417 | 3 | 99 | 83.0% | 96.4% | 45.0% | 61.4% | 0.7% |
| Difficult | 300 | 15 | 210 | 0 | 75 | 75.0% | 100.0% | 16.7% | 28.6% | 0.0% |
| Edge | 100 | 5 | 69 | 1 | 25 | 74.0% | 83.3% | 16.7% | 27.8% | 1.4% |
| School | 300 | 25 | 208 | 2 | 65 | 77.7% | 92.6% | 27.8% | 42.7% | 1.0% |
| Government | 300 | 33 | 210 | 0 | 57 | 81.0% | 100.0% | 36.7% | 53.7% | 0.0% |
| Public email | 200 | 20 | 140 | 0 | 40 | 80.0% | 100.0% | 33.3% | 50.0% | 0.0% |
| Instructions | 200 | 23 | 138 | 2 | 37 | 80.5% | 92.0% | 38.3% | 54.1% | 1.4% |
| English source | 600 | 61 | 419 | 3 | 117 | 80.0% | 95.3% | 34.3% | 50.4% | 0.7% |
| Traditional Chinese source | 400 | 40 | 277 | 1 | 82 | 79.2% | 97.6% | 32.8% | 49.1% | 0.4% |

Across 100 scenario families, 2 had all ten cases classified correctly and 3 had all three issues detected. 71 had at least one issue detected, and 97 had zero false alarms.

95% family-cluster bootstrap intervals used 10,000 resamples of whole families within each domain and difficulty stratum.

| Metric | Interval |
|---|---:|
| Accuracy | 78.4%–81.0% |
| Recall | 29.3%–38.0% |
| F1 | 44.8%–54.5% |
| Clean false alarm rate | 0.0%–1.3% |
| Precision | 91.9%–100.0% |

## Warning quality and error audit

The Sol testing agent manually reviewed all 110 warnings and all 199 missed issues. A warning earned identification credit only when its explicit facts or machine comparison concretely isolated the material change in the original texts. A generic review prompt or a quotation spanning the correct words was insufficient. Concrete warnings covered 63.4% of flagged issue cases and 21.3% of all issue cases. Unresolved coverage affected 0 cases.

| Warning assessment | Count |
|---|---:|
| Clean pair with a machine back-translation error | 2 |
| Clean pair with a meaning-equivalent comparison flagged | 2 |
| Isolates the discrepancy | 68 |
| Points towards the discrepancy with limited or obscured detail | 36 |
| Gives a different or unsupported explanation on an issue case | 2 |

For missed issues, the evaluator checked whether the machine back-translation still exposed the material contrast. This audit describes what survived translation. It does not establish what a model internally relied on.

| Miss audit assessment | Count |
|---|---:|
| Blurred | 18 |
| Partial | 35 |
| Preserved | 146 |

### Findings from the case review

- The checker missed all 29 exception changes and all eight omissions. It detected 10 of 49 scope changes and three of 20 condition changes. It flagged all 11 quantity changes, although some machine comparisons gave the wrong unit or measured item.
- In 146 of 199 misses, the full back-translation preserved the material contrast. For example, T0965 clearly distinguishes permission to use a photo in an event summary from using it on a paid billboard, and T0179 distinguishes a subscriber requesting a particular update from blocking that category. Neither was flagged.
- T0652 omits a supervisor’s seal check before a machine cycle can restart. Full-notice contradiction scores in both comparison paths remained below 0.001. T0068 changes the meal waiver from the first substitute meal to each meal. The whole-notice contradiction scores were high, but the aligned coverage passage’s back-translation-based scores failed the frozen agreement requirement.
- T0429’s explicit warning correctly shows 21 May versus 12 May. T0799 flagged 30 versus 70 millilitres, but the machine comparison assigned the corrected volume to coffee powder instead of water. T0879 flagged a change, but its back-translation did not show that a caliper’s jaws should be opened instead of closed.
- Two clean-pair false alarms came from nonmaterial wording about sowing seeds (T0462 and T0975). The other two arose when the machine changed closing caliper jaws to adding a number of claws (T0039) and the Resume button label to Restore (T0565). All four retained their frozen clean labels.

## Largest miss groups

| Gold issue type | Issue cases | Detected | Missed | Recall |
|---|---:|---:|---:|---:|
| scope | 49 | 10 | 39 | 20.4% |
| exception | 29 | 0 | 29 | 0.0% |
| procedure | 28 | 6 | 22 | 21.4% |
| condition | 20 | 3 | 17 | 15.0% |
| actor | 20 | 7 | 13 | 35.0% |
| timing | 19 | 6 | 13 | 31.6% |
| omission | 8 | 0 | 8 | 0.0% |
| position | 16 | 8 | 8 | 50.0% |
| object | 11 | 4 | 7 | 36.4% |
| eligibility | 8 | 2 | 6 | 25.0% |
| equipment | 16 | 10 | 6 | 62.5% |
| location | 12 | 6 | 6 | 50.0% |

## Test design and run verification

- GPT-6.1 Sol at medium reasoning independently authored and ran the held-out test. The frozen benchmark comprises 100 scenario families with three separately authored bilingual frames per family, plus controlled semantic alternatives. There are 1,000 unique paired notices. The test compares formal English with Hong Kong written Traditional Chinese.
- The benchmark contains 600 routine, 300 difficult and 100 edge cases. Each family contains seven clean pairs and three issue pairs. School and government each contribute 300 cases. Public email and instructions each contribute 200. English is authoritative in 600 cases and Traditional Chinese in 400.
- The generator found zero exact notice-text matches, in either language, against the original 500-case benchmark, the V8 holdout and the V9 holdout. This check does not establish semantic non-overlap with every previous example.
- The labels and issue evidence were frozen before the first prediction. The candidate's runner accepts three columns. The initial attempt stopped at schema validation, before prediction, because the original held-out input file also includes source-language metadata. An input projection preserves parsed ID and bilingual text bytes and row order for all 1,000 cases. Both input hashes are recorded below. Source language identifies the authoritative version for the evaluator only.
- All 1,000 unique cases were scored. The candidate source hashes still matched the freeze after inference. The run used CPU for 24 minutes and 11 seconds and called the V7 fallback zero times.
- The cases and gold labels are synthetic and agent-authored. The same test agent reviewed the warnings and missed cases. There was no independent human validation. Short notices and related alternatives within a family do not measure performance on naturally distributed public notices or on documents near runtime context limits.

| Artifact | SHA-256 |
|---|---|
| Candidate | `c8d31da1510ad1d6a2270742b8745c8c676a79941cada37c8265f94443d3f449` |
| Dataset manifest | `899d6e4ef1b43bb5e7c5a68af12f6e14ee632b09b4f704c4befa476802b8c56a` |
| Original inputs | `67361fc532c73eef9d5000aab2790616792f4893d8b2ceaacf45bed52ea0147c` |
| Actual runner inputs | `57273985ed1508d63788944fc90335e2081983945e956e83533439099122006e` |
| Predictions | `959127973e6638b693f79bad4c3e3824d71dc69167f662ba404535c67455a566` |

## Evidence files

- [Full benchmark and annotations](review_all_1000.md)
- [All case-level outcomes and warnings](case_results.csv)
- [Manual warning decisions](warning_audit.csv) and [manual review of missed issues](miss_audit.csv)
- [Machine-readable metrics](metrics.json), [dataset manifest](frozen_manifest.json) and [input projection manifest](input_projection_manifest.json)
- [Raw predictions](v10_results.json), [inference log](run.log) and [initial input-schema rejection](input_schema_retry.log)
