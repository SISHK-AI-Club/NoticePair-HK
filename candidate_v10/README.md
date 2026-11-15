# V10 contextual notice checker

V10 removes the V7 fallback. Every valid short notice goes through the same contextual comparison. It does not require a known notice template or an exact full-sentence regular expression.

1. Unicode is normalised without deleting negation or quantities. The bilingual input is kept separate from benchmark labels.
2. LaBSE matches related passages, permitting sentence reordering and attaching unmatched sentences to related groups. Unequal sentence counts alone do not create an alarm.
3. Explicit bilingual facts compare quantities with units, dates, weekdays, identifiers and supported semantic properties. A property must be resolved on both sides. Chinese characters inside words such as 百分比 do not become arbitrary numeric discrepancies. Equivalent unit conversions are accepted.
4. NLLB translates each Chinese sentence into English independently, retaining all sentence translations. Its internal source is converted to Simplified Chinese with OpenCC; the original Traditional Chinese is retained for direct comparison and evidence. A bounded, published glossary anchors technical vocabulary. This is terminology normalisation, not a template whitelist. This is a supporting model, not the answer key.
5. mDeBERTa compares both directions of the original bilingual pair and the English/back-translated pair, at complete-notice and aligned-passage levels. Fixed development-selected thresholds govern semantic warnings.
6. Warnings include both source excerpts. Explicit facts name the differing values. Semantic warnings include the machine back-translation and textual differences, and remain model-based review requests.

The pretrained weights are not fine-tuned. V10 changes the comparison architecture, evidence checks and decision policy. It is not a GPT translation checker: GPT-6.1 Sol with medium thinking is the independent dataset/testing agent.

## Reproduce

Install `requirements.txt`, then run:

```bash
python candidate_v10/run.py --inputs holdout_v10/v10_runner_inputs.csv --output holdout_v10/v10_results.json --cache /tmp/v10_cache.json --require-frozen
```

The input CSV must contain only `case_id`, `english` and `chinese`. The runner rejects answer-key columns, verifies frozen source hashes, records component versions and writes raw predictions before scoring. Use `Public_Notice_Check_V10_frozen.ipynb` in Colab for the same frozen code.

## Evidence and limits

Old V9 benchmark data is now development data for V10. Scores on it cannot establish unseen accuracy. The fresh Sol-authored holdout is created independently and frozen before the first prediction. Related cases share scenario families, so row-level accuracy is not equivalent to 1,000 independent real notices. The public test report should include family-aware uncertainty and distinguish a detected notice from an accurately identified issue.

The checker has a 6,000-character front-end limit and a smaller validated model-context limit. Inputs exceeding the token window are explicitly marked unresolved; later text is never silently truncated. Current benchmark notices fit the validated short-notice scope. Long-document processing needs a separately validated windowing method.

Local inference uses LaBSE, mDeBERTa and [NLLB-200 distilled 600M](https://huggingface.co/facebook/nllb-200-distilled-600M). NLLB is a research model, is not intended for production deployment or certified translation, and has a noncommercial licence. This matters before turning the prototype into a deployed product. All three model revisions are pinned in the source; the test records dependency versions.
