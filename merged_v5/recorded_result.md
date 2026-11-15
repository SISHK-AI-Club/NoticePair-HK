**Recorded Colab comparison · 14 November 2026**

| Checker | Incorrect notices flagged | Clean false alarms | Accuracy |
|---|---:|---:|---:|
| Teammate V5 | 23/40 | 0/20 | 71.7% |
| Our V5 candidate | 37/40 | 0/20 | 95.0% |
| **Merged candidate** | **40/40** | **0/20** | **100.0%** |

These are results on the **reused 60-case regression suite**, not unseen accuracy. The merge also passed 34/34 development fixtures. The tested sources ran in isolated namespaces in an existing Colab GPU session. This saved copy contains those sources; section 11 reruns the approved CSV. No model weights were fine-tuned.
