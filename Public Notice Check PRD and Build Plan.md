# Public Notice Check

**Veritas AI + Languages, §4.4.4 · Weekend prototype · 14 November 2026**

## 1. Product requirements document

### Problem and user

A programme coordinator at a Hong Kong community centre, charity or school often needs to send a notice in English and Traditional Chinese. They may use Google Translate to draft one version, then make a last-minute edit to the other. Before publishing, they need to know whether both versions tell families the same thing about when to apply, who qualifies and what they must do.

**Product promise.** Paste the two drafts. See which instructions disagree or need review, and jump straight to the evidence. The coordinator or bilingual reviewer checks the findings, edits the draft in their usual editor, and decides when to publish.

### MVP workflow and requirements

| Step | Requirement |
|---|---|
| 1. Draft | The coordinator writes one version and prepares the second in Google Translate or through their usual translation process. Google Translate is outside the app. |
| 2. Paste | Two plain-text fields, labelled English and Traditional Chinese, each with a live counter and a **6,000 Unicode character** starting limit. User identifies the source draft. Reject empty or over-limit input clearly and preserve both drafts for editing. |
| 3. Check | Local inference matches related passages and checks **application deadlines, eligibility and required actions**. Retain offsets to the exact original text. |
| 4. Review | A discrepancy card shows the category, both excerpts and why a reader might act differently. An unmatched relevant passage shows the available excerpt and **Needs review**. For a missing counterpart, say that the tool could not match one. |
| 5. Recheck | Keep both editable drafts visible. After an edit, mark the prior results as stale until the next check. Show checked and unresolved coverage. Use **No discrepancies found in checked passages** when appropriate. |
| 6. Publish | The reviewer makes the release decision in their normal workflow. |

The first release is a single local Python/Gradio page with the custom checkpoint and tokenizer bundled locally. PDF import, OCR, automatic translation, extra languages, accounts and publishing integrations are deferred. Use public notices and team-authored examples for the demo and evaluation.

### Acceptance criteria

- A complete notice with a changed application deadline highlights the deadline on both sides, even if the event date occurs nearby.
- A changed eligibility or required-action clause can be flagged when every number stays identical. A missing or unclear counterpart produces a review item.
- A verified equivalent pair with different date formats or reordered wording can be checked without introducing a false flag. Keep failed examples in the results.
- A relevant issue near the end of a near-limit input is processed, or a clearly identified passage is marked unresolved. Check real tokenizer limits per model call and never silently truncate.
- After model files are downloaded, the full demo runs without API calls. Test a cold start and a repeat run on the demo laptop. Time both a typical notice and a near-limit notice before confirming the cap.
- A person can complete paste → check → inspect the evidence → fix and recheck. Record where they hesitate and whether the workflow helps them spot a meaningful issue.

**Accuracy target.** Aim for at least 90% issue precision on development notices, then optimise recall at that threshold. This is a tuning target. Report counts and held-out results as measured.

## 2. Build plan

### Data and models

