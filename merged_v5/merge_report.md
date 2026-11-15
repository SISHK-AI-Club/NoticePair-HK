# Merged V5 checker: results and remaining limits

The merged candidate achieved **60/60 correct classifications on the approved regression suite: all 40 incorrect notices flagged, with no false alarms on the 20 clean notices.** This improves our V5 candidate from 95.0% to 100.0% on these cases. It does **not** establish 100% accuracy on unseen notices.

[Open the saved merged Colab notebook](https://colab.research.google.com/drive/1HAfiCltH2fEHemm_yhopcZWrV6Bumo94?authuser=3). The teammate's notebook and our earlier candidate remain separate. No source notebook was overwritten.

## Comparison on the approved 60 cases

| Version | Incorrect notices flagged | Incorrect notices missed | Clean notices falsely flagged | Overall accuracy | Error recall |
|---|---:|---:|---:|---:|---:|
| Original prototype, saved earlier run | 30/40 | 10 | 4/20 | 76.7% | 75.0% |
| V4, saved earlier run | 23/40 | 17 | 0/20 | 71.7% | 57.5% |
| Teammate V5, fresh run | 23/40 | 17 | 0/20 | 71.7% | 57.5% |
| Our V5 candidate, fresh run | 37/40 | 3 | 0/20 | 95.0% | 92.5% |
| **Merged candidate, fresh run** | **40/40** | **0** | **0/20** | **100.0%** | **100.0%** |

Accuracy = (correctly flagged incorrect notices + correctly accepted clean notices) / all notices. For the merge, this is (40 + 20) / 60. Recall = 40/40; precision of notice warnings = 40/40. None of our V5's detections were lost.

The historical 42-case `holdout` portion scored 42/42: 28/28 incorrect notices flagged and 0/14 clean notices falsely flagged. The 18-case development portion scored 18/18. **Those 42 cases have already informed several revisions, so this is historical-split reporting, not a held-out estimate.**

## What was merged

The teammate's V5 source adds a wording-normalisation cell to the V4 checker. It handles biennial events, half-price expressions, ordinals such as “third,” futsal, non-negative words containing 別, and language-specific web links. These changes are useful, but they are rules around pretrained models rather than fine-tuning of model weights.

Our V5 adds supported comparisons for obligations, eligibility, exceptions, date boundaries and other semantic features. The merge retains those checks and the cautious model thresholds: similarity below 0.40 or contradiction above 0.65. It also retains one-to-one sentence matching and the 0.25 alignment cutoff.

The merge is more than concatenating the two patches:

1. **Normalise equivalent wording while preserving facts.** “兩年一度,” “biennially” and “every other year” resolve to an interval of two years. Annual versus biennial remains detectable. Half-price expressions resolve to 50%, so a 25% translation still differs.
2. **Separate links from language-model scoring, then compare their destinations.** Recognised language path prefixes and language query parameters may differ. Domains, remaining paths, content identifiers, other query values and fragments remain significant. Removing a link must not silently accept a different destination. This comparison does not fetch the linked pages or prove their content is equivalent.
3. **Fix the scope of Chinese obligation words.** In “須待…才可報名,” the requirement is to wait; registration is permitted afterwards. The closest supported modal before the action now determines its obligation, avoiding the old “must register” false warning.
4. **Compare document and condition relationships.** The checker now distinguishes a document's issuer from its named person, connects each ID form to its owner, and compares supported proxy-collection conditions.
5. **Improve explanations.** It explicitly compares one versus both required carers and unrestricted versus delayed registration for other eligible applicants.

The decision remains: flag when an existing rule or model warns, or when a supported paired semantic comparison differs. Added rules quote evidence from both languages and abstain when they cannot resolve the supported feature. They do not read benchmark IDs, labels or reference rationales. The pretrained LaBSE and mDeBERTa weights were not changed.

## What the merge recovered

| Case | Previous V5 behaviour | Merged explanation |
|---|---|---|
| N15-2 | Missed | Proof **issued by a parent** differs from proof **in the parent's name**. |
| N16-1 | Missed | Recipient ID is original instead of copy; proxy ID is copy instead of original. |
| N16-2 | Missed | Inability to collect becomes inability to attend the **original slot**, adding a restriction. |
| N13-2 | Flagged with an ambiguous number warning | One carer being sufficient differs from both companions being carers. |
| N18-2 | Flagged with a generic contradiction warning | Other eligible applicants must now wait until the priority period ends before registering. |

I reviewed all 40 incorrect-notice outputs against their approved rationales. All now identify a relevant planted difference, compared with 35 specific explanations in the previous V5 review. Some retained warnings are still terse number or negation messages; “specific issue identified” does not mean every explanation is equally polished or comprehensive. This is this assistant's review, not independent human or blind-agent adjudication.

## Additional checks for ambiguous wording

The same three checkers also ran through 34 development fixtures: 20 clean pairs and 14 intentionally different pairs. These examples were written while developing the merge; several closely resemble the 60-case suite. They must not be pooled into an independent 94-case accuracy claim.

| Version | Errors caught | Clean false alarms | Correct classifications |
|---|---:|---:|---:|
| Teammate V5 | 9/14 | 2/20 | 27/34 — 79.4% |
| Our V5 candidate | 11/14 | 10/20 | 21/34 — 61.8% |
| **Merged candidate** | **14/14** | **0/20** | **34/34 — 100.0%** |

These checks show why the two approaches complement each other. Our V5's zero false alarms on the original 20 clean notices did not extend to the broader wording examples. The teammate's patch resolved many of those problems, but still misread “every other year,” mishandled a bare URL adjacent to Chinese text, and missed changed domains and paths. The merge passed those examples while retaining detection of changed frequencies, percentages, ordinals and group negation.

Local verification also passed the prior 36 semantic guard pairs, the 38 new rule-level pairs (including four ambiguity/abstention checks), and a repeat-execution check for the new normalisation cell. Every saved code cell compiles. These are engineering checks, not independent linguistic validation.

## How this was tested and saved

All three fresh versions used the same loaded Colab T4 models, package environment and fixed thresholds. Each checker was built in a separate namespace from the saved source cells; fresh predictions were computed for every input. Existing V4 functions and thresholds were checked to remain unchanged. This used the already-running GPU session rather than starting another runtime.

Reference labels were consulted only after all inference finished. That prevents runtime answer leakage, but does not undo the fact that the examples informed development. The approved CSV's SHA-256 was checked before inference:

`eadcf4d7c6149e9656be2522f63977c25cb62fa6d0a206046ad96e8de746dfc1`

The separate merged Colab notebook contains the tested normalisation and checker sources and an embedded copy of that CSV. It was exported and all 39 cell sources were compared with the local build; they matched. The saved copy itself has not had a new end-to-end “Run all” session. The checker code was executed in the existing GPU session, and its result archive is preserved locally. The earlier starter experiments remain in the notebook; the final merged checker is installed in section 9 and the approved regression runner is in section 11. The demo launch is optional and disabled by default.

Recorded environment: Python 3.13.16, torch 2.14.1+cu130, transformers 5.22.1, sentence-transformers 5.7.0. See `results/run_metadata.json` for timestamps, source hashes, thresholds and all metrics. Future model downloads are not pinned to weight revisions, so the saved outputs are the reference for this run.

## How to improve real accuracy next

**Freeze this candidate before looking at a genuinely new evaluation set.** More tuning on these 60 examples will make the reported score less informative. Near-perfect performance on the current suite is already achieved; the next question is whether it transfers.

Prepare a new, human-reviewed set from different notice families. A useful next pilot is at least 120 cases, balanced between 60 clean notices and 60 incorrect ones. Include clean paraphrases as aggressively as errors. Have a fluent Hong Kong Traditional Chinese/Cantonese reviewer check the labels and evidence spans before model outputs are examined. Keep all variants of an underlying notice in the same split. Decide the scoring rules and freeze the checker before running it. Treat that result as one evaluation; later fixes need another untouched set.

The new set should test relationships and conditions in unfamiliar language: active/passive phrasing, pronouns, issued by versus issued to, documents held by several people, multiple exceptions, different logical scopes, inclusive boundaries, renamed organisations and URLs with content-specific identifiers. Include sentence merges/splits, paragraph reordering, long clauses and ambiguity that a human cannot confidently resolve. The current one-to-one alignment and limited grammars do not cover all of these.

For actual fine-tuning, collect a larger reviewed corpus with both clean and incorrect pairs, fault categories and evidence spans. Train the semantic classifier on that corpus; select its threshold on a separate development set. Use hard clean paraphrases to reduce false alarms and minimal meaning changes to improve recall. Preserve reliable deterministic checks for dates, quantities and explicit relationships. Evaluate the trained model against this frozen merged baseline before adopting it.

Report four measures separately: incorrect notices flagged, clean notices falsely flagged, correct identification of the actual problem, and cases needing human interpretation. A development objective can maximise error recall subject to zero observed false alarms, but zero observed false alarms in a small reused sample is not a guarantee for new notices. An uncertain result should lead to review, not a claim that the translation is correct.

The next meaningful milestone is strong performance on that untouched, independently labelled set—not another increase in the current 100% regression score.
