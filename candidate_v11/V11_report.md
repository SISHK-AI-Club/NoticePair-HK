# V11: frozen model and fresh 1,000-case evaluation

V11 achieved **84.6% accuracy**, below the requested 90%. It improved on frozen V10's **81.8% on these same cases**, but the improvement was uneven: it flagged more incorrect notices overall while regressing on exceptions and edge cases. It should remain an experimental version.

The benchmark used the agreed 60/30/10 difficulty split and 70% clean / 30% incorrect split. All 1,000 cases completed. No cases were dropped, no comparisons were unresolved, and V7 was never called. The run took 28 minutes 46 seconds in the local CPU runtime. A Colab-ready notebook containing the exact frozen source is supplied; that notebook was not executed in Colab during this task.

## Fresh results and comparison

| Measure | Frozen V10 | Frozen V11 | Change |
|---|---:|---:|---:|
| Accuracy | 81.8% | **84.6%** | +2.8 percentage points |
| Incorrect notices flagged, out of 300 | 148 | **177** | +29 |
| Incorrect notices missed | 152 | **123** | −29 |
| Clean notices falsely flagged, out of 700 | 30 | **31** | +1 |
| Clean notices correctly accepted | 670 | **669** | −1 |
| Recall of incorrect notices | 49.3% | **59.0%** | +9.7 percentage points |
| Precision of flags | 83.1% | **85.1%** | +2.0 percentage points |
| False-alarm rate among clean notices | 4.3% | **4.4%** | +0.1 percentage points |

Accuracy is `(177 + 669) / 1,000`. Recall is `177 / 300`; false-alarm rate is `31 / 700`. The 70% clean mix gives an always-clean checker 70% accuracy, so accuracy alone overstates usefulness.

V10's decisions were reconstructed from the same frozen neural signals generated in this run. V11 retains V10's signal extraction, pretrained weights, translation process and normalization. The reconstruction was verified against all 2,000 previously saved V10 predictions with zero verdict differences. This is a matched decision comparison, not a separate new V10 neural inference run. V10's earlier 79.7% result used a different benchmark and is not the baseline in this table.

V11 fixed 45 old misses but introduced 16 new misses. It fixed nine false alarms but introduced ten new ones. The net totals conceal these swaps.

| Difficulty | Cases / incorrect / clean | V10 accuracy | V11 accuracy | V11 incorrect flagged | V11 missed | V11 false alarms |
|---|---:|---:|---:|---:|---:|---:|
| Routine | 600 / 180 / 420 | 85.2% | **89.2%** | 132 | 48 | 17 |
| Difficult | 300 / 90 / 210 | 77.7% | **80.7%** | 35 | 55 | 3 |
| Edge | 100 / 30 / 70 | 74.0% | **69.0%** | 10 | 20 | 11 |

The edge-case false-alarm rate was **15.7%**, versus 4.0% for routine and 1.4% for difficult notices. This does not meet the intended low-false-alarm behavior for edge cases. Government notices scored 83.0%, school notices 85.7%, public emails 87.0%, and formal instructions 83.0%.

The overall 95% family-cluster bootstrap interval was **81.5–87.4%**. It resamples whole scenario families within domain and difficulty strata, using 10,000 draws. This measures uncertainty within this synthetic benchmark design; it does not establish accuracy on real institutional correspondence.

## Did it catch the targeted errors?

| Target group | Cases | V10 flagged | V11 flagged | V11 missed | V11 warnings pinpointing the issue |
|---|---:|---:|---:|---:|---:|
| Scope | 48 | 16 | **17** | 31 | **13** |
| Exceptions | 27 | 13 | **10** | 17 | **4** |
| Omissions | 24 | 0 | **5** | 19 | **1** |

Scope includes all frozen issue labels containing “scope”; exceptions includes “exception” and “exception precedence.” These groups are disjoint. The last column uses the stricter content audit, not merely whether a notice received a flag.

The intended improvement is only partly achieved. Omission flags increased from zero to five, but only one omission warning fully identified the missing requirement. Scope improved by one binary detection. Exception detection fell by three.

Examples checked against the actual bilingual text and output:

