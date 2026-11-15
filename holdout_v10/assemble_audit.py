"""Attach the evaluation reviewer's manual judgements to generated evidence tables."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def manual_notes(path):
    notes = {}
    with path.open() as handle:
        for key, assessment, reason in csv.reader(handle, delimiter="\t"):
            assert key not in notes, key
            notes[key] = dict(assessment=assessment, audit_reason=reason)
    return notes


def table(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_table(path, rows):
    with path.open("w", newline="") as handle:
        if rows:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manual_warnings", type=Path)
    parser.add_argument("manual_misses", type=Path)
    args = parser.parse_args()
    warnings = table(ROOT / "warning_review.csv")
    cases = table(ROOT / "case_results.csv")
    warning_notes = manual_notes(args.manual_warnings)
    miss_notes = manual_notes(args.manual_misses)

    audited_warnings = []
    for warning in warnings:
        key = f"{warning['case_id']}:{warning['warning_number']}"
        assert key in warning_notes, key
        audited_warnings.append(dict(warning, **warning_notes.pop(key)))
    assert not warning_notes, warning_notes

    audited_misses = []
    for case in cases:
        if case["outcome"] != "FN":
            continue
        assert case["case_id"] in miss_notes, case["case_id"]
        audited_misses.append(dict(
            case, machine_backtranslation=json.loads(case["signals"]).get("translation", ""),
            **miss_notes.pop(case["case_id"])
        ))
    assert not miss_notes, miss_notes

    identified = {w["case_id"] for w in audited_warnings
                  if w["outcome"] == "TP" and w["assessment"] == "identified"}
    coverage_only = {
        r["case_id"] for r in cases if r["coverage"] != "complete_notice"
    }
    n_issue = sum(r["expected_status"] == "issue" for r in cases)
    tp = sum(r["outcome"] == "TP" for r in cases)
    summary = dict(
        individually_reviewed_warnings=len(audited_warnings),
        individually_reviewed_false_negatives=len(audited_misses),
        warning_assessments=dict(Counter(w["assessment"] for w in audited_warnings)),
        miss_assessments=dict(Counter(c["assessment"] for c in audited_misses)),
        issue_cases_with_concrete_correct_warning=len(identified),
        issue_cases_with_concrete_correct_warning_share=len(identified) / n_issue,
        flagged_issue_cases_with_concrete_correct_warning_share=len(identified) / tp if tp else None,
        unresolved_coverage_cases=len(coverage_only),
        methodology=(
            "The test author manually compared each warning with the two original notices and the "
            "frozen issue evidence. A warning is identified only if its facts or actual pairwise "
            "comparison isolate the concrete changed concept, without inventing or obscuring that "
            "concept. Broad quote overlap is never sufficient. Miss assessments describe whether "
            "the material contrast is preserved in the full machine back-translation."
        ),
    )
    write_table(ROOT / "warning_audit.csv", audited_warnings)
    write_table(ROOT / "miss_audit.csv", audited_misses)
    metrics_path = ROOT / "metrics.json"
    metrics = json.loads(metrics_path.read_text())
    metrics["manual_audit"] = summary
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
