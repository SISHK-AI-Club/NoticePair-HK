# V11 frozen bilingual notice checker

V11 targets mismatched scope, exceptions and omitted conditions. It keeps the V10 neural models and adds a regularized equivalence classifier plus a narrow, corroborated qualifier-loss check. There is no V7 fallback and no paid API call. The Codex testing agent is GPT-6.1 Sol with medium reasoning; the checker itself uses the pretrained models recorded in the manifest.

## Changes

- Uses both entailment and neutral evidence in both directions, alongside contradiction, embedding similarity, back-translation quality and explicit bilingual facts. Two statements can both be true while failing to translate each other completely.
- Learns a small decision head from the two old 1,000-case datasets. Case identifiers, topics, reference rationales and labels are excluded from inference features.
- Selects regularization and a threshold using five family-disjoint folds. The selection target allowed up to 2% false positives among clean development notices; this is not a guarantee on fresh data.
- Adds an extra-condition check requiring strong one-way information loss in both original bilingual and back-translated comparisons, reverse entailment, and an additional explicit qualifier. Missing operator words alone do not flag a pair.
- Quotes the relevant English and Chinese passages and exposes machine-gloss differences. Machine glosses can be wrong, so a detection and a correct explanation are evaluated separately.

## Freeze and evaluation

`frozen_manifest.json` records the exact inference source, exported coefficients, threshold and pretrained model revisions. The model was frozen before the new benchmark and before its first prediction. The fresh benchmark is in `../holdout_v11/`, with 600 routine, 300 difficult and 100 edge cases, and 70% clean / 30% incorrect within each tier. It uses 100 related scenario families, each containing ten cases. All fresh predictions and references remain unchanged after evaluation.

The old datasets are now development data. Their scores and the fold-selection scores are not held-out accuracy. The actual fresh results and independent warning review are recorded in `V11_report.md` after the run.

## Running

Open `Public_Notice_Check_V11_frozen.ipynb` in Colab. Run the setup cells and upload `v11_blind_inputs.csv` when prompted. Keep the answer-key CSV separate until predictions are complete. The notebook contains a verified copy of every frozen inference file. It has not been executed in Colab in this task; the recorded benchmark runs in the local CPU environment documented in the manifest.

Command-line use:

```bash
python candidate_v11/run.py --inputs holdout_v11/v11_blind_inputs.csv --output holdout_v11/v11_results.json --cache holdout_v11/inference_cache.json --require-frozen
```

The input CSV has exactly three columns: `case_id,english,chinese`. The output contains warnings, model signals, coverage, freeze hashes and runtime metadata. Oversized or failed comparisons are explicitly marked unresolved; they must not be treated as checked clean notices.

## Limits

These are agent-authored synthetic notices with agent-reviewed labels, not a representative sample of real correspondence. Difficulty labels are editorial judgments. A 70% clean benchmark has a 70% always-clean baseline, so recall and false-alarm rates matter alongside accuracy. Related cases within families are not statistically independent.

The input notices must fit the models' context windows. The benchmark checks actual embedding token lengths, not just character counts. This version has not been validated on long letters, attachments, tables or every formal Cantonese variety. Its decision score is not a calibrated probability. The back-translation model and NLI models can make correlated mistakes. The NLLB component is a research model under CC-BY-NC-4.0: https://huggingface.co/facebook/nllb-200-distilled-600M.
