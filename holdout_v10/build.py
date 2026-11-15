"""Build and verify the benchmark from the bilingual frame files."""
import csv
import hashlib
import io
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOMAINS = ["school", "government", "public_email", "instructions"]
TIERS = ["routine", "difficult", "edge"]
FIELDS = [
    "case_id", "family_id", "split", "domain", "topic", "difficulty",
    "source_language", "english", "chinese", "expected_status",
    "english_evidence", "chinese_evidence", "expected_issue_or_clean_rationale",
    "severity", "issue_type", "frame_id",
]
INPUT_FIELDS = ["case_id", "source_language", "english", "chinese"]

# English-source counts by domain, difficulty and status. Other cases are
# Chinese-source, with clean and issue counts fixed at seven and three per family.
EN_CLEAN = [[76, 38, 13], [76, 38, 13], [50, 26, 8], [50, 26, 8]]
EN_ISSUE = [[32, 16, 5], [32, 16, 5], [22, 10, 4], [22, 10, 4]]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_families():
    for domain in DOMAINS:
        for line in (ROOT / f"{domain}.txt").read_text().splitlines():
            if not line.strip():
                continue
            if line.startswith("@"):
                tier, topic = line[1:].split("|")
                frames = []
                yield domain, tier, topic, frames
            else:
                kind, en, zh, *values = line.split("|")
                assert en.count("{}") == zh.count("{}") == 1, line
                values = [tuple(v.split("~")) for v in values]
                assert all(len(v) == 2 for v in values), line
                assert len(values) in (3, 4), line
                assert len(set(values)) == len(values), line
                frames.append((kind, en, zh, values))


def render(frame, value):
    # The empty substitution can be used for controlled omission or addition.
    rendered = frame.replace("{}", value).replace(r"\n", "\n")
    return rendered.replace(" .", ".").replace(" ,", ",").strip()


def source_languages(domain, tier, status, n, rng):
    d, t = DOMAINS.index(domain), TIERS.index(tier)
    en_count = (EN_CLEAN if status == "clean" else EN_ISSUE)[d][t]
    languages = ["en"] * en_count + ["zh"] * (n - en_count)
    rng.shuffle(languages)
    return iter(languages)


def create_rows():
    rng = random.Random(914026)
    families = list(read_families())
    assert len(families) == 100
    for domain in DOMAINS:
        for tier in TIERS:
            n = sum((d, t) == (domain, tier) for d, t, _, _ in families)
            expected = {"school": (18, 9, 3), "government": (18, 9, 3),
                        "public_email": (12, 6, 2), "instructions": (12, 6, 2)}
            assert n == expected[domain][TIERS.index(tier)], (domain, tier, n)
    sources = {}
    for domain, tier in [(d, t) for d in DOMAINS for t in TIERS]:
        n = sum((d, t) == (domain, tier) for d, t, _, _ in families)
        for status, per_family in [("clean", 7), ("issue", 3)]:
            sources[domain, tier, status] = source_languages(
                domain, tier, status, n * per_family, rng
            )
    rows = []
    for idx, (domain, tier, topic, frames) in enumerate(families, 1):
        assert [len(f[-1]) for f in frames] == [4, 3, 3], topic
        for frame_no, (kind, en_frame, zh_frame, values) in enumerate(frames, 1):
            clean = values[:-1]
            issue = values[-1]
            for match in [*clean, None]:
                status = "clean" if match is not None else "issue"
                language = next(sources[domain, tier, status])
                if match is not None:
                    en_ev, zh_ev = match
                    rationale = (
                        f"Both texts communicate the same {kind.replace('_', ' ')}: "
                        f"EN ‹{en_ev.strip() or 'no clause'}› corresponds to "
                        f"ZH ‹{zh_ev or '無此條款'}› within the same notice."
                    )
                else:
                    base = rng.choice(clean)
                    if ("", "") in clean:
                        base = ("", "")
                    if language == "en":
                        en_ev, zh_ev = base[0], issue[1]
                        source, translation = base, issue
                    else:
                        en_ev, zh_ev = issue[0], base[1]
                        source, translation = base, issue
                    i = 0 if language == "en" else 1
                    j = 1 - i
                    source_ev = source[i].strip()
                    changed_ev = translation[j].strip()
                    if not changed_ev:
                        rationale = f"The translation omits this source detail: ‹{source_ev}›."
                        kind_for_row = "omission"
                    elif not source_ev:
                        rationale = f"The translation adds a detail absent from the source: ‹{changed_ev}›."
                        kind_for_row = "addition"
                    else:
                        rationale = (
                            f"The source specifies ‹{source_ev}›. The translation gives "
                            f"‹{changed_ev}›, which changes the {kind.replace('_', ' ')}."
                        )
                        kind_for_row = kind
                en = render(en_frame, en_ev)
                zh = render(zh_frame, zh_ev)
                rows.append(dict(
                    family_id=f"vf{idx:03d}", split="holdout", domain=domain, topic=topic,
                    difficulty=tier, source_language=language, english=en, chinese=zh,
                    expected_status=status,
                    english_evidence=en_ev.strip() or en,
                    chinese_evidence=zh_ev.strip() or zh,
                    expected_issue_or_clean_rationale=rationale,
                    severity="material" if status == "issue" else "none",
                    issue_type=kind_for_row if status == "issue" else "",
                    frame_id=f"vf{idx:03d}-{frame_no}",
                ))
    rng.shuffle(rows)
    for i, row in enumerate(rows, 1):
        row["case_id"] = f"T{i:04d}"
    verify(rows)
    return rows


