# Public Notice Check

**A last check before a bilingual notice goes out.**
Veritas AI International High School Hackathon 2026 · Track: AI + Languages · SISHK AI Club

A programme coordinator at a Hong Kong community centre, charity or school pastes the Traditional
Chinese and English versions of a notice. The checker matches the sentences, flags places where the
two versions tell readers different things (a deadline, a fee, who qualifies, what to do), and
explains why. A person always makes the final call.

[![Open V9 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SISHK-AI-Club/Veritas-AI-Hackathon/blob/main/V9_development_comparison.ipynb)
&nbsp;V9 checker &nbsp;·&nbsp;
[![Open the full notebook in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SISHK-AI-Club/Veritas-AI-Hackathon/blob/main/Public_Notice_Check.ipynb)
&nbsp;Full pipeline and demo

## Why it matters

Hong Kong notices are often published in two languages, and the English is not always checked as
carefully as the Chinese. A single wrong date, a dropped "not", or a deadline swapped with an event
date can send families to the wrong place on the wrong day. A spell checker does not catch these
mistakes: each sentence reads perfectly well on its own, and the error only shows up when you
compare the two versions.

## How the V9 checker works

Each notice goes through three layers.

1. **Clause facts (new in V9).** Each language is parsed **on its own** against 31 hand-written
   clause patterns: fees, refunds and waivers, age eligibility, who pays postage, where a signed
   original goes, which entrance to use, and so on. Each fact found once in both versions is
   compared value by value, and any difference becomes a warning that quotes the exact words in
   each language. Text the patterns do not recognise is not skipped: it goes on to the next two
   layers.
2. **Evidence rules (V8).** Our hand-written checks for numbers (including Chinese numerals and
   years like 二○二六), clock times, negation, application deadline vs event date, weekdays,
   actions (bring, submit, pay, register), and web links (a `/tc/` vs `/en/` page is the same
   link). Each rule **abstains** when it cannot read a feature on both sides, instead of guessing.
3. **Pretrained models.** [LaBSE](https://huggingface.co/sentence-transformers/LaBSE) matches
   sentences across languages (one-to-one, so reordered paragraphs still line up), and
   [mDeBERTa NLI](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)
   gives the probability that two sentences contradict each other, asked in both directions.

Locked settings: flag if similarity < 0.40 or contradiction > 0.65. The model weights are used as
released; we did not fine-tune them.

**What is pretrained and what is ours.** LaBSE and mDeBERTa are pretrained by others. The rules,
the clause grammar, the logic that combines everything, the test data and the evaluation are ours.

## Results

We report errors caught and false alarms separately, and we say which numbers are blind.

| Test | Data | Errors caught | False alarms | Blind? |
|---|---|---|---|---|
| **Final blind test** (v4) | 47 sentence pairs from 4 real info.gov.hk press releases | **19 / 21** | **7 / 26** | **Yes, scored once** |
| First blind test (v3) | 48 pairs from 4 other real press releases | 20 / 22 | 12 / 26 | Yes, then used to fix bugs |
| V9 vs V8 comparison | 1,000 synthetic notices | V8 248 / 300 → **V9 293 / 300** | V8 134 / 700 → **V9 14 / 700** | No, development |
| Development set (v3, v4) | 73 pairs in `notices.csv` | 33 / 37 | 0 / 36 | No, development |

On the final blind test the plain baseline (a length rule) caught 0 of 21 errors, our rules alone
caught 15, and the pretrained models alone caught 17. Combining them caught 19: every number error
(8 / 8), every negation error (3 / 3) and 8 of 10 meaning errors.

**The V9 figure is a development result.** Overall accuracy on the 1,000 synthetic cases rose from
81.4% (V8) to 97.9% (V9). Those cases were used while building V9, so they show that the new clause
layer works as designed, not how it does on notices it has never seen. On the 100 hardest "edge"
cases V9 is unchanged from V8 (23 / 30 caught, 14 false alarms), because they fall outside what the
clause grammar can read.

## Where it fails

- **Awkward but not wrong English is invisible.** "Carefully slip" for 小心地滑 is not flagged,
  because nothing in it contradicts the Chinese.
- **Long sentences with several dates** can push the contradiction model into false alarms.
- **Similarity alone cannot tell right from wrong.** Correct and broken English both score about
  0.81 to 0.92 against the Chinese, which is why rules and the contradiction model do the deciding.
- **The clause layer only knows 31 patterns.** They were written while looking at the 1,000
  synthetic cases, which explains the jump from 81.4% to 97.9% on that set. Outside those patterns
  V9 behaves like V8. Real notices phrased differently will mostly go to the V8 rules and models.

## Files

| File | What it is |
|---|---|
| `V9_development_comparison.ipynb` | The latest checker. Runs frozen V8 and V9 side by side on 1,000 synthetic cases, with the same models and thresholds. The data is embedded and checksum-verified. |
| `Public_Notice_Check.ipynb` | The full pipeline: data, baseline, models, rules, development and blind-test results, whole-notice check, and a Gradio demo app. Its history goes v2 → v6. |

**Version history.** v2 to v5 were built one on top of the other, each fixing what the previous test
exposed (see the commit messages). After v5, work split into two branches. **V8 → V9** (built from
v5) added evidence rules and then the clause layer. **v6** added a softer "worth a look" level for
contradiction scores between 0.30 and 0.65, after our 60-notice benchmark showed real errors in that
range.

## Run it

1. Click a Colab badge above.
2. *Runtime → Change runtime type → T4 GPU* (faster, but it also runs on CPU).
3. *Runtime → Run all.* The first run downloads the two models (about 2.5 GB).

For the full notebook, upload `notices.csv`, `fresh_test.csv` and `fresh_test_2.csv` with the folder
icon before running, to reproduce the tables above.

## Data

- Development notices (`notices.csv`) were drafted with Claude.
- Blind-test notices are real Hong Kong Government press releases from
  [info.gov.hk](https://www.info.gov.hk/gia/general/). The correct sentences are the government's
  own text; the broken English versions were written for testing.
- The 1,000-case V9 set is synthetic.
- No personal information is used anywhere.

## Credits

- Models: LaBSE (Feng et al.), mDeBERTa-v3 XNLI (Laurer et al., MIT licence)
- Libraries: sentence-transformers, transformers, PyTorch, pandas, NumPy, SciPy, Gradio
- Platform: Google Colab
- Data: Hong Kong Government press releases (info.gov.hk)
- AI tools: Claude (Anthropic) helped with planning, notebook code, test files and the write-up
  draft. Gemini (Google) was also used by the team.