- **K0038 — missed actor scope:** English reserves collection of a loan remote for the resident but allows the resident or nominated driver to return it. Chinese reverses those permissions. The back-translation preserved the reversal, but the decision score was only 0.103 and the notice was accepted.
- **K0046 — missed exception:** English says remove transport clips except those holding a removable shelf. Chinese says remove only those clips. V11 accepted the pair with a score of 0.037.
- **K0009 — missed entire requirement:** English requires the label to state whether nutrition figures describe the product as sold or as prepared. Chinese contains only the separate font-size instruction. The missing sentence was not flagged.
- **K0113 — useful scope warning:** The comparison explicitly showed “first profile” versus “second setup file,” identifying the changed scanner setting.
- **K0138 — correct binary flag, wrong explanation:** The actual error changes inventory section A to B. The warning instead questions the agreed instrument-cover instruction.

## Warning quality

The GPT-6.1 Sol testing agent, at medium reasoning, reviewed all **208 warnings**, all **123 misses**, and a seeded sample of **24 true negatives**. The main agent independently reconciled all audit IDs and counts and checked representative warnings and failures against both languages.

Among the 177 flagged incorrect notices:

- **135** warnings identified the concrete discrepancy.
- **21** were partial or generic.
- **21** warned about an unrelated or incorrect issue.

Thus useful, specific issue identification was **135/300 = 45.0%** of all incorrect notices, or **76.3%** of flagged incorrect notices. It was 103/180 routine issues, 29/90 difficult issues, and **3/30 edge issues**. This is the more demanding measure of whether the checker helps a reviewer fix the translation.

Merely quoting the faulty sentence did not earn credit. A warning had to expose the specific changed or missing requirement through its stated contrast, faithful machine gloss or structured comparison edits. The audit is an AI judgment, not human-certified annotation.

Of the 123 misses, the reviewer found that 83 back-translations still exposed the discrepancy and ten retained the missing requirement's absence. Thirty glosses obscured the issue. Therefore improving translation alone cannot resolve most misses: the decision and requirement-coverage steps also need work.

## Why false alarms remain

All 31 false alarms occur in eight families, illustrating why 1,000 related variants are not 1,000 independent situations.

Two families contribute 14 false alarms: keyboard assessment settings and a USB foot pedal. In **K0070**, the Chinese correctly says to go to the previous page, but the machine gloss says “top of the page.” In **K0041**, a practical-assessment instruction becomes an instruction to an “internship evaluator” in the gloss. The checker treats those machine errors as evidence against the original bilingual pair.

The new qualifier rule also transferred poorly. It triggered on seven cases: two labelled incorrect and five labelled clean. One of the two incorrect cases was already caught by the learned head. Its unique contribution was therefore **one extra detection and five extra false alarms**.

The five false alarms share a clean equivalence: “distinguishes colour complaints **from** pressure complaints” versus “區分水色**和**水壓投訴.” The Chinese conjunction does not add a requirement. Both semantic models nevertheless supplied the strong asymmetric scores required by the rule. Corroboration by two related comparisons was insufficient.

No rule or threshold was changed after this finding. The delivered V11 remains the exact frozen model tested.

## What changed in V11

V10 relied heavily on strong contradictions. V11 also considers whether one side leaves information unsupported, which can happen when both statements are logically compatible.

1. **A learned equivalence decision layer.** It uses 178 numeric features from original bilingual and back-translated entailment, neutral and contradiction scores in both directions; whole-notice and aligned-passage summaries; similarity; translation quality; and explicit-fact evidence. Identifiers, topics, source-language labels, rationales and answers are not inference features.
2. **Development confined to old data.** A regularized logistic model was fitted on the two previous 1,000-case datasets. Five family-disjoint folds selected regularization and a threshold. The classifier uses `C=0.01` and threshold `0.785`. These scores are not calibrated probabilities of translation error.
3. **A narrow extra-qualifier check.** It requires strong neutral evidence in the same direction in both comparisons, reverse entailment, an adequate translation-quality score, and an explicit extra qualifier. The fresh test revealed its limitations described above.
4. **More inspectable warnings.** Outputs include original bilingual spans, the machine gloss and word-level contrasts. This improves inspectability but does not guarantee correct localization, as K0138 demonstrates.

The pretrained LaBSE, multilingual DeBERTa and NLLB weights were retained. This work trained a small decision layer; it did not fine-tune the pretrained language models. No V7 dependency or paid model API was added.

The final development-selection result was 91.3%, with 28 false alarms among 1,400 old clean notices. That number is not held-out accuracy: it informed model and rule selection. The fresh 84.6% result is the relevant generalization test.

## Benchmark integrity and limitations

