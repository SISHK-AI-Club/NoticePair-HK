"""Display review items and join recorded bilingual judgments to final results."""
import argparse
import csv
import json
import random
from collections import Counter, defaultdict

from score import ROOT, analyze, write_csv


def records(path):
    with path.open() as file:
        return list(csv.DictReader(file))


def gold_records():
    return {r["case_id"]: r for r in records(ROOT / "v11_blind_1000.csv")}


def abbreviated(words):
    if not words:
        return "—"
    return words


def review_queue(start, end):
    gold = gold_records()
    source = ROOT / "v11_results.jsonl"
    with source.open() as handle:
        predictions = [json.loads(line) for line in handle]
    for p in predictions[start:end]:
        r = gold[p["case_id"]]
        issue = r["expected_status"] == "issue"
        if not (p["flagged"] or issue):
            continue
        outcome = "TP" if p["flagged"] and issue else "FP" if p["flagged"] else "FN"
        print(f"{r['case_id']}/{r['family_id']} {outcome} {r['source_language']} {r['issue_type']}")
        if outcome == "FN":
            signal = p.get("signals", {})
            print(f"  Gold {r['english_evidence']} | {r['chinese_evidence']}")
            print(f"  MT   {signal.get('translation','')}")
        elif outcome == "FP":
            print(f"  Notice {r['english']} | {r['chinese']}")
        else:
            print(f"  Gold {r['english_evidence']} | {r['chinese_evidence']}")
        for i, w in enumerate(p.get("warnings", []),1):
            print(f"  {i} {w['kind']} ({w.get('category','')})")
            if w["kind"] == "equivalence_model":
                edits = w.get("comparison_edits", [])
                print(f"  Focus {w['english_span']} | {w['chinese_span']}")
                print(f"  MT    {w['machine_backtranslation']}")
                print("  Edits " + " ; ".join(f"{abbreviated(edit['english'])} → {abbreviated(edit['machine_backtranslation'])}" for edit in edits))
            else:
                print(f"  {w['why']}")


def tn_sample(cases):
    rng = random.Random(11299)
    groups = defaultdict(list)
    for case in cases:
        if case["outcome"] == "TN":
            groups[(case["domain"], case["difficulty"])].append(case)
    sampled = []
    for group, options in sorted(groups.items()):
        first = rng.choice(options)
        other = [row for row in options if row["source_language"] != first["source_language"] and row["family_id"] != first["family_id"]]
        other = other or [row for row in options if row["family_id"] != first["family_id"]] or options
        second = rng.choice(other)
        sampled.extend((first,second))
    return {r["case_id"]:r for r in sampled}.values()


def read_judgments():
    notes = {}
    for path in sorted(ROOT.glob("judgments_*.tsv")):
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            key, assessment, reason = line.split("\t",2)
            assert key not in notes, key
            notes[key] = dict(assessment=assessment, audit_reason=reason)
    return notes


def finalize():
    cases = records(ROOT / "case_results.csv")
    warnings = records(ROOT / "warning_review.csv")
    notes = read_judgments()

    audited_warnings = [dict(w, **notes.pop(f"{w['case_id']}:{w['warning_number']}")) for w in warnings]
    audited_misses = [dict(r, **notes.pop(r["case_id"])) for r in cases if r["outcome"] == "FN"]
    audited_tn = [dict(r, **notes.pop(r["case_id"])) for r in tn_sample(cases)]
    assert not notes, set(notes)

    valid = {"identified","partial_or_generic","wrong_issue","false_alarm","unresolved_coverage"}
    assert {r["assessment"] for r in audited_warnings} <= valid
    identified = {w["case_id"] for w in audited_warnings if w["outcome"] == "TP" and w["assessment"] == "identified"}
    tp = {r["case_id"] for r in cases if r["outcome"] == "TP"}
    issues = {r["case_id"] for r in cases if r["expected_status"] == "issue"}
    assert identified <= tp <= issues
    coverage = {r["case_id"] for r in cases if r["coverage"] != "complete_notice"}
    summary = {
        "audit_type": "AI bilingual content review by the independent test agent",
        "individual_warnings_reviewed": len(audited_warnings),
        "individual_flags_reviewed": len({w["case_id"] for w in audited_warnings}),
        "false_negatives_reviewed": len(audited_misses),
        "representative_true_negatives_reviewed": len(audited_tn),
        "warning_assessments": dict(Counter(w["assessment"] for w in audited_warnings)),
        "miss_assessments": dict(Counter(w["assessment"] for w in audited_misses)),
        "true_negative_assessments": dict(Counter(w["assessment"] for w in audited_tn)),
        "strict_concrete_issue_identification": {
            "count": len(identified),
            "all_issues_denominator": len(issues),
            "among_all_issues": len(identified)/len(issues),
            "flagged_issues_denominator": len(tp),
            "among_flagged_issues": len(identified)/len(tp) if tp else None,
            "by_difficulty": {tier: dict(
                identified=sum(r["case_id"] in identified and r["difficulty"] == tier for r in cases),
                issues=sum(r["case_id"] in issues and r["difficulty"] == tier for r in cases),
                flagged_issues=sum(r["case_id"] in tp and r["difficulty"] == tier for r in cases))
                for tier in ("routine","difficult","edge")},
        },
        "unresolved_coverage_count": len(coverage),
        "method": "Full bilingual notices were compared against the frozen gold and each warning's actual reported contrast. Quote overlap was insufficient. A faithful, isolated bilingual comparison or faithful machine gloss naming the concrete change could earn credit. Generic alerts, wrong comparisons, and unrelated literal edits could not. Miss review compared the gold with the model's full back-translation. Two true negatives were selected per domain × tier with a fixed seed and source-direction diversity where available.",
    }
    write_csv(ROOT / "warning_audit.csv", audited_warnings)
    write_csv(ROOT / "miss_audit.csv", audited_misses)
    write_csv(ROOT / "true_negative_audit.csv", audited_tn)
    path = ROOT / "metrics.json"
    metrics = json.loads(path.read_text())
    metrics["content_audit"] = summary
    path.write_text(json.dumps(metrics,indent=2,ensure_ascii=False) + "\n")
    print(json.dumps(summary,indent=2,ensure_ascii=False))


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("mode", choices=("queue","tn","finalize"))
    cli.add_argument("--start",type=int,default=0)
    cli.add_argument("--end",type=int)
    args = cli.parse_args()
    if args.mode == "finalize":
        finalize()
    elif args.mode == "tn":
        for row in tn_sample(records(ROOT / "case_results.csv")):
            print(f"{row['case_id']} {row['domain']}/{row['difficulty']}/{row['source_language']} {row['english']} | {row['chinese']}")
    else:
        review_queue(args.start,args.end)

if __name__ == "__main__":
    main()
