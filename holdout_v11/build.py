"""Produce, validate and freeze the bilingual benchmark and blind projection."""
import csv
import re
import hashlib
import io
import itertools
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent
DOMAINS = {"school": (18,9,3), "government": (18,9,3), "public_email": (12,6,2), "instructions": (12,6,2)}
TIERS = ("routine", "difficult", "edge")
FIELDS = ("case_id","family_id","split","domain","topic","difficulty","source_language","english","chinese","expected_status","english_evidence","chinese_evidence","expected_issue_or_clean_rationale","severity","issue_type","frame_id")
INPUT_FIELDS = ("case_id", "english", "chinese")
EN_CLEAN = ((76,38,13),(76,38,13),(50,26,8),(50,26,8))
EN_ISSUE = ((32,16,5),(32,16,5),(22,10,4),(22,10,4))
PRIOR = ("benchmark_500/formal_bilingual_benchmark_500.csv","holdout_1000/v8_holdout_1000.csv","holdout_v9/v9_unseen_1000.csv","holdout_v10/v10_blind_1000.csv")

FRAMES = {
    "routine": ((0,), (0,1), (0,2), (0,3), (1,0), (2,0), (3,0), (0,1), (0,2), (0,3)),
    "difficult": ((0,1), (0,2), (3,0), (0,1,2), (1,0,3), (2,3,0), (3,0,2), (0,1,3), (2,0,1), (3,2,0)),
    "edge": ((0,1,2), (0,2,3), (1,3,0), (2,0,1), (1,0,3), (3,0,2), (1,2,0,3), (0,2,1,3), (2,0,1,3), (3,2,0,1)),
}

LINKED_FRAMES = {
    "difficult": ((1,0),(1,0,2),(1,0,3),(2,1,0),(3,1,0),(1,2,0),(1,3,0),(1,0,2),(1,0,3),(3,1,0)),
    "edge": ((1,0,2),(1,0,3),(2,1,0),(3,1,0),(1,2,0),(1,3,0),(1,0,2,3),(1,0,3,2),(2,1,0,3),(3,1,0,2)),
}

def csv_bytes(rows, fields):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()

def source_directions(rng, n, en):
    values = ["en"] * en + ["zh"] * (n-en)
    rng.shuffle(values)
    return iter(values)

def read_families(domain):
    families = []
    for line in (ROOT/f"{domain}.txt").read_text().splitlines():
        if line:
            columns = line.split("|")
            assert len(columns) == 13, (len(columns),line)
            tier, topic, issue_type, *bilingual = columns
            families.append((tier,topic,issue_type,list(zip(bilingual[::2], bilingual[1::2]))))
    return families

def render(slots, pairs, lang):
    return (" " if lang == 0 else "").join(pairs[slot][lang] for slot in slots if pairs[slot][lang])

def build():
    rng = random.Random(11497)
    rows = []
    family_number = 0
    for domain_index,(domain, quotas) in enumerate(DOMAINS.items()):
        families = read_families(domain)
        assert Counter(tier for tier,_,_,_ in families) == dict(zip(TIERS, quotas))
        for tier_index,tier in enumerate(TIERS):
            clean_directions = source_directions(rng, quotas[tier_index]*7, EN_CLEAN[domain_index][tier_index])
            issue_directions = source_directions(rng, quotas[tier_index]*3, EN_ISSUE[domain_index][tier_index])
            for selected_tier,topic,issue_type,pairs in families:
                if selected_tier != tier:
                    continue
                family_number += 1
                correct, variant, *context = pairs
                linked = issue_type.endswith("@")
                if linked:
                    issue_type = issue_type[:-1]
                frames = LINKED_FRAMES[tier] if linked else FRAMES[tier]
                if correct[0].count(".") == 2:
                    frames = (*frames[:6], (0,1,3), (1,0,2), (2,0,3), (0,3,2))
                for index, en_order in enumerate(frames):
                    issue = index >= 7
                    authority = next(issue_directions if issue else clean_directions)
                    bilingual = [list(correct), *context]
                    if issue:
                        altered_language = 1 if authority == "en" else 0
                        bilingual[0][altered_language] = variant[altered_language]
                    # Switch the placement of independently worded context where it reads naturally.
                    if linked:
                        # Preserve the definition before its use, but move independent ancillary content.
                        zh_order = en_order if index % 3 == 0 else tuple(
                            [slot for slot in en_order if slot not in (0,1)] + [1,0]
                        )
                    else:
                        zh_order = en_order if index % 3 == 0 else en_order[1:] + en_order[:1]
                    english = render(en_order,bilingual,0)
                    chinese = render(zh_order,bilingual,1)
                    en_evidence, zh_evidence = (s or "[ABSENT — entire required sentence omitted]" for s in bilingual[0])
                    if issue:
                        required, observed = (en_evidence, zh_evidence) if authority == "en" else (zh_evidence, en_evidence)
                        rationale = f"The {'English' if authority == 'en' else 'Chinese'} source states “{required}”. The translation {'omits this requirement' if not bilingual[0][altered_language] else f'changes the {issue_type.replace("_"," ")} to “{observed}”'}."
                    else:
                        rationale = f"The English and Chinese agree on the {topic.lower()} rule and all additional conditions, as indicated by “{en_evidence}” and “{zh_evidence}”."
                    rows.append(dict(family_id=f"K{family_number:03d}",split="holdout",domain=domain,topic=topic,difficulty=tier,source_language=authority,english=english,chinese=chinese,expected_status="issue" if issue else "clean",english_evidence=en_evidence,chinese_evidence=zh_evidence,expected_issue_or_clean_rationale=rationale,severity="material" if issue else "none",issue_type=issue_type if issue else "none",frame_id=f"{family_number:03d}-{index+1:02d}"))
    rng.shuffle(rows)
    for i,row in enumerate(rows, 1):
        row["case_id"] = f"K{i:04d}"
    return rows