The model was frozen at 03:38:28 UTC on 15 November 2026. The new benchmark was frozen at 03:39:29. Prediction ran from 03:39:50 to 04:08:35. All source, model-revision, input and benchmark hashes were checked again afterward.

The benchmark contains 100 new scenario families with ten variants each, seven clean and three incorrect. It comprises 300 school notices, 300 government notices, 200 public emails and 200 formal instructions. English is authoritative in 600 cases and Chinese in 400. The predictor received only case ID, English and Chinese. The independent test agent reviewed completed batches while inference continued; no review feedback changed the predictor or frozen labels.

The four earlier corpora supplied 3,500 pairs for overlap checks. There were zero normalized exact notice matches. A closest-neighbor check found maximum normalized similarity of 0.7000 in English and 0.4242 in Chinese; the closest scenarios were reviewed as different. These checks support fresh wording but cannot prove complete semantic independence.

Notices contain one to four sentences. The longest were 359 English characters and 111 Chinese characters, with maximum embedding-token lengths of 73 and 113. This test does not cover long emails, attachments or all written Cantonese varieties. Its Chinese is formal Hong Kong written Traditional Chinese.

The benchmark and labels were AI-authored. Review recorded possible wording concerns in **31 cases across five families**, including an English piano-delivery notice whose object is only explicit in Chinese, “private” versus “personal” portfolio wording, and ambiguous transfer-reversal wording. The original labels were preserved. Excluding the listed cases yields 84.62%; even resolving every currently misclassified listed concern in the checker's favour would yield at most 85.1%. Neither is a replacement score, and neither changes the failure to reach 90%. Unlisted annotation problems may still exist; human validation remains necessary.

NLLB is supplied as a research model under CC-BY-NC-4.0, with document translation and production deployment outside its stated intended use. See the [official model card](https://huggingface.co/facebook/nllb-200-distilled-600M). It is used here as a research cross-check.

## Next development priorities

**First, compare requirement coverage explicitly.** Split notices into obligations, permissions, exclusions and informational claims. For each source claim, find a supported counterpart anywhere in the other notice; allow reordered and merged sentences. Preserve an explicit unmatched-claim state instead of attaching a missing sentence to an otherwise matching passage and averaging the result. K0009 is a direct development example.

**Second, resolve references before checking scope and exceptions.** Expand “first profile,” “section B,” “those cases” and similar references into the properties defined earlier in the notice. Compare the actor, action, object, condition and exception for the same instruction. This targets K0038, K0089 and K0111 more directly than another global threshold change.

**Third, replace operator-presence shortcuts with relation checks.** A conjunction can express the same relation as English “from,” “between” or a relative clause. The five callback-priority false alarms show why detecting an extra word is not detecting an extra requirement. The next candidate should distinguish changed logical scope from alternative syntax and be tested on both clean paraphrases and genuine added conditions.

**Fourth, verify translation evidence and warning localization.** A model-generated gloss that changes “previous page” to “top of the page” must not establish a source translation error by itself. Warnings should name the exact changed requirement, its counterpart or absence, and the supported difference. Where evidence is inconsistent, expose uncertainty separately from a confirmed discrepancy. Measure exact issue identification alongside notice-level accuracy.

**Finally, strengthen evaluation before claiming general accuracy.** Treat this benchmark as development data for any further changes. Prepare a separate evaluation from independently collected or independently authored notice families, including headings and context needed to judge permissible elaboration. Have bilingual human reviewers adjudicate the labels and a sample of warnings. Set accuracy, error recall, clean false-alarm and explanation-quality requirements before opening that evaluation.

These changes are recommendations for a subsequent candidate. They were not applied to the frozen V11 after testing.

## Deliverables

- [Frozen Colab notebook](</Users/aidenp/Desktop/Veritas AI Hackathon/candidate_v11/Public_Notice_Check_V11_frozen.ipynb>)
- [Complete benchmark and answer key](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v11/v11_blind_1000.csv>)
- [Exact inputs-only CSV](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v11/v11_blind_inputs.csv>)
- [Per-case results](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v11/case_results.csv>)
- [Warning audit](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v11/warning_audit.csv>) and [miss audit](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v11/miss_audit.csv>)
- [Independent test-agent report](</Users/aidenp/Desktop/Veritas AI Hackathon/holdout_v11/report.md>)
- [Code, data and results bundle](</Users/aidenp/Desktop/Veritas AI Hackathon/candidate_v11/V11_code_data_results.zip>)