| Use | Exact choice |
|---|---|
| In-domain source text | Hong Kong government press release search, using the matching English and Traditional Chinese versions of LCSD recreation, workshop and cultural enrolment notices. Save source URLs and programme-family IDs. [Search resource](https://data.gov.hk/en-data/dataset/hk-dpo-datagovhk1-pressrelease-search/resource/5a2bc3d5-5487-4c09-959a-6d38c314d426) · [Example notice](https://www.info.gov.hk/gia/general/202312/01/P2023120100573p.htm) |
| Bilingual alignment warm-up | HK-LegiCoST **data/train.parquet**, columns **transcript** and **translation**. Sample up to **10,000** filtered, deduplicated pairs with a fixed seed. Check a sample of alignments and negatives. This is formal bilingual text with noisy alignment. [Data files](https://huggingface.co/datasets/Borrison/hk-legicost/tree/main/data) |
| Separate external benchmark | WMT22 HW-TSC date/time and affirmation/negation subsets, **198 documented cases**. Check eligibility for supported patterns, report the number scored and treat ties as misses on the ranking test. [TSV and benchmark description](https://github.com/HwTsc/Challenge-Set-for-MT-Metrics) |

Pangeanic remains an option for a written Cantonese extension. The first release targets formal Traditional Chinese. HK-LegiCoST supplies alignment examples. The reviewed post-translation drafts and edited notices supply evidence about discrepancy detection.

### Phase 1 — Scratch-trained architecture

Train a custom SentencePiece BPE tokenizer on both languages from the training partitions of HK-LegiCoST and the government notices. Start with an 8K shared vocabulary and byte fallback. Check token coverage and truncation by language. Train a randomly initialised PyTorch cross-encoder with four Transformer layers, 256 hidden units, eight attention heads and a 1,024-wide feed-forward layer. Pass [CLS] English [SEP] Chinese [SEP] through the encoder with positional and language embeddings and a padding mask. Use the final CLS state to predict 0 entailment, 1 contradiction or 2 neutral. Start with 256 tokens per clause pair. The UI cap remains 6,000 characters per draft. Split long passages and surface anything unresolved. This configuration is roughly 5.3M parameters. Six layers, width 384 and a 16K vocabulary would be around 17M. Verify the actual count in code.

### Phase 2 — Warm-up and task data

- Warm up the encoder for 1–2 epochs on 10,000 sampled HK-LegiCoST pairs using binary alignment. Use aligned clauses as positives and similar but unrelated clauses as negatives. Keep the alignment head for ranking matches shortlisted by heading, role and neighbouring context.
- Extract 500–1,000 parallel clauses from training-only Hong Kong government notices. Build about 1,000 task examples from reviewed equivalent clauses, edits such as changed age cutoffs, and unrelated or partially overlapping clauses. Use DeepSeek V4 Pro to draft additional meaning-changing edits that preserve the numbers. Review labels, edit both languages and retain provenance. Treat a weakened obligation as an actionable notice discrepancy even if formal entailment treats it as neutral in one direction.
- Split by programme family before training the tokenizer or generating variants. Keep all variants of a notice in the same partition.

### Phase 3 — Distil DeepSeek V4 Pro

Use the API in a separate training utility on public or team-authored examples. Cache the model version, prompt version, predicted class and a short evidence note. Request a probability for each of the three classes and validate the vector. A prompted probability vector is an estimate, and a single confidence score leaves two class probabilities unspecified. Train a hard-label cross-entropy baseline, with teacher-only labels recorded as pseudo-labels. Compare it with cross-entropy plus weighted KL divergence on examples with valid teacher distributions. Review disagreements with known labels. Keep explanation generation optional. The app displays source excerpts and templated explanations. [DeepSeek API documentation](https://api-docs.deepseek.com/api/create-chat-completion/)

### Phase 4 — Train and package

Use PyTorch and SentencePiece with a separate API client for training. Start with AdamW, batch 16 and learning rate 1e-4, with 5e-5 as a development alternative. Time a short Colab run, then train up to 10–15 epochs with early stopping. Record runtime, GPU and actual checkpoint size. A 20M-parameter checkpoint contains about 80 MB of FP32 weights. Package the chosen .pth checkpoint, configuration and tokenizer with Gradio and run the demo offline. Include the dates-and-numbers rules and route uncertain clause matches to manual review. Use the scratch hard-label checkpoint if distillation is unavailable or underperforms.

### Phase 5 — Evaluation and delivery

### Accuracy evaluation

- Target **30 independent notice families**, 10 development and 20 held out. Group all versions from the same programme before splitting. If time limits collection, publish the actual counts.
- For each family, prepare a reviewed clean pair. For a subset, use the real original notice and a fresh Google Translate draft made from the public source. A bilingual reader labels genuine changes before seeing checker output. Keep actual machine-translation errors distinct from controlled edits. Add one-sided late edits, same-number role swaps, omitted exceptions and harmless paraphrases. Keep all variants in their family's split.
- Record issue category, source spans and which action changes. For genuinely ambiguous pairs, record that review is expected. Freeze test labels and thresholds before scoring. Keep usability examples separate from the locked accuracy test.
- Compare **uniform random guessing** (33⅓% expected three-class accuracy), **date/number rules**, the **scratch hard-label model**, and the **distilled student**. Score DeepSeek independently against the same human-labelled holdout as a teacher reference. Report contradiction precision, recall and F1 alongside the notice-level results. Report issue precision and recall with raw counts, false alerts on clean notices, manual-review rate and top-three alignment recall. A generic review item receives no credit as a correctly identified discrepancy. Show separate counts for fresh machine translations and seeded changes. Report one false positive and one missed issue if observed.

## 3. Real-person test before submitting

**Recruit now.** Ask one actual bilingual person who writes or approves notices. First choice is a community programme coordinator. A school activities coordinator or club adviser who regularly sends bilingual registration notices is a useful fallback. A bilingual teammate can do the dry run. Describe their feedback as internal if an external reviewer is unavailable.

**Book 20 minutes for Sunday, ideally by 16:00 HKT.** Ask the person to describe a recent notice and their actual process. With their agreement, use public or simulated drafts, avoid recording personal information, and ask before quoting them.

| Time | What to do |
|---|---|
| 4 min | Ask who writes the source, how the second version is prepared, what gets edited late, and who gives the go-ahead. Ask how they review a notice today. |
| 5 min | Give them a public or mock bilingual draft with one labelled discrepancy. Ask them to review it in their usual way. Time the task and record whether they found the issue. Keep the answer key out of view. |
| 5 min | Give them a comparable, different notice with the checker. Ask them to check it, explain the flag and say what they would change. Measure time, whether they caught the issue, and any false alert they investigated. If a second reviewer is available, reverse the task order and swap the notices. |
| 6 min | Show a verified clean case and ask what they would do with a **Needs review** result. Ask where this could fit before publishing and what would make them skip it. |

**Record:** participant role, scenario, task order, seconds, issues found, false flags investigated, and one observed friction point. Fix the highest-impact usability issue before recording. If it changes scoring behaviour, disclose the change and keep previously seen test cases out of any new tuning claim. A one-person comparison is a usability observation, with effects from task difficulty and order. Report what they did and said, with any adoption claim left open.

## 4. Weekend milestones and submission

| When, HKT | Outcome |
|---|---|
| Saturday, first two build hours | Confirm PRD scope. Test six reviewed bilingual clauses. Get one real pair through paste → flag. Invite the reviewer and assign model, data and demo ownership. |
| Saturday evening | Rules baseline and scratch encoder smoke test run on development notices. The reviewer UI displays evidence and uncertainty. Lock the notice-family split. |
| Sunday morning | Run warm-up, hard-label training and distillation as time permits. Decide what ships using development data. Freeze scoring settings and run the held-out evaluation. |
| Sunday by 16:00 | Run the real-person test. Address the highest-impact workflow issue and recheck the demo. |
| Sunday evening | Submit the reproducible code link, one-page write-up, credits and two-minute video. Check links in an incognito window. Official deadline is **Monday 16 November, 12:59 p.m. HKT**. [Veritas submission instructions](https://highschoolhackathon.org/briefs) |

### Two-minute judge demo

- **0:00–0:20.** A coordinator prepares a bilingual enrolment notice. Show the source and a draft prepared in Google Translate. Use a clearly labelled controlled edit if the generated translation contains no relevant error.
- **0:20–1:05.** Paste the two versions. Show a last-minute source change that leaves the other language stale. Then show a more difficult case where the numbers match and the eligibility or obligation changes. Read the two highlighted excerpts, fix the draft and recheck.
- **1:05–1:45.** Show the held-out results against the baseline, the measured difference distillation made, and one observation from the real-person test. Use measured values.
- **1:45–2:00.** Show one uncertainty or miss and explain how the reviewer handles it. For the live final, load the weights before presenting and let a judge change a clause. [Veritas judging rubric](https://highschoolhackathon.org/judges)

The model choice, input cap and projected sample size are proposed. Accuracy, runtime and adoption are unmeasured until the team runs these checks.
