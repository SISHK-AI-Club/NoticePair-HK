# V8 structured notice checker

This candidate was developed using the errors in the approved 500-case benchmark. Its results on that dataset are development results, not held-out estimates of real-world accuracy. The frozen V7 notebook and original CSV remain unchanged.

## Run and use

Open `V8_structured_notice_comparison.ipynb` in Google Colab and run its cell on a T4 runtime. It downloads the same pretrained LaBSE and multilingual NLI models used by V7, creates two separate checker namespaces, verifies the embedded CSV and candidate code checksums, and runs both versions on all 500 inputs. Labels are used only after all predictions finish.

After the run, check another notice with:

```python
display(candidate['check_notice'](chinese_text, english_text))
```

The full raw results are written to `v8_500_results.json`. The final cell output includes an expandable compressed export. Download the results before terminating the runtime.

## What changed

`structured_notice.py` independently parses each complete language version into a supported notice structure, subject, and named facts. It supports action order, expiry month, staff exceptions, group booking, duties, contact-update prerequisites, corrections, audience-specific schedules, and simple time notices. Dates are attached to current/superseded roles; times remain attached to their audience; duties remain attached to their actor. Reporting and arriving stay distinct.

`adapter.py` installs this layer in a private copy of the frozen checker. A complete parse on both sides allows fact comparison at whole-notice level, avoiding sentence-alignment warnings for equivalent merged or reordered sentences. The subject remains subject to similarity and contradiction checks. When those isolated-subject checks are uncertain and no explicit fact differs, the original full-notice assessment decides; the revision does not create an alarm solely by removing context. Every explicit mismatch reports the category, both values, and bilingual source evidence.

Unrecognised structures, extra clauses, mixed exception connectors, and unsupported conditions use the frozen V7 checker. Matching one fact alone never establishes that the whole notice is equivalent. The parser rejects action/condition wording inside title fields conservatively.

No pretrained weights were fine-tuned. The inherited similarity and contradiction thresholds remain 0.40 and 0.65. V7 and V8 share the exact same loaded model objects in the comparison.

## Verification and limits

Run `python3 -m unittest discover -s candidate_v8 -p 'test_*.py' -v` from the project folder. The fourteen tests exercise both order directions, month boundaries, passive duty swaps, group modality, correction roles, audience/time swaps, added clauses, unsupported conditions, reporting versus arrival, valid time formats, and preservation of explicit issues when a subject is uncertain. These tests check grammar behaviour; they are not an independent model accuracy benchmark.

The parser is deliberately bounded and was written after inspecting this benchmark. The dataset has only 35 template families; repeated examples and alternate-phrasing choices limit representativeness. Recognition of these families must not be presented as general semantic reasoning. Unknown formats retain V7's limitations. Subject checks are probabilistic and can miss a changed name or scope. New held-out cases should use independently authored wording and unseen document structures, with bilingual human review.

The approved CSV was preserved byte-for-byte. F048 and F075 contain incidental month changes as well as the intended correction-role swaps; the original rationales do not fully describe those mutations.

`source_manifest.json` records the dataset and candidate source checksums. `score_comparison.py` evaluates the exported outputs separately from inference and writes the row-by-row comparison.
