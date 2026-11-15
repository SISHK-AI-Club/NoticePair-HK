# How to read the V10 results

The checker is frozen before the first new holdout prediction. Its code hash, component revisions and selected thresholds are recorded in `frozen_manifest.json`. The GPT-6.1 Sol testing agent runs at medium reasoning effort; it creates and evaluates the new benchmark but is not the translation-checking model.

The fresh benchmark contains 1,000 synthetic notices: 700 clean and 300 incorrect. Its difficulty mix is 600 routine, 300 difficult and 100 edge cases. These are 100 scenario families with three authored linguistic frames per family, not 1,000 unrelated real-world documents. Labels are authored rather than independently human-validated.

The original frozen input file also contains `source_language`. The predictor requires exactly the identifier and two text columns. A separately hashed, verified projection removes only that metadata field; every case ID and both text strings remain identical. The original dataset and answer key remain unchanged. No ground-truth label or rationale is available to the prediction function.

## Measures

- **Accuracy:** (incorrect notices flagged + clean notices left unflagged) / 1,000.
- **Error recall:** incorrect notices flagged / 300. This is the share of actual errors detected.
- **Warning precision:** incorrect notices flagged / all flagged notices.
- **False-alarm rate:** clean notices flagged / 700.
- **Issue identification:** whether the warning identifies the seeded discrepancy. A generic review request or a whole-notice quote does not, by itself, establish this.
- **Unresolved coverage:** inputs the checker cannot process completely. These are reported separately and are not credited as an accurately explained issue.

A checker which always accepts a notice would score 70% accuracy on this mix and catch no errors. Consequently accuracy must be read with recall and false alarms. A 90% observed score on this synthetic benchmark does not establish 90% accuracy on all school or government notices. Family-clustered uncertainty accounts for correlation between related examples more honestly than treating all rows as independent.

The earlier V9 dataset is reused for development and a matched comparison. Those results answer whether V10 improved on the same old notices. Only the untouched new set answers the fresh-holdout question. No rule or threshold will be changed in response to this holdout within V10.
