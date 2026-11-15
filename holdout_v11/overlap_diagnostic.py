"""Independent near-overlap diagnostic for the already frozen benchmark."""
import csv
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

ROOT = Path(__file__).resolve().parent
PRIOR = (
    "benchmark_500/formal_bilingual_benchmark_500.csv",
    "holdout_1000/v8_holdout_1000.csv",
    "holdout_v9/v9_unseen_1000.csv",
    "holdout_v10/v10_blind_1000.csv",
)


def read(path):
    with path.open(encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalize(text):
    return "".join(re.findall(r"\w+", text.casefold()))


def report():
    fresh = read(ROOT / "v11_blind_1000.csv")
    older = [row for file in PRIOR for row in read(ROOT.parent/file)]
    output = {}
    for lang in ["english", "chinese"]:
        new_text = [normalize(row[lang]) for row in fresh]
        old_text = [normalize(row[lang]) for row in older]
        vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2,5), sublinear_tf=True)
        all_vectors = vectorizer.fit_transform(old_text + new_text)
        knn = NearestNeighbors(n_neighbors=12,algorithm="brute",metric="cosine")
        knn.fit(all_vectors[:len(older)])
        distance, index = knn.kneighbors(all_vectors[len(older):])
        max_by_edit_match = max(
            (SequenceMatcher(None,text,old_text[j],autojunk=False).ratio(),i,j)
            for i,text in enumerate(new_text) for j in index[i]
        )
        score,i,j = max_by_edit_match
        normalized_old = set(old_text)
        output[lang] = {
            "prior_notices_compared": len(older),
            "normalized_exact": sum(text in normalized_old for text in new_text),
            "maximum_normalized_edit_similarity_in_12_closest_candidates_per_notice": round(score,4),
            "nearest_pair": [fresh[i]["case_id"],older[j]["case_id"]],
            "distinct_current_notices": len(set(new_text)),
        }
    (ROOT / "overlap_diagnostic.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))


if __name__ == "__main__":
    report()
