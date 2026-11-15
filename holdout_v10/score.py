"""Score frozen checker predictions against the blind benchmark."""

import argparse
import csv
import hashlib
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def normalized(value):
    value = unicodedata.normalize("NFKC", str(value)).casefold()
    return re.sub(r"[\s\W_]+", "", value)


def evidence_in_notice(evidence, text):
    return bool(normalized(evidence)) and normalized(evidence) in normalized(text)


def overlaps_gold(evidence, gold):
    evidence = normalized(evidence)
    gold = normalized(gold)
    return bool(evidence and gold and (gold in evidence or evidence in gold))


def measure(rows):
    totals = Counter(r["outcome"] for r in rows)
    tp, tn, fp, fn = (totals[k] for k in ("TP", "TN", "FP", "FN"))
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    return {
        "cases": len(rows),
        "accuracy": (tp + tn) / len(rows) if rows else None,
        "precision": precision,
        "recall": recall,
        "f1": 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else None,
        "clean_false_alarm_rate": fp / (fp + tn) if fp + tn else None,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
    }


def bootstrap_family_intervals(by_family, draws=10000, seed=689617):
    # Resample whole families to retain within-family dependence. Stratification
    # keeps the original domain and difficulty composition fixed.
    strata = defaultdict(list)
    for group, metrics in by_family:
        strata[group].append(tuple(metrics[name] for name in ("tp", "tn", "fp", "fn")))
    rng = random.Random(seed)
    metrics = defaultdict(list)
    for _ in range(draws):
        sample = [
            row for families in strata.values()
            for row in rng.choices(families, k=len(families))
        ]
        tp, tn, fp, fn = map(sum, zip(*sample))
        metrics["accuracy"].append((tp + tn) / (tp + tn + fp + fn))
        metrics["recall"].append(tp / (tp + fn))
        metrics["f1"].append(2 * tp / (2 * tp + fp + fn))
        metrics["clean_false_alarm_rate"].append(fp / (fp + tn))
        if tp + fp:
            metrics["precision"].append(tp / (tp + fp))
    return {
        "draws": draws,
        "seed": seed,
        "cluster_count": sum(map(len, strata.values())),
        "method": "95% percentile intervals, resampling whole families within domain × tier.",
        "intervals": {
            metric: [sorted(values)[int(p * (len(values) - 1))] for p in (0.025, 0.975)]
            for metric, values in metrics.items()
        },
    }


def groups(rows, field):
    result = defaultdict(list)
    for row in rows:
        result[row[field]].append(row)
    return {key: measure(group) for key, group in sorted(result.items())}


def extract_warning_items(prediction):
    warnings = prediction.get("warnings", prediction.get("issues", [])) or []
    assert isinstance(warnings, list), prediction
    rows = []
    for warning in warnings:
        if isinstance(warning, str):
            warning = {"message": warning}
        rows.append(warning)
    return rows


def warning_evidence(warning, field):
    evidence = warning.get(
        f"{field}_span", warning.get(f"{field}_evidence", warning.get(f"{field}_text"))
    )
    if not evidence:
        embedded = warning.get("evidence", {})
        if isinstance(embedded, dict):
            evidence = embedded.get(field, embedded.get("en" if field == "english" else "zh"))
    if isinstance(evidence, list):
        return " / ".join(str(item) for item in evidence)
    return str(evidence or "")


def analyze(gold, predictions):
    ids = [p["case_id"] for p in predictions]
    assert len(ids) == len(set(ids)) == len(gold)
    assert set(ids) == set(gold), (set(gold) - set(ids), set(ids) - set(gold))
    results, warning_rows = [], []
    for p in predictions:
        r = gold[p["case_id"]]
        assert isinstance(p["flagged"], bool), (r["case_id"], p)
        assert p["v7_fallback"] is False, r["case_id"]
        raw_status = "issue" if p["flagged"] else "clean"
        outcome = {
            ("issue", "issue"): "TP", ("clean", "clean"): "TN",
            ("clean", "issue"): "FP", ("issue", "clean"): "FN",
        }[r["expected_status"], raw_status]
        warnings = extract_warning_items(p)
        coverage = p["coverage"]
        assert isinstance(coverage, str) and coverage, (r["case_id"], coverage)
        results.append(dict(r, predicted_status=raw_status, outcome=outcome,
                            warning_count=len(warnings), coverage=coverage,
                            decision_path=json.dumps(p["decision_path"], ensure_ascii=False),
                            signals=json.dumps(p.get("signals", {}), ensure_ascii=False),
                            warning_details=json.dumps(warnings, ensure_ascii=False)))
        for idx, warning in enumerate(warnings, 1):
            evidence = {lang: warning_evidence(warning, lang) for lang in ("english", "chinese")}
            span_support = {lang: evidence_in_notice(evidence[lang], r[lang]) for lang in evidence}
            gold_contact = {
                lang: overlaps_gold(evidence[lang], r[f"{lang}_evidence"])
                and span_support[lang] for lang in evidence
            }
            warning_rows.append(dict(
                case_id=r["case_id"], warning_number=idx, outcome=outcome,
                difficulty=r["difficulty"], domain=r["domain"], family_id=r["family_id"],
                source_language=r["source_language"], issue_type=r["issue_type"],
                english=r["english"], chinese=r["chinese"], gold=r["expected_issue_or_clean_rationale"],
                gold_english=r["english_evidence"], gold_chinese=r["chinese_evidence"],
                warning_type=warning["kind"], category=warning["category"],
                message=warning["why"],
                backtranslation=warning.get("machine_backtranslation", ""),
                comparison_edits=json.dumps(warning.get("comparison_edits", []), ensure_ascii=False),
                english_evidence=evidence["english"], chinese_evidence=evidence["chinese"],
                english_evidence_present=span_support["english"],
                chinese_evidence_present=span_support["chinese"],
                english_gold_contact=gold_contact["english"], chinese_gold_contact=gold_contact["chinese"],
                warning_json=json.dumps(warning, ensure_ascii=False),
            ))
    return results, warning_rows


