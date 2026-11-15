# Matched comparison on the previous V9 benchmark

These are the exact same 1,000 notices used for the prior frozen V9 result, including their original headings, reference identifiers and formatting. V10 was developed using this data, so its score here is **development evidence**, not held-out accuracy.

| Difficulty | V9 accuracy | V10 accuracy | V9 caught / missed / false alarms | V10 caught / missed / false alarms |
|---|---:|---:|---:|---:|
| Overall | 77.5% | 94.7% | 238 / 62 / 163 | 247 / 53 / 0 |
| Routine | 76.5% | 97.5% | 131 / 49 / 92 | 165 / 15 / 0 |
| Difficult | 79.7% | 91.3% | 78 / 12 / 49 | 64 / 26 / 0 |
| Edge | 77.0% | 88.0% | 29 / 1 / 22 | 18 / 12 / 0 |

V10 fixed 209 notice decisions and regressed 37. Decision paths: {'v10_contextual_comparison': 1000}. Coverage: {'complete_notice': 1000}.

An incorrect notice with any warning counts as caught in this table. That does not establish that the warning explains the actual issue. The fresh holdout report includes a separate warning-quality audit.

| Scenario family | V10 missed | V10 false alarms |
|---|---:|---:|
| Boundary ownership | 8 | 0 |
| Archive attribution | 5 | 0 |
| Reporting denominator | 8 | 0 |
| Science specimen | 10 | 0 |
| Superseding map layer | 5 | 0 |
| Grandfathered classification | 2 | 0 |
| Consent inheritance | 3 | 0 |
| Calibration mark | 5 | 0 |
| Label reference frame | 5 | 0 |
| Units across a mode change | 1 | 0 |
| Cancellation message scope | 1 | 0 |
