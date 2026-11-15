# V5 candidate: combining error detection with fewer false alarms

The fresh Google Colab run met the requested target on the approved 60-case regression suite: **37 of 40 incorrect notices flagged, no false alarms on 20 clean notices, and 57/60 correct classifications (95.0%).** The target was at least 35/40 with 0/20 false alarms.

[Open the saved V5 candidate](https://colab.research.google.com/drive/1Z-QgnJ2Mhyg36OX-f0IKqysXngiTCZ9x?authuser=3). The original and V4 source notebooks were not replaced.

## Verified comparison

| Measure | Original | V4 | V5 candidate |
|---|---:|---:|---:|
| Incorrect notices flagged | 30/40 | 23/40 | **37/40** |
| Incorrect notices missed | 10/40 | 17/40 | **3/40** |
| Clean notices falsely flagged | 4/20 | 0/20 | **0/20** |
| Error detection rate (recall) | 75.0% | 57.5% | **92.5%** |
| Precision of notice warnings | 88.2% | 100% | **100%** |
| Overall classification accuracy | 76.7% | 71.7% | **95.0%** |

V5 catches seven more incorrect notices than the original and fourteen more than V4. No V4 detections were lost. These are notice-level measures: a warning anywhere in an incorrect notice earns a detection, so explanations also need a separate review.

The historical 42-case split scores 39/42 (92.9%): 25/28 incorrect notices caught and 0/14 clean notices falsely flagged. The historical development split scores 18/18. **The 42 cases are no longer an unseen holdout:** their failures informed development. The headline 95% is a regression result, not an estimate of general translation accuracy.

## What combines the useful behaviour

Simply combining both versions' warnings with OR would preserve the original's false alarms. Requiring both versions to agree would discard useful detections. Instead, V5 retains V4's alignment and normalisation, retains its cautious model thresholds, and adds checks for specific meaning differences.

For each aligned pair, the decision is:

`flag = existing V4 warning OR supported semantic difference`

The existing model settings remain similarity below 0.40 or contradiction above 0.65. The new checks run independently of those thresholds. This restores detection of differences that the generic contradiction model scores too weakly to flag, without lowering its threshold for every sentence.

Each added check extracts a supported feature from both texts, compares the two values, and quotes the evidence. For example, English “must bring” resolves to **required**, while Chinese “可攜同” resolves to **permitted**. That is a specific obligation mismatch even if the sentences have high embedding similarity. Equivalent “must bring” and “須帶備” produce no warning from that check.

The rules use a limited set of patterns. They abstain when either side cannot be resolved or a supported feature is ambiguous. Abstention by a rule does not establish that the notice is clean; the existing model and other checks still run, and unsupported errors can remain missed. No benchmark IDs, reference labels or reference rationales enter the checker. The model weights were not fine-tuned.

## The fourteen recovered cases

| Cases | Difference now detected |
|---|---|
| N04-2, N11-1, N13-1 | Required versus permitted actions: bringing ID, submitting a form, reserving a ticket |
| N06-1 | By Friday versus after Friday |
| N09-2 | Fee-waiver eligibility moved from members to volunteers |
| N11-2 | A paper submission option added outside the approved exception; also an obligation change |
| N12-2 | Signal No. 8 included versus excluded from the cancellation threshold |
| N14-1 | Working days versus calendar days |
| N14-2 | Deadline counted from receipt versus issuance |
| N15-1 | Both documents versus either document |
| N17-2 | Induction for the new role versus the former role |
| N19-1 | People already queued at the cutoff versus people joining afterwards |
| N20-1 | Limit per household versus per address |
| N20-2 | Shared-address permission undermined by a different-address condition |

N05-2 was already flagged by V4; V5 also improves its explanation by identifying that a requirement for performers expands to all participants.

## Explanation quality and remaining misses

A manual review compared the output warnings with each bilingual pair and its approved rationale. **35 of the 40 incorrect notices have a clear explanation identifying the planted problem.** Two further notices are flagged but have weaker explanations:

- **N13-2:** The warning reports a numerical discrepancy involving 2. It does not distinguish the second ticket from the requirement for both companions to be carers. This report therefore withholds strict explanation credit, even though earlier reviews accepted the numeric warning more generously.
- **N18-2:** A generic contradiction warning locates a faulty passage but does not explain that allocation priority has become an earlier registration window.

The three missed notices are:

- **N15-2:** “Proof in your parent's name” becomes “proof issued by your parent.” The checker does not distinguish the document's named person from its issuer.
- **N16-1:** The recipient and proxy are assigned the wrong original/copy ID requirements. Both texts contain the same people and document types, but the relationships are swapped.
- **N16-2:** The Chinese adds an “original collection slot” restriction to proxy eligibility. This is an added condition rather than a simple word-level contradiction.

The full 60-row CSV includes every original input, approved rationale, version flag, V5 warning, extracted evidence and explanation-review outcome. The explanation review was performed by this assistant; it is not independent human or blind-agent adjudication.

## How to improve beyond this candidate

The next useful addition is comparison of relationships, not another global threshold reduction. Represent relevant instructions as facts containing **actor, action, object, owner, document form, obligation, condition and exception**. For N16-1, compare “proxy brings recipient's ID copy” and “proxy brings own original ID” separately. Matching the set of words or numbers cannot detect their ownership swap.

Before adding a rule or training a model for each relation, include equivalent phrasing and genuinely different phrasing. Examples should include active/passive wording, reordered conditions, pronouns with clear antecedents, original versus copy, issued by versus issued to, and original versus rescheduled collection times. Keep all variants of one underlying notice in the same dataset split.

For model fine-tuning, collect a larger set of human-reviewed bilingual pairs with labels and evidence spans. Include many difficult clean paraphrases as well as subtle errors. Train on those examples, select decision thresholds on a separate development set, and freeze both model and thresholds before an untouched evaluation. A useful development objective is to maximise error recall subject to zero observed false alarms on that development set. It does not guarantee zero false alarms on new notices.

Keep these 60 cases as a permanent regression suite. For a next independent pilot, prepare and approve at least 120 new cases, with 60 clean and 60 incorrect notices from different notice families. Have a Cantonese/Traditional Chinese reviewer confirm the labels before the model outputs are examined. Measure notice detection, correct error explanation, false alarms and unresolved cases separately. Avoid changing the checker after seeing those test results and continuing to call the same set held out.

Zero false alarms on 20 clean examples is encouraging but limited evidence. For a stronger claim about a low false-alarm rate, collect substantially more independently sourced clean notices. With zero errors among 300 independent, representative clean cases, the exact one-sided 95% binomial upper bound is `1 - 0.05**(1/300)`, approximately 1%. This is a sampling statement, not a deployment guarantee.

## Execution and reproducibility

- Run started 14 November 2026 at 12:38:40 UTC / 20:38:40 Hong Kong time; device CUDA.
- All 60 unique approved cases completed without execution errors. Predictions matched the preliminary saved-output replay exactly, including every output row and explanation.
- Colab initially refused a second GPU session. The approved idle V2 session was stopped. The fresh candidate inference ran using the already loaded models in the V4 GPU session, with candidate functions defined in a separate namespace. An assertion verified that V4's checker functions and thresholds remained unchanged.
- The saved V5 copy contains the tested checker and benchmark code. Its exported code was compared with the local tested sources and all Python cells passed syntax checks. The optional demo is disabled by default. Older copied outputs were cleared to avoid confusing V4 results with V5 results.
- The added semantic checks pass 36 targeted development examples: 18 equivalent pairs, 14 contrasting pairs and 4 ambiguous/unsupported pairs. These are unit examples, not an additional unseen benchmark.
- Approved CSV SHA256: `eadcf4d7c6149e9656be2522f63977c25cb62fa6d0a206046ad96e8de746dfc1`.
- Semantic rules SHA256: `db4a728eda1effb35afcad0a5af5720e41e4a4bb4c7c179202458bf1e7e028d7`.
- The run record contains package versions, thresholds, time and split metrics. Raw predictions and the case comparison are saved alongside this report.

This benchmark concerns meaning consistency in the supplied English and written Traditional Chinese notices; it does not establish broad spoken Cantonese translation quality.
