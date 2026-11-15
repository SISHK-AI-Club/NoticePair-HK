# Version 4 benchmark

Run in the requested Colab notebook on the unchanged approved 60-case CSV. All 60 unique cases completed without execution errors. Observed runtime: CUDA; thresholds: similarity 0.4, contradiction 0.65. Checker code was unchanged. A temporary cell loaded the checksum-verified CSV; the existing benchmark cell 35 performed inference. The notebook is read-only in the connected account, so session changes were not saved to the source Drive file. Raw outputs were downloaded locally.

| Metric | Original | Alignment revision | V4 |
|---|---:|---:|---:|
| Accuracy, all 60 | 76.7% | 76.7% | 71.7% |
| Issue notices flagged /40 | 30 | 27 | 23 |
| Clean notices falsely flagged /20 | 4 | 1 | 0 |
| Original holdout accuracy /42 | 69.0% | 69.0% | 64.3% |

V4 development: 10 true positives, 6 true negatives, 2 false negatives, 0 false positives. Original holdout: 13 true positives, 14 true negatives, 15 false negatives, 0 false positives. Overall: 23 true positives, 20 true negatives, 17 false negatives, 0 false positives. Notice-level accuracy credits any warning on an incorrect notice and does not establish that its explanation identifies the planted error.

Compared with the alignment revision, V4 removes the N13-C false alarm but loses four issue detections: N06-1 (by Friday becomes after Friday), N13-1 (optional ticket becomes mandatory), N14-1 (working days become calendar days), N19-1 (already queued becomes joining after cutoff). Their previous generic contradiction scores were 53%, 42%, 31% and 64%, below the V4 threshold of 65%. N20-2 remains missed: the same-address exception is made conditional on different addresses. N13-2 still receives a numeric mismatch warning.

This is a reused regression suite, not a fresh held-out estimate of general translation accuracy. The 42-case split is retained for historical comparison. Results from the notebook’s separate government-notice datasets are not included in these numbers. Zero observed false alarms on 20 examples does not establish zero false alarms in deployment.

The higher threshold reduces warnings but leaves semantic gaps. The next change should target obligation, boundary and exception comparisons with evidence, while retaining clean paraphrase checks. Reversing the threshold alone would restore these generic warnings but would not explain the errors.
