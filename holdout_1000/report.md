# V8 on 1,000 unseen synthetic notices

V8 accuracy was 81.4%. V7 and V8 agreed on 1,000 of 1,000 decisions.
V8 caught 248 of 300 incorrect notices and flagged 134 of 700 clean notices.
Error recall was 82.7% and the false-alarm rate was 19.1%.
Decision paths recorded: {'frozen_fallback': 1000}.

| Difficulty | V7 accuracy | V8 accuracy | V8 caught | V8 missed | V8 false alarms |
|---|---:|---:|---:|---:|---:|
| Routine | 88.5% | 88.5% | 165 | 15 | 54 |
| Difficult | 68.0% | 68.0% | 60 | 30 | 66 |
| Edge | 79.0% | 79.0% | 23 | 7 | 14 |
| Overall | 81.4% | 81.4% | 248 | 52 | 134 |

Both versions ran in Colab against the same checksum-verified CSV using shared model objects. Stable V8 source identity was verified against the previous source manifest.

The original 500-case score measured a development set. This benchmark uses 38 new scenario families with repeated structures within each family. The 70% clean share also yields 70% accuracy for an always-clean predictor, so error recall and false alarms should accompany accuracy.

## Results by scenario family

| Difficulty | Scenario | Cases | Caught | Missed | False alarms |
|---|---|---:|---:|---:|---:|
| Routine | Collection fee | 36 | 14 | 0 | 0 |
| Routine | Locker assignment | 37 | 10 | 0 | 0 |
| Routine | Document format | 37 | 6 | 0 | 0 |
| Routine | Equipment limit | 38 | 9 | 0 | 0 |
| Routine | Envelope marking | 37 | 14 | 0 | 0 |
| Routine | Entrance colour | 39 | 9 | 6 | 0 |
| Routine | Offline retention | 39 | 8 | 0 | 0 |
| Routine | Equipment weight | 37 | 16 | 0 | 0 |
| Routine | Contact routing | 38 | 10 | 0 | 0 |
| Routine | Counter hours | 38 | 12 | 0 | 0 |
| Routine | Record destination | 37 | 0 | 9 | 0 |
| Routine | Refund amount | 38 | 13 | 0 | 0 |
| Routine | Code location | 37 | 10 | 0 | 27 |
| Routine | Handback destination | 37 | 15 | 0 | 0 |
| Routine | Quantity in bundle | 37 | 8 | 0 | 0 |
| Routine | Collection channel | 38 | 11 | 0 | 27 |
| Difficult | Scope of requirement | 25 | 6 | 0 | 0 |
| Difficult | Refund exclusion | 25 | 11 | 0 | 14 |
| Difficult | Eligibility boundary | 25 | 6 | 1 | 0 |
| Difficult | Fallback channel | 26 | 3 | 4 | 0 |
| Difficult | Permission versus duty | 25 | 0 | 4 | 0 |
| Difficult | Actor responsibility | 25 | 3 | 3 | 0 |
| Difficult | Scope of cancellation | 25 | 5 | 0 | 20 |
| Difficult | Time anchor | 24 | 7 | 0 | 17 |
| Difficult | Priority rule | 25 | 9 | 0 | 0 |
| Difficult | No implied threshold | 24 | 0 | 7 | 0 |
| Difficult | Acknowledgement | 26 | 0 | 11 | 0 |
| Difficult | Role reversals | 25 | 10 | 0 | 15 |
| Edge | Exception to exclusion | 10 | 0 | 4 | 0 |
| Edge | Cross reference | 10 | 2 | 0 | 8 |
| Edge | Grid assignment | 10 | 4 | 0 | 6 |
| Edge | Boundary on continuation | 10 | 3 | 0 | 0 |
| Edge | Embedded quotation | 10 | 1 | 3 | 0 |
| Edge | Scope in footnote | 10 | 3 | 0 | 0 |
| Edge | Exception precedence | 10 | 2 | 0 | 0 |
| Edge | Linked conditions | 10 | 3 | 0 | 0 |
| Edge | Retained earlier condition | 10 | 2 | 0 | 0 |
| Edge | Relative deadline | 10 | 3 | 0 | 0 |

The per-case CSV supplies bilingual evidence and unedited checker warnings. Counts measure whether a warning appeared. Explanation correctness was not manually adjudicated.
