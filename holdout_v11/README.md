# V11 bilingual notice holdout

The AI test agent authored this synthetic benchmark for Hong Kong public-facing English and formal written Traditional Chinese. It contains no user or institutional records.

| Split | Cases | Clean | Issue |
|---|---:|---:|---:|
| Routine | 600 | 420 | 180 |
| Difficult | 300 | 210 | 90 |
| Edge | 100 | 70 | 30 |
| Total | 1,000 | 700 | 300 |

School and government notices each contribute 300 cases. Public emails and instructions each contribute 200. The authoritative text is English in 600 and Chinese in 400. The issue is introduced only on the translation side. The labels file records which side is authoritative. The checker did not receive this information.

The 100 families each have seven clean pairs and three issue pairs. Variants share an operational rule. They vary the surrounding instructions, the order of bilingual content and, for selected difficult and edge families, the definition needed to apply a cross-sentence rule. The linked definitions remain present on both sides. Issues cover changes such as conditional scope, sequence, quantity, authority, permission, material requirements and omissions. Four corpus versions were checked for normalized overlap. Related cases within a family are statistically dependent, so score intervals resample whole families.

Routine notices contain one or two sentences per side. Difficult and edge notices contain two or three and three or four, respectively. The longest inputs were 359 English characters and 111 Chinese characters. Actual LaBSE tokenization gave maxima of 73 and 113 tokens, respectively, including special tokens.

- `v11_blind_inputs.csv` is the predictor's exact input. Its only columns are case ID, English and Chinese.
- `v11_blind_1000.csv` contains all case texts, gold labels, authority, explanatory rationale and bilingual evidence. A designation beginning with `[ABSENT` marks an omitted sentence.
- `build.py`, the four domain source files and `frozen_manifest.json` record the deterministic construction and pre-inference hashes. The builder requires Python 3.12 or newer.
- `score.py` checks frozen hashes, joins by case ID and computes metrics. `audit.py` records the separate AI review of warnings, missed issues and a stratified sample of true negatives.

The labels are authored and reviewed by an AI agent. Human validation and validation on independently collected real-world notices remain unmeasured.

The model source and benchmark files were both frozen before the first prediction. The test agent reviewed saved batches while later batches ran. No audit finding was passed to the predictor or used to change the labels. Wording concerns are recorded separately from the primary score.