def overlap(rows, prior, language):
    def normalize(text):
        return "".join(re.findall(r"\w+", text.casefold()))
    def shingles(text):
        return {text[i:i+5] for i in range(len(text)-4)}
    old_texts = [normalize(row[language]) for row in prior]
    old_grams = [shingles(t) for t in old_texts]
    posting = defaultdict(set)
    for i,grams in enumerate(old_grams):
        for gram in grams:
            posting[gram].add(i)
    old_set = set(old_texts)
    max_ratio = 0.0
    near = []
    exact_hits = 0
    for row in rows:
        normalized = normalize(row[language])
        exact_hits += normalized in old_set
        grams = shingles(normalized)
        possible = set().union(*(posting[gram] for gram in grams))
        for i in possible:
            if len(old_texts[i]) < 0.65*len(normalized) or len(normalized) < 0.65*len(old_texts[i]):
                continue
            common = len(grams & old_grams[i])
            union = len(grams) + len(old_grams[i]) - common
            if union and common/union >= .25:
                ratio = SequenceMatcher(None, normalized, old_texts[i], autojunk=False).ratio()
                max_ratio = max(ratio,max_ratio)
                if ratio >= .85:
                    near.append((row["case_id"], prior[i]["case_id"],round(ratio,3)))
    return {"normalized_exact": exact_hits, "near_matches_at_0.85": near, "largest_ratio_among_shingle_candidates": round(max_ratio,3)}

def main():
    rows = build()
    assert len(rows) == 1000
    assert len({(row["english"],row["chinese"]) for row in rows}) == 1000
    assert Counter(row["source_language"] for row in rows) == {"en":600,"zh":400}
    assert Counter(row["expected_status"] for row in rows) == {"clean":700,"issue":300}
    assert Counter(row["difficulty"] for row in rows) == {"routine":600,"difficult":300,"edge":100}
    assert Counter(row["domain"] for row in rows) == {"school":300,"government":300,"public_email":200,"instructions":200}
    assert Counter((row["difficulty"],row["expected_status"]) for row in rows) == dict(zip(itertools.product(TIERS,("clean","issue")),(420,180,210,90,70,30)))
    for row in rows:
        assert 0 < len(row["english"]) <= 650, row
        assert 0 < len(row["chinese"]) <= 220, row
        for language in ("english","chinese"):
            evidence = row[f"{language}_evidence"]
            assert evidence.startswith("[ABSENT") or evidence in row[language], row
    prior = [row for file in PRIOR for row in csv.DictReader((ROOT.parent/file).open(encoding="utf-8-sig"))]
    assert not {row["topic"].casefold() for row in rows} & {row["topic"].casefold() for row in prior}
    for language in ("english","chinese"):
        assert not {row[language].casefold() for row in rows} & {row[language].casefold() for row in prior}
    for tier, limits in zip(TIERS, ((1,2),(2,3),(3,4))):
        for row in (row for row in rows if row["difficulty"] == tier):
            assert limits[0] <= row["english"].count(".") <= limits[1], row
            assert limits[0] <= row["chinese"].count("。") <= limits[1], row
    result_overlap = {lang:overlap(rows,prior,lang) for lang in ("english","chinese")}
    assert all(x["normalized_exact"] == 0 and not x["near_matches_at_0.85"] for x in result_overlap.values()), result_overlap
    outputs = {"v11_blind_1000.csv": csv_bytes(rows,FIELDS), "v11_blind_inputs.csv": csv_bytes(rows,INPUT_FIELDS)}
    for filename, content in outputs.items():
        path = ROOT/filename
        if path.exists() and path.read_bytes() != content:
            raise RuntimeError(f"Frozen output changed: {filename}")
        path.write_bytes(content)
    files = [*outputs,"build.py",*(f"{domain}.txt" for domain in DOMAINS)]
    report = {
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "prior_notice_overlap": result_overlap,
        "case_lengths_maximum_chars": {lang:max(len(row[lang]) for row in rows) for lang in ("english","chinese")},
        "files_sha256": {filename:hashlib.sha256((ROOT/filename).read_bytes()).hexdigest() for filename in files},
        "families": 100,
        "issue_types": Counter(row["issue_type"] for row in rows if row["expected_status"] == "issue"),
        "sentence_counts": {tier:{language:dict(Counter((row[language].count("。") if language == "chinese" else row[language].count(".")) for row in rows if row["difficulty"]==tier)) for language in ("english","chinese")} for tier in TIERS},
    }
    manifest = ROOT/"frozen_manifest.json"
    if manifest.exists():
        previous = json.loads(manifest.read_text())
        assert previous["files_sha256"] == report["files_sha256"], "Frozen source content changed."
    else:
        manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")

if __name__ == "__main__":
    main()
