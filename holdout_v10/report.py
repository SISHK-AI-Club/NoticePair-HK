"""Render a report from verified metrics and the independent evaluator's findings."""

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def ratio(value):
    return f"{value:.1%}" if value is not None else "—"


def row(label, m):
    return (f"| {label} | {m['cases']} | {m['tp']} | {m['tn']} | "
            f"{m['fp']} | {m['fn']} | {ratio(m['accuracy'])} | "
            f"{ratio(m['precision'])} | {ratio(m['recall'])} | "
            f"{ratio(m['f1'])} | {ratio(m['clean_false_alarm_rate'])} |")


def main():
    m = json.loads((ROOT / "metrics.json").read_text())
    a = m["manual_audit"]
    proof = m["integrity"]
    runtime = proof["runtime"]
    elapsed = datetime.fromisoformat(runtime["completed"]) - datetime.fromisoformat(runtime["started"])
    text = [
        "# V10 independent blind holdout evaluation",
        "",
        f"The frozen V10 checker scored **{ratio(m['overall']['accuracy'])} accuracy** on 1,000 "
        f"fresh test pairs. It flagged **{m['overall']['tp']} of 300 notices with a material "
        f"translation discrepancy** and **{m['overall']['fp']} of 700 clean notices**. "
        f"Warnings identified the actual gold discrepancy in **{a['issue_cases_with_concrete_correct_warning']} "
        f"of 300 issue cases** under review by the Sol testing agent.",
        "",
        "**Scope.** These are short synthetic notices, with a maximum of 162 English "
        "characters and 49 Chinese characters, or 34 and 51 LaBSE tokens respectively. "
        "Difficulty tiers were assigned by the author. "
        "The benchmark provides no performance estimate for full multi-paragraph official emails.",
        "",
        "## Notice-level detection",
        "",
        "An issue is the positive class. A flag is the checker’s request for review. Recall is the "
        "share of issue notices flagged, and the clean false alarm rate is the share of clean "
        "notices flagged. If a case had several warnings, it still contributes once to this table. "
        "An always-clean baseline would attain 70% accuracy and zero recall on this test.",
        "",
        "| Split | Cases | True positives | True negatives | False alarms | Misses | Accuracy | Precision | Recall | F1 | Clean false alarm rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        row("**Overall**", m["overall"]),
    ]
    for tier in ("routine", "difficult", "edge"):
        text.append(row(tier.capitalize(), m["by_difficulty"][tier]))
    for domain, label in [("school", "School"), ("government", "Government"),
                          ("public_email", "Public email"), ("instructions", "Instructions")]:
        text.append(row(label, m["by_domain"][domain]))
    for lang, label in [("en", "English source"), ("zh", "Traditional Chinese source")]:
        text.append(row(label, m["by_source_language"][lang]))
    boot = m["family_bootstrap"]
    family = m["family_summary"]
    text.extend([
        "",
        f"Across 100 scenario families, {family['fully_correct']} had all ten cases classified "
        f"correctly and {family['all_issues_detected']} had all three issues detected. "
        f"{family['at_least_one_issue_detected']} had at least one issue detected, and "
        f"{family['without_false_alarms']} had zero false alarms.",
        "",
        f"95% family-cluster bootstrap intervals used {boot['draws']:,} resamples of whole families "
        "within each domain and difficulty stratum.",
        "",
        "| Metric | Interval |",
        "|---|---:|",
    ])
    for key, values in boot["intervals"].items():
        label = key.replace("_", " ").capitalize()
        text.append(f"| {label} | {ratio(values[0])}–{ratio(values[1])} |")
    text.extend([
        "",
        "## Warning quality and error audit",
        "",
        f"The Sol testing agent manually reviewed all {a['individually_reviewed_warnings']} warnings and "
        f"all {a['individually_reviewed_false_negatives']} missed issues. "
        "A warning earned identification credit only when its explicit facts or machine "
        "comparison concretely isolated the material change in the original texts. A generic "
        "review prompt or a quotation spanning the correct words was insufficient. "
        f"Concrete warnings covered {ratio(a['flagged_issue_cases_with_concrete_correct_warning_share'])} "
        f"of flagged issue cases and {ratio(a['issue_cases_with_concrete_correct_warning_share'])} "
        f"of all issue cases. Unresolved coverage affected {a['unresolved_coverage_cases']} cases.",
        "",
        "| Warning assessment | Count |",
        "|---|---:|",
    ])
    descriptions = {
        "identified": "Isolates the discrepancy",
        "partial": "Points towards the discrepancy with limited or obscured detail",
        "generic": "Generic guidance without a concrete translated contrast",
        "wrong_issue": "Gives a different or unsupported explanation on an issue case",
        "false_backtranslation": "Clean pair with a machine back-translation error",
        "false_context": "Clean pair with a meaning-equivalent comparison flagged",
        "false_explicit": "Clean pair with an unsupported extracted factual difference",
        "unresolved": "Coverage warning requiring manual review",
        "label_concern": "Clean pair with a warning that exposes a reference-label concern",
    }
    for key, count in sorted(a["warning_assessments"].items()):
        text.append(f"| {descriptions[key]} | {count} |")
    text.extend([
        "",
        "For missed issues, the evaluator checked whether the machine back-translation "
        "still exposed the material contrast. This audit describes what survived translation. "
        "It does not establish what a model internally relied on.",
        "",
        "| Miss audit assessment | Count |",
        "|---|---:|",
    ])
    for key, count in sorted(a["miss_assessments"].items()):
        text.append(f"| {key.capitalize()} | {count} |")
    text.extend([
        "",
        "### Findings from the case review",
        "",
        "- The checker missed all 29 exception changes and all eight omissions. It detected "
        "10 of 49 scope changes and three of 20 condition changes. It flagged all 11 quantity "
        "changes, although some machine comparisons gave the wrong unit or measured item.",
        "- In 146 of 199 misses, the full back-translation preserved the material contrast. "
        "For example, T0965 clearly distinguishes permission to use a photo in an event summary "
        "from using it on a paid billboard, and T0179 distinguishes a subscriber requesting a "
        "particular update from blocking that category. Neither was flagged.",
        "- T0652 omits a supervisor’s seal check before a machine cycle can restart. "
        "Full-notice contradiction scores in both comparison paths remained below 0.001. "
        "T0068 changes the meal waiver from the first substitute meal to each meal. "
        "The whole-notice contradiction scores were high, but the aligned coverage passage’s "
        "back-translation-based scores failed the frozen agreement requirement.",
        "- T0429’s explicit warning correctly shows 21 May versus 12 May. T0799 flagged 30 "
        "versus 70 millilitres, but the machine comparison assigned the corrected volume to "
        "coffee powder instead of water. T0879 flagged a change, but its back-translation "
        "did not show that a caliper’s jaws should be opened instead of closed.",
        "- Two clean-pair false alarms came from nonmaterial wording about sowing seeds "
        "(T0462 and T0975). The other two arose when the machine changed closing caliper jaws "
        "to adding a number of claws (T0039) and the Resume button label to Restore (T0565). "
        "All four retained their frozen clean labels.",
    ])
    issue_types = m["issue_case_detection_by_type"]
    important = Counter({kind: data["fn"] for kind, data in issue_types.items()})
    text.extend([
        "",
        "## Largest miss groups",
        "",
        "| Gold issue type | Issue cases | Detected | Missed | Recall |",
        "|---|---:|---:|---:|---:|",
    ])
    for key, _ in important.most_common(12):
        d = issue_types[key]
        text.append(f"| {key.replace('_',' ')} | {d['cases']} | {d['tp']} | {d['fn']} | {ratio(d['recall'])} |")
    text.extend([
        "",
        "## Test design and run verification",
        "",
        "- GPT-6.1 Sol at medium reasoning independently authored and ran the held-out test. "
        "The frozen benchmark comprises 100 scenario families with three separately authored "
        "bilingual frames per family, plus controlled semantic alternatives. There are 1,000 "
        "unique paired notices. The test compares formal English with Hong Kong written Traditional Chinese.",
        "- The benchmark contains 600 routine, 300 difficult and 100 edge cases. Each family "
        "contains seven clean pairs and three issue pairs. School and government each contribute "
        "300 cases. Public email and instructions each contribute 200. English is authoritative "
        "in 600 cases and Traditional Chinese in 400.",
        "- The generator found zero exact notice-text matches, in either language, against the "
        "original 500-case benchmark, the V8 holdout and the V9 holdout. This check does not "
        "establish semantic non-overlap with every previous example.",
        "- The labels and issue evidence were frozen before the first prediction. The candidate's "
        "runner accepts three columns. The initial attempt stopped at schema validation, before "
        "prediction, because the original held-out input file also includes source-language "
        "metadata. An input projection preserves parsed ID and bilingual text bytes and row "
        "order for all 1,000 cases. Both input hashes are recorded below. Source language "
        "identifies the authoritative version for the evaluator only.",
        f"- All 1,000 unique cases were scored. The candidate source hashes still matched the freeze "
        f"after inference. The run used {runtime['device'].upper()} for {elapsed.seconds // 60} minutes "
        f"and {elapsed.seconds % 60} seconds and called the V7 fallback zero times.",
        "- The cases and gold labels are synthetic and agent-authored. The same test agent reviewed "
        "the warnings and missed cases. There was no independent human validation. Short notices "
        "and related alternatives within a family do not measure performance on naturally "
        "distributed public notices or on documents near runtime context limits.",
        "",
        "| Artifact | SHA-256 |",
        "|---|---|",
        f"| Candidate | `{proof['candidate_sha256']}` |",
        f"| Dataset manifest | `{proof['dataset_manifest_sha256']}` |",
        f"| Original inputs | `{proof['original_input_sha256']}` |",
        f"| Actual runner inputs | `{proof['runner_input_sha256']}` |",
        f"| Predictions | `{proof['predictions_sha256']}` |",
        "",
        "## Evidence files",
        "",
        "- [Full benchmark and annotations](review_all_1000.md)",
        "- [All case-level outcomes and warnings](case_results.csv)",
        "- [Manual warning decisions](warning_audit.csv) and [manual review of missed issues](miss_audit.csv)",
        "- [Machine-readable metrics](metrics.json), [dataset manifest](frozen_manifest.json) and [input projection manifest](input_projection_manifest.json)",
        "- [Raw predictions](v10_results.json), [inference log](run.log) and [initial input-schema rejection](input_schema_retry.log)",
        "",
    ])
    (ROOT / "report.md").write_text("\n".join(text))


if __name__ == "__main__":
    main()