def write_csv(path, rows):
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "frozen_manifest.json").read_text())
    for filename, expected in manifest["output_sha256"].items():
        actual = hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()
        assert actual == expected, (filename, expected, actual)
    with (ROOT / "v10_blind_1000.csv").open() as handle:
        gold = {r["case_id"]: r for r in csv.DictReader(handle)}
    prediction_file = json.loads(args.predictions.read_text())
    metadata = prediction_file["metadata"]
    candidate = json.loads((ROOT.parent / "candidate_v10/frozen_manifest.json").read_text())
    projection = json.loads((ROOT / "input_projection_manifest.json").read_text())
    assert metadata["files"] == candidate["files"]
    for filename, expected in candidate["files"].items():
        actual = hashlib.sha256((ROOT.parent / "candidate_v10" / filename).read_bytes()).hexdigest()
        assert actual == expected, (filename, expected, actual)
    assert candidate["holdout_inputs_sha256"] == projection["original_sha256"]
    assert manifest["output_sha256"]["v10_blind_inputs.csv"] == projection["original_sha256"]
    projected = ROOT / projection["projected"]
    actual_projection = hashlib.sha256(projected.read_bytes()).hexdigest()
    assert metadata["inputs_sha256"] == projection["projected_sha256"] == actual_projection
    assert metadata["predictions"] == len(gold)
    assert metadata["v7_fallback_calls"] == 0
    predictions = prediction_file["results"]
    assert isinstance(predictions, list), "Expected a JSON list, a results object, or JSONL."
    rows, warnings = analyze(gold, predictions)
    issue_rows = [row for row in rows if row["expected_status"] == "issue"]
    metrics = {
        "integrity": {
            "candidate_sha256": candidate["candidate_sha256"],
            "dataset_manifest_sha256": hashlib.sha256((ROOT / "frozen_manifest.json").read_bytes()).hexdigest(),
            "predictions_sha256": hashlib.sha256(args.predictions.read_bytes()).hexdigest(),
            "original_input_sha256": projection["original_sha256"],
            "runner_input_sha256": actual_projection,
            "runtime": metadata,
        },
        "overall": measure(rows),
        "by_difficulty": groups(rows, "difficulty"),
        "by_domain": groups(rows, "domain"),
        "by_source_language": groups(rows, "source_language"),
        "by_family": groups(rows, "family_id"),
        "by_coverage": groups(rows, "coverage"),
        "decision_path_counts": dict(Counter(row["decision_path"] for row in rows)),
        "issue_case_detection_by_type": groups(issue_rows, "issue_type"),
    }
    family = metrics["by_family"]
    group_for = {
        r["family_id"]: (r["domain"], r["difficulty"]) for r in rows
    }
    metrics["family_bootstrap"] = bootstrap_family_intervals(
        (group_for[key], family_metrics) for key, family_metrics in family.items()
    )
    metrics["family_summary"] = {
        "fully_correct": sum(f["accuracy"] == 1 for f in family.values()),
        "at_least_one_issue_detected": sum(f["tp"] > 0 for f in family.values()),
        "all_issues_detected": sum(f["tp"] == 3 for f in family.values()),
        "without_false_alarms": sum(f["fp"] == 0 for f in family.values()),
    }
    metrics["warning_screen"] = {
        "warning_count": len(warnings),
        "warning_triggered_clean_cases": sum(r["expected_status"] == "clean" and r["warning_count"] > 0 for r in rows),
        "warning_triggered_issue_cases": sum(r["expected_status"] == "issue" and r["warning_count"] > 0 for r in rows),
        "by_case_outcome": dict(Counter(w["outcome"] for w in warnings)),
        "by_kind_and_outcome": {
            "|".join(key): count for key, count in sorted(Counter(
                (w["warning_type"], w["outcome"]) for w in warnings
            ).items())
        },
        "with_both_evidence_spans_in_notice": sum(
            w["english_evidence_present"] and w["chinese_evidence_present"] for w in warnings),
        "issue_warnings_touching_both_gold_spans": sum(
            w["outcome"] in {"TP", "FN"} and w["english_gold_contact"] and w["chinese_gold_contact"]
            for w in warnings),
        "span_check_limit": "Exact normalized string checks measure evidence presence and overlap. "
                            "Warning actionability and faithfulness require content review.",
    }
    write_csv(ROOT / "case_results.csv", rows)
    write_csv(ROOT / "warning_review.csv", warnings)
    (ROOT / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in metrics.items() if k != "by_family"}, indent=2))


if __name__ == "__main__":
    main()
