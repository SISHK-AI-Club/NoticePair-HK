# Frozen V9 on 1,000 new synthetic notices

| Group | Cases | Accuracy | Caught | Missed | False alarms |
|---|---:|---:|---:|---:|---:|
| Overall | 1000 | 77.5% | 238 | 62 | 163 |
| Routine | 600 | 76.5% | 131 | 49 | 92 |
| Difficult | 300 | 79.7% | 78 | 12 | 49 |
| Edge | 100 | 77.0% | 29 | 1 | 22 |
| Stage cue | 62 | 100.0% | 19 | 0 | 0 |
| Science specimen | 60 | 25.0% | 15 | 3 | 42 |
| Instrument tuning | 58 | 100.0% | 17 | 0 | 0 |
| Assessment aggregation | 31 | 100.0% | 10 | 0 | 0 |
| Archive attribution | 30 | 93.3% | 7 | 2 | 0 |
| Attendance classification | 29 | 31.0% | 9 | 0 | 20 |
| Consent inheritance | 15 | 26.7% | 4 | 0 | 11 |
| Assessment dependency | 15 | 26.7% | 4 | 0 | 11 |
| Survey datum | 62 | 88.7% | 12 | 7 | 0 |
| Recycling material | 60 | 81.7% | 7 | 11 | 0 |
| Print orientation | 58 | 8.6% | 5 | 12 | 41 |
| Consultation identity publication | 32 | 71.9% | 10 | 0 | 9 |
| Boundary ownership | 30 | 76.7% | 1 | 7 | 0 |
| Reporting denominator | 28 | 28.6% | 8 | 0 | 20 |
| Superseding map layer | 15 | 100.0% | 5 | 0 | 0 |
| Grandfathered classification | 15 | 100.0% | 5 | 0 | 0 |
| Caption language | 42 | 69.0% | 0 | 13 | 0 |
| Exhibition medium | 40 | 100.0% | 12 | 0 | 0 |
| Transcript page | 38 | 100.0% | 11 | 0 | 0 |
| Thread visibility | 22 | 100.0% | 7 | 0 | 0 |
| Renewal effect | 20 | 100.0% | 6 | 0 | 0 |
| Attachment replacement | 18 | 100.0% | 5 | 0 | 0 |
| Cancellation message scope | 10 | 100.0% | 3 | 0 | 0 |
| Individual versus shared edits | 10 | 100.0% | 3 | 0 | 0 |
| Glyph orientation | 42 | 92.9% | 10 | 3 | 0 |
| Calibration mark | 40 | 77.5% | 12 | 0 | 9 |
| Paper fold | 38 | 100.0% | 11 | 0 | 0 |
| Reset persistence | 22 | 100.0% | 7 | 0 | 0 |
| Label reference frame | 20 | 85.0% | 3 | 3 | 0 |
| Sorting key | 18 | 100.0% | 5 | 0 | 0 |
| Branch convergence | 10 | 100.0% | 3 | 0 | 0 |
| Units across a mode change | 10 | 90.0% | 2 | 1 | 0 |

Decision paths: {'frozen_fallback': 1000}.

The 1,000 rows represent 32 synthetic scenario families with repeated wording and layout variants within each family. The score measures this benchmark mix. Notice-level detection credits any warning on an incorrect notice.

Dataset SHA-256: `e99de209ce48848ea2d4ff3a1a68adcb421600265a0043926be9bdc673fa13e9`

Frozen V9 SHA-256: `2497f00d26f076da74278c300d619e585657e04bf3c59dd21109580c7dedaf92`
