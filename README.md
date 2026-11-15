# NoticePair HK v11

NoticePair HK compares the Traditional Chinese and English versions of a Hong Kong public notice. It flags discrepancies in deadlines, fees, eligibility and other conditions, with excerpts a reviewer can check before publication.

**SISHK AI Club · Veritas AI International High School Hackathon 2026 · AI + Languages**

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SISHK-AI-Club/NoticePair-HK/blob/main/NoticePair_HK_v11.ipynb)

## Judges start here

**Submission file:** [`NoticePair_HK_v11.ipynb`](NoticePair_HK_v11.ipynb). Open it in Colab and run the **Demo app**. Use this README for the project summary, test results, and limitations.

This is a private repository. Open the Colab badge with a GitHub account that has access. If Colab cannot open it directly, download [the notebook](NoticePair_HK_v11.ipynb) from GitHub and upload it in Colab via **File → Upload notebook**.

1. Open the notebook in Colab and select **Runtime → Change runtime type → T4 GPU**.
2. Select **Runtime → Run all**. Setup downloads about 5 GB of pretrained models. The Gradio demo needs no file uploads.
3. Scroll to **Demo app** and open the Gradio interface. Try the second built-in example, where the application deadline and event date are swapped between English and Chinese. Review the flagged passages and explanation.

## How it works

LaBSE matches passages, mDeBERTa estimates whether they agree, and NLLB-200 provides a translation cross-check. Rules compare dates, amounts and other explicit facts. A small logistic regression model combines these signals, and a separate check flags missing conditions when both model views support the finding. The notebook includes the frozen checker code and verifies its checksums before loading it.

## Evaluation

| Test set | Accuracy | Errors caught | False alarms |
| --- | ---: | ---: | ---: |
| 38 pairs from three new Hong Kong Government releases | 78.9% | 13 of 18 | 3 of 20 |
| 1,000 synthetic pairs from topics excluded from v11 training | 90.8% | 211 of 300 | 3 of 700 |
| 47 pairs from four earlier Hong Kong Government releases | 80.9% | 15 of 21 | 3 of 26 |

The newest real-notice set was built after v11 was frozen. The team had seen the synthetic topics during v9 development, and the earlier releases were already available. The real-notice sample is small, and some synthetic topics match the checker’s fact rules closely.

The checker can miss awkward wording that preserves the same meaning. The demo checks long notices paragraph by paragraph and normalises spaced thousands such as `6 300`. The scores above predate that number normalisation.

## Data and history

See the [evaluation datasets](https://github.com/SISHK-AI-Club/NoticePair-HK/tree/v11/data), [v11 archive](https://github.com/SISHK-AI-Club/NoticePair-HK/tree/v11), and [version tags](https://github.com/SISHK-AI-Club/NoticePair-HK/tags). The notebook’s optional benchmark cell accepts an [inputs-only CSV](https://github.com/SISHK-AI-Club/NoticePair-HK/blob/v11/holdout_v11/v11_blind_inputs.csv).

Models by Feng et al. (LaBSE), Laurer et al. (mDeBERTa, MIT), and Meta (NLLB-200 distilled 600M, CC BY-NC 4.0). The real-notice tests use Hong Kong Government press releases, with links in the evaluation datasets.
