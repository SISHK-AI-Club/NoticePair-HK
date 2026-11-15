# Public Notice Check — Merged V5 candidate

**Recorded Colab comparison · 14 November 2026**

| Checker | Incorrect notices flagged | Clean false alarms | Accuracy |
|---|---:|---:|---:|
| Teammate V5 | 23/40 | 0/20 | 71.7% |
| Our V5 candidate | 37/40 | 0/20 | 95.0% |
| **Merged candidate** | **40/40** | **0/20** | **100.0%** |

These are results on the **reused 60-case regression suite**, not unseen accuracy. The merge also passed 34/34 development fixtures. The tested sources ran in isolated namespaces in an existing Colab GPU session. This saved copy contains those sources; section 11 reruns the approved CSV. No model weights were fine-tuned.

Combines our V5 semantic evidence checks with the teammate's V5 wording fixes, and adds bounded checks for document relationships and proxy conditions.

**Evaluation:** the approved 60 cases are a reused regression suite. They are no longer an unseen holdout. No general accuracy claim follows from a perfect result here.

Run cells in order. Sections before the whole-notice checker retain the inherited starter experiments; the merged checker is installed in section 9. Section 11 embeds the approved CSV and runs the final merged checker with fixed thresholds (similarity 0.40, contradiction 0.65). The optional demo does not launch automatically.

The merge preserves event frequency and link destinations when normalising wording. Every added semantic warning includes evidence from both languages. Unsupported or ambiguous patterns are left to the existing models; this remains a finite grammar, not a general language reasoner.

Sources: [teammate V5](https://colab.research.google.com/drive/1zQgH25wQDPfQEKq7658q24PqS2GsXQH9) and our saved V5 candidate. Pretrained model weights are unchanged. Source notebooks have not been overwritten.
