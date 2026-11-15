"""Compare notice-level warnings on the approved benchmark."""
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import median

cases = {
    row["case_id"]: row
    for row in csv.DictReader(
        Path("public_notice_benchmark.csv").open(encoding="utf-8-sig", newline="")
    )
}
for filename in ("public_notice_original_predictions.jsonl", "public_notice_v3_final_predictions.jsonl"):
    results = [json.loads(line) for line in Path(filename).read_text().splitlines()]
    assert len(results) == len({row["case_id"] for row in results}) == 60
    assert {row["case_id"] for row in results} == set(cases)
    assert not any("error" in row for row in results)
    print(filename)
    for split in ("dev", "holdout", "all"):
        selected = [row for row in results if split == "all" or cases[row["case_id"]]["split"] == split]
        counts = Counter()
        for row in selected:
            truth = cases[row["case_id"]]["expected_status"] == "issue"
            predicted = any(finding["why"] for finding in row["rows"])
            counts[("T" if truth == predicted else "F") + ("P" if predicted else "N")] += 1
        accuracy = (counts["TP"] + counts["TN"]) / len(selected)
        print(split, dict(counts), f"accuracy={accuracy:.4%}", f"median_seconds={median(row['seconds'] for row in selected):.3f}")
