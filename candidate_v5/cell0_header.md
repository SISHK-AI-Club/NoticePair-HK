# Public Notice Check (V5 candidate)

This candidate retains V4's alignment, normalisation and cautious model thresholds, and adds paired evidence checks for obligations, eligibility, boundaries and exceptions.

**Reproduce:** Runtime → Run all. The approved 60-row CSV is embedded in the regression cell. Models download on the first run. The benchmark sends only the Chinese and English text to the checker; reference labels are used afterwards to score the results.

**Evaluation limit:** These 60 cases were inspected during development. Scores on them describe regression performance, not accuracy on unseen notices. The new semantic rules use a limited grammar and abstain when they cannot recognise a supported feature on both sides. Model weights are unchanged.

The source V4 notebook remains separate. Review the evidence and make the final publication decision yourself.

## Verified regression result — 14 November 2026

| Metric | Original | V4 | V5 candidate |
|---|---:|---:|---:|
| Incorrect notices flagged /40 | 30 | 23 | **37** |
| Clean notices falsely flagged /20 | 4 | 0 | **0** |
| Overall accuracy /60 | 76.7% | 71.7% | **95.0%** |

The fresh Colab GPU run completed all 60 cases without execution errors at 20:38 Hong Kong time. It used this candidate's checker and benchmark code in an isolated namespace in the existing V4 GPU session because the new session was initially unavailable. An assertion confirmed that V4's functions and thresholds remained unchanged. Predictions matched the preliminary saved-output replay exactly.

The historical 42-case split scored 39/42 (92.9%), but those cases have now been used in development and are no longer unseen holdout data. Three cases remain missed: N15-2 (issuer versus named owner of proof), N16-1 (original/copy assigned to the wrong people), and N16-2 (proxy eligibility narrowed to the original collection slot).

Sections 1–8 retain the V4 baseline workflow. **Section 9 installs V5; section 11 runs the approved 60-case regression.** The optional demo is disabled by default. The numbers above record the verified run; running the benchmark again regenerates its outputs.
