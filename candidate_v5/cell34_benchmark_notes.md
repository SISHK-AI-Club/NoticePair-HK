## 11. Approved 60-case regression benchmark

The next cell loads the embedded, checksum-verified CSV and runs V5 on all 60 notices. It saves `public_notice_v5_predictions.jsonl` and `public_notice_v5_run.json`. Reference labels are used only after predictions are complete. The historical dev/holdout split is reported for comparison; these cases are now development data.