def verify(rows):
    assert len(rows) == len({(r["english"], r["chinese"]) for r in rows}) == 1000
    assert len({r["frame_id"] for r in rows}) == 300
    assert Counter(r["difficulty"] for r in rows) == {
        "routine": 600, "difficult": 300, "edge": 100}
    assert Counter(r["source_language"] for r in rows) == {"en": 600, "zh": 400}
    assert Counter(r["expected_status"] for r in rows) == {"clean": 700, "issue": 300}
    assert Counter(r["domain"] for r in rows) == {
        "school": 300, "government": 300, "public_email": 200, "instructions": 200}
    assert len(Counter(r["topic"] for r in rows)) == 100
    family_status_totals = Counter((r["family_id"], r["expected_status"]) for r in rows)
    assert len(family_status_totals) == 200
    assert all(n == {"clean": 7, "issue": 3}[status]
               for (_, status), n in family_status_totals.items())
    assert all(r["english"] and r["chinese"] and r["expected_issue_or_clean_rationale"] for r in rows)
    for tier, count in zip(TIERS, [600, 300, 100]):
        assert sum(r["difficulty"] == tier and r["expected_status"] == "issue"
                   for r in rows) == count * 3 // 10
    for row in rows:
        assert row["english_evidence"] in row["english"], row
        assert row["chinese_evidence"] in row["chinese"], row
        assert "{}" not in row["english"] and "{}" not in row["chinese"], row


def csv_bytes(rows, fields):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


def review(rows):
    lines = ["# V10 blind holdout. Full reference review", "",
             "Cases are grouped by domain, tier and scenario family. The source label",
             "marks the authoritative language. Evidence is copied from both rendered",
             "texts. An omission cites the rendered text on the side without the clause.", ""]
    groups = defaultdict(list)
    for row in rows:
        groups[row["family_id"]].append(row)
    for family_id, group in sorted(groups.items()):
        meta = group[0]
        lines.extend([f"## {meta['topic']} ({family_id})", "",
                      f"{meta['domain']} · {meta['difficulty']}", ""])
        for row in sorted(group, key=lambda r: (r["frame_id"], r["case_id"])):
            lines += [
                f"### {row['case_id']} · {row['expected_status']} · source {row['source_language'].upper()}",
                "", f"**EN** {row['english']}", "", f"**繁體中文** {row['chinese']}", "",
                f"**Evidence** ‹{row['english_evidence']}› / ‹{row['chinese_evidence']}›", "",
                row["expected_issue_or_clean_rationale"], "",
            ]
    return "\n".join(lines).encode()


def prior_matches(rows):
    prior_files = [
        ROOT.parent / "benchmark_500/formal_bilingual_benchmark_500.csv",
        ROOT.parent / "holdout_1000/v8_holdout_1000.csv",
        ROOT.parent / "holdout_v9/v9_unseen_1000.csv",
    ]
    result = {}
    for path in prior_files:
        with path.open(encoding="utf-8-sig", newline="") as f:
            old = list(csv.DictReader(f))
        checks = {}
        for columns in [("english",), ("chinese",), ("english", "chinese")]:
            seen = {tuple(r[c].strip() for c in columns) for r in old}
            checks["+".join(columns)] = sum(
                tuple(r[c].strip() for c in columns) in seen for r in rows
            )
        assert not any(checks.values()), (path, checks)
        result[path.name] = checks
    return result


def main():
    rows = create_rows()
    files = {
        "v10_blind_1000.csv": csv_bytes(rows, FIELDS),
        "v10_blind_inputs.csv": csv_bytes(rows, INPUT_FIELDS),
        "review_all_1000.md": review(rows),
    }
    for filename, data in files.items():
        (ROOT / filename).write_bytes(data)
    manifest = {
        "version": 1,
        "output_sha256": {name: sha(data) for name, data in files.items()},
        "reproduction_sha256": {
            path.name: sha(path.read_bytes())
            for path in [Path(__file__), *(ROOT / f"{domain}.txt" for domain in DOMAINS)]
        },
        "source_language_notice": "The source language is authoritative. The inputs file excludes gold fields.",
        "scenario_families": 100,
        "authored_frames": 300,
        "case_count": len(rows),
        "unique_english_texts": len({r["english"] for r in rows}),
        "unique_chinese_texts": len({r["chinese"] for r in rows}),
        "split_counts": {
            "|".join(k): count for k, count in sorted(Counter(
                (r["domain"], r["difficulty"], r["source_language"], r["expected_status"])
                for r in rows
            ).items())
        },
        "issue_types": dict(sorted(Counter(
            r["issue_type"] for r in rows if r["issue_type"]
        ).items())),
        "exact_overlap_with_prior": prior_matches(rows),
        "design_limits": [
            "Three authored linguistic frames per family with controlled alternatives. "
            "An issue pair shares one side with a clean pair in the same frame.",
            "Cases within a family are related. Family-level breakdowns are necessary for interpretation.",
            "One bilingual author produced the reference annotations and deterministic checks. "
            "No independent human annotation or natural-corpus frequency calibration.",
        ],
    }
    (ROOT / "frozen_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
