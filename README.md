# NoticePair HK v11

**A last check before a bilingual notice goes out.**
Veritas AI International High School Hackathon 2026 · Track: AI + Languages · SISHK AI Club

A programme coordinator at a Hong Kong community centre, charity or school pastes the Traditional Chinese and English
versions of a notice. The checker compares them and flags places where the two versions tell readers different things
(a deadline, a fee, a weight, who qualifies, what to do), and explains why. A person always makes the final call.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SISHK-AI-Club/Veritas-AI-Hackathon/blob/main/NoticePair_HK_v11.ipynb)

## Why it matters

Hong Kong notices are published in two languages, and the English is not always checked as carefully as the Chinese. A
wrong date, a dropped "not", or a deadline swapped with the event date can send families to the wrong place on the wrong
day. A spell checker cannot see these mistakes: each sentence reads perfectly well on its own, and the error only shows
up when the two versions are compared.

## How V11 works

1. **Three pretrained models** (used as released, not retrained):
   - **LaBSE** matches Chinese and English passages and measures how similar they are.
   - **mDeBERTa NLI** scores whether one version contradicts, supports or says nothing about the other, in both
     directions.
   - **NLLB-200** translates the Chinese into English as a cross-check (never as the answer key).
2. **178 signals per notice**, for the whole notice and for each matched passage: contradiction, support and neutral
   scores, similarity and translation quality.
3. **Hand-written fact checks** compare clear facts that appear exactly once in each version: numbers (including
   Chinese numerals such as 六千三百), amounts with units, dates, clock times, colours, languages, file formats, email
   addresses, web links, and must / may / need-not wording.
4. **A missing-detail rule** flags a condition ("unless", "except", 除非 ...) that appears in only one version, but only
   when both model views agree the other version lacks it.
5. **A small trained classifier** (logistic regression over the 178 signals plus whether a fact check found a conflict,
   which is its strongest single signal) turns everything into one score. A notice is flagged at 0.785 or above, or
   when the missing-detail rule fires. This classifier is the only part that was trained.

V11's code is shown file by file in the notebook, with notes. Every file is checked against the SHA-256 checksum recorded
when V11 was frozen, so the code that produced the results below cannot have been changed afterwards.

## Results

Each test was scored once, after V11 was frozen.

| Test | Data | Accuracy | Errors caught | False alarms | How blind? |
|---|---|---|---|---|---|
| **Newest real notices** | 38 sentence pairs from 3 government press releases of 13 Nov 2026 | **78.9%** | 13 / 18 | 3 / 20 | Built after V11 was frozen |
| **Unseen-topic synthetic notices** | 1,000 notices from 38 topic families not in V11's training data | **90.8%** | 211 / 300 | 3 / 700 | Our team had seen these topics while building V9 |
| Earlier real notices | 47 pairs from 4 government press releases | 80.9% | 15 / 21 | 3 / 26 | Available to the team before V11 |

**What this shows.** V11 rarely raises false alarms (3 in 700 on the synthetic set), and it handles topics it was not
trained on. On real government notices it scores about 80%, lower than on synthetic ones: real notices are longer and
phrased more freely.

**How we got here.** The earlier versions are in this repository's history:
- **v2 to v6** combined the pretrained models with hand-written rules. Final blind test on real notices (v4): the
  baseline length rule caught 0 of 21 errors, the rules alone 15, the models alone 17, and the combined checker
  19 of 21, with 7 false alarms on 26 correct sentences.
- **V8 and V9** added more rules and 31 hand-written clause patterns. V9 scored 97.9% on the 1,000 cases it was built on,
  but only **77.5% on 1,000 new-topic cases, exactly the same as V8**: the patterns had learned the test generator's
  templates, not the task. That lesson is why V11 learns how to combine model signals instead.
- **A V12 experiment** retrained V11's classifier on 3,000 cases. It caught more errors but raised more false alarms
  (89.2% with 40 false alarms on the synthetic test; 77.6% on real notices), so we kept V11.

## Where it fails

- **Awkward but not wrong English is invisible.** "Carefully slip" for 小心地滑 is not flagged, because nothing in it
  contradicts the Chinese.
- **Spaced thousands.** V11's number rules read Government-style "6 300 grams" as 300 g, which caused a false alarm on a
  real Customs press release. The demo app now joins such numbers before checking; the scores above did not use this.
- **Long notices.** Notices longer than about 300 Chinese characters exceed what the models can read in one piece. V11
  refuses them rather than silently cutting text; the demo then checks them paragraph by paragraph.
- **Real notices are harder** than synthetic ones, and our real-notice tests are small (85 sentence pairs).
- **Some fact checks match test topics closely.** Seven of the 38 synthetic test topics are fully covered by V11's fact
  rules (money, clock times, weights, colours, file formats), which is why we do not call that test fully blind.

## Files

| File | What it is |
|---|---|
| `NoticePair_HK_v11.ipynb` | **V11, the current version.** Readable checker code, a single example and a Gradio demo app. |
| [V9 development comparison](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/blob/99b3d67/V9_development_comparison.ipynb) | Frozen V8 vs V9 on V9's 1,000 development cases. |
| `data/` | All test and training files: `notices.csv`, `fresh_test.csv`, `fresh_test_2.csv`, `fresh_test_3.csv`, `v9_development_1000.csv`, `v9_unseen_1000.csv`. |

## Version history

Browse the [commit history](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/commits/main/) or open a version below.

[v2](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v2) · [v3](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v3) · [v4](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v4) · [v5](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v5) · [v6](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v6) · [v7](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v7) · [v8](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v8) · [v9](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v9) · [v10](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v10) · [v11](https://github.com/SISHK-AI-Club/Veritas-AI-Hackathon/tree/v11)

v2–v6 point to the original published commits. The v7 tag contains the frozen checker source recovered from the v8 comparison. v8–v10 include the saved notebooks and evaluation files, and v11 is the final NoticePair HK version. The original benchmark is archived with the project materials.

## Run it

1. Open `NoticePair_HK_v11.ipynb` in Google Colab.
2. *Runtime → Change runtime type → T4 GPU.*
3. *Runtime → Run all.* The first run downloads the three models (about 5 GB). The demo app appears near the end; it
   needs no data files.

## Data

- Real notices are Hong Kong Government press releases from [info.gov.hk](https://www.info.gov.hk/gia/general/). The
  correct sentences are the government's own text; the broken English versions were written for testing. Each file's
  `source` column links the release.
- `notices.csv` and the 1,000-case sets are synthetic. No personal information is used anywhere.

## Credits

- Models: LaBSE (Feng et al.); mDeBERTa-v3 XNLI (Laurer et al., MIT licence); NLLB-200 distilled 600M (Meta,
  CC-BY-NC 4.0, non-commercial research use)
- Libraries: sentence-transformers, transformers, PyTorch, scikit-learn, pandas, NumPy, SciPy, OpenCC, Gradio
- Platform: Google Colab
- Data: Hong Kong Government press releases (info.gov.hk)
