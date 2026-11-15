"""Build the Colab runner from the verified frozen comparison sources."""
import ast
import base64
import hashlib
import json
import zlib
from pathlib import Path

here = Path(__file__).resolve().parent
merged = here.parent / 'merged_v5'
packed = (merged / 'isolated_comparison_cell.py').read_text().split('base64.b64decode("', 1)[1].split('"', 1)[0]
bundle = json.loads(zlib.decompress(base64.b64decode(packed)))
book = json.loads((merged / 'Public_Notice_Check_merged_candidate_saved.ipynb').read_text())
source = lambda i: ''.join(book['cells'][i]['source'])
payload = (here / 'formal_bilingual_benchmark_500.csv').read_bytes()
runner = '''# Held-out run of the frozen merged checker
!pip -q install sentence-transformers==5.7.0 transformers==5.22.1 sentencepiece
import re, pandas as pd, numpy as np, torch
torch.set_num_threads(2)
import base64, zlib, json, csv, io, hashlib, time, platform, importlib.metadata
from pathlib import Path
from datetime import datetime, timezone
'''
runner += f'''
frozen = json.loads(zlib.decompress(base64.b64decode({packed!r})))
raw = zlib.decompress(base64.b64decode({base64.b64encode(zlib.compress(payload)).decode()!r}))
assert hashlib.sha256(raw).hexdigest() == {hashlib.sha256(payload).hexdigest()!r}
cases = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
assert len(cases) == len({{c["case_id"] for c in cases}}) == 500
'''
runner += 'if not all(k in globals() for k in ("labse","nli_model","nli_tok","CONTRA")):\n' + ''.join('    '+line for line in source(8).splitlines(keepends=True)) + '\n' + '''
namespace = {k: globals()[k] for k in ['re','pd','np','torch','labse','util','nli_tok','nli_model','device','CONTRA']}
for source in [frozen['model_functions'], *frozen['base_rules'],
               frozen['base_checker_functions'], frozen['merged_normalisation'],
               frozen['merged_checker']]:
    exec(source, namespace)
assert (namespace['SIM_T'], namespace['NLI_T']) == (0.4, 0.65)
assert namespace['RULE_SOURCE_HASHES'] == frozen['source_hashes']
started = datetime.now(timezone.utc).isoformat()
results = []
partial = Path("formal500_partial.jsonl")
partial.write_text("")
print("Starting 500 held-out predictions on", device, flush=True)
for i, case in enumerate(cases, 1):
    output = namespace['check_notice'](case['chinese'], case['english'])
    results.append({'case_id': case['case_id'], 'rows': output.to_dict('records')})
    with partial.open("a") as out:
        out.write(json.dumps(results[-1], ensure_ascii=False) + chr(10))
    if i % 10 == 0:
        print(f"{i}/500", flush=True)
counts = dict(TP=0, TN=0, FP=0, FN=0)
for case, result in zip(cases, results):
    truth = case['expected_status'] == 'issue'
    flagged = any(row['why'] for row in result['rows'])
    counts[('T' if flagged == truth else 'F') + ('P' if flagged else 'N')] += 1
meta = dict(started=started, device=str(device), counts=counts,
            csv_sha256=hashlib.sha256(raw).hexdigest(),
            rules=frozen['source_hashes'], thresholds=[0.4,0.65],
            python=platform.python_version(), packages={p:importlib.metadata.version(p) for p in
                ['torch','transformers','sentence-transformers']},
            model_ids=['sentence-transformers/LaBSE', NLI_NAME],
            revisions=[getattr(labse[0].auto_model.config,'_commit_hash',None),
                       getattr(nli_model.config,'_commit_hash',None)])
Path('formal500_results.json').write_text(json.dumps(dict(metadata=meta, results=results),ensure_ascii=False,indent=2))
print("Held-out run complete", counts, flush=True)
print("Accuracy:", (counts['TP'] + counts['TN']) / len(cases))
'''
(here / 'colab_run.py').write_text(runner)
