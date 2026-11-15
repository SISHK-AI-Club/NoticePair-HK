from pathlib import Path
import base64,zlib,json,hashlib
root=Path(__file__).resolve().parent
parent=root.parent
pack=lambda s:base64.b64encode(zlib.compress(s if isinstance(s,bytes) else s.encode(),9)).decode()
frozen_packed=(parent/'merged_v5/isolated_comparison_cell.py').read_text().split('base64.b64decode("',1)[1].split('"',1)[0]
csv_bytes=(parent/'benchmark_500/formal_bilingual_benchmark_500.csv').read_bytes()
book=json.loads((parent/'merged_v5/Public_Notice_Check_merged_candidate_saved.ipynb').read_text())
loader=''.join(book['cells'][8]['source'])
new_source=(root/'structured_notice.py').read_text()+'\n'+(root/'adapter.py').read_text()
runner='''# V8 development comparison: approved 500 cases are now reused development data.
# Frozen V7 and V8 run fresh with identical loaded model objects and thresholds.
!pip -q install sentence-transformers==5.7.0 transformers==5.22.1 sentencepiece
import re, pandas as pd, numpy as np, torch
import base64, zlib, json, csv, io, hashlib, time, platform, importlib.metadata, types, sys
from pathlib import Path
from datetime import datetime, timezone
from IPython.display import display, HTML
from collections import Counter
torch.set_num_threads(2)
torch.manual_seed(8)
'''+loader+'\n'
runner+=f'''frozen=json.loads(zlib.decompress(base64.b64decode({frozen_packed!r})))
raw=zlib.decompress(base64.b64decode({pack(csv_bytes)!r}))
assert hashlib.sha256(raw).hexdigest()=={hashlib.sha256(csv_bytes).hexdigest()!r}
references=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
assert len(references)==len({{r['case_id'] for r in references}})==500
# Only bilingual input and identifier pass to the prediction loop.
inputs=[{{k:r[k] for k in ('case_id','chinese','english')}} for r in references]
patch=zlib.decompress(base64.b64decode({pack(new_source)!r})).decode()
assert hashlib.sha256(patch.encode()).hexdigest()=={hashlib.sha256(new_source.encode()).hexdigest()!r}
'''
runner+='''
def make_checker(name,patched=False):
    module=types.ModuleType(name)
    sys.modules[name]=module
    ns=module.__dict__
    ns.update({k:globals()[k] for k in ['re','pd','np','torch','labse','util','nli_tok','nli_model','device','CONTRA']})
    for src in [frozen['model_functions'],*frozen['base_rules'],frozen['base_checker_functions'],frozen['merged_normalisation'],frozen['merged_checker']]:
        exec(src,ns)
    if patched: exec(patch,ns)
    assert (ns['SIM_T'],ns['NLI_T'])==(0.4,0.65)
    assert ns['RULE_SOURCE_HASHES']==frozen['source_hashes']
    return ns
baseline=make_checker('v7_frozen_comparison')
candidate=make_checker('v8_candidate_comparison',True)
started=datetime.now(timezone.utc).isoformat()
results=[]
Path('v8_500_partial.jsonl').write_text('')
print('Starting fresh V7 + V8 predictions: 500 notices on',device,flush=True)
for i,case in enumerate(inputs,1):
    item={'case_id':case['case_id']}
    for name,checker in [('frozen',baseline),('candidate',candidate)]:
        frame=checker['check_notice'](case['chinese'],case['english'])
        item[name]=json.loads(frame.to_json(orient='records',force_ascii=False))
    results.append(item)
    with Path('v8_500_partial.jsonl').open('a') as f:f.write(json.dumps(item,ensure_ascii=False)+'\\n')
    if i%25==0:print(f'{i}/500 complete for BOTH versions',flush=True)
# Score only after every prediction has finished.
counts={name:Counter() for name in ['frozen','candidate']}
by_tier={name:{tier:Counter() for tier in ['routine','difficult','edge']} for name in counts}
for case,res in zip(references,results):
    assert case['case_id']==res['case_id']
    truth=case['expected_status']=='issue'
    for name in counts:
        flagged=any(r['why'] for r in res[name])
        outcome=('T' if truth==flagged else 'F')+('P' if flagged else 'N')
        counts[name][outcome]+=1
        by_tier[name][case['difficulty']][outcome]+=1
metadata=dict(started=started,completed=datetime.now(timezone.utc).isoformat(),device=str(device),
    dataset_sha256=hashlib.sha256(raw).hexdigest(),candidate_sha256=hashlib.sha256(patch.encode()).hexdigest(),
    baseline_source_sha256=hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest(),
    source_hashes=frozen['source_hashes'],thresholds=[0.4,0.65],
    python=platform.python_version(),packages={p:importlib.metadata.version(p) for p in ['torch','transformers','sentence-transformers']},
    model_ids=['sentence-transformers/LaBSE',NLI_NAME],shared_model_objects=True,
    evaluation='reused development benchmark; not held out for V8',counts=counts,by_difficulty=by_tier)
output=json.dumps(dict(metadata=metadata,results=results),ensure_ascii=False,indent=2)
Path('v8_500_results.json').write_text(output)
print('COMPARISON COMPLETE',flush=True)
for name in counts:
    print(name,dict(counts[name]),'accuracy',(counts[name]['TP']+counts[name]['TN'])/500)
    for tier,c in by_tier[name].items():print('  ',tier,dict(c),'accuracy',(c['TP']+c['TN'])/sum(c.values()))
print('Dataset SHA256:',metadata['dataset_sha256'])
print('Candidate SHA256:',metadata['candidate_sha256'])
# A compact, visible export of the complete raw outputs, not only aggregate scores.
export=base64.b64encode(zlib.compress(output.encode(),9)).decode()
display(HTML('<details><summary>Complete raw comparison export (compressed base64)</summary><textarea id="v8-result-export" rows="5" style="width:100%">'+export+'</textarea></details>'))
print('Raw results saved to v8_500_results.json')
'''
(root/'colab_run.py').write_text(runner)
# Make an importable, readable patched notebook as well as the compact runner.
book={'nbformat':4,'nbformat_minor':5,'metadata':{'colab':{'name':'V8 - structured notice comparison.ipynb'},'kernelspec':{'name':'python3','display_name':'Python 3'},'accelerator':'GPU'},'cells':[{'cell_type':'markdown','metadata':{},'source':['# V8 structured notice checker — development comparison\n','This revision uses the 500 cases for development; results are not held-out accuracy. Both versions run fresh with shared models. No pretrained weights are fine-tuned.\n']},{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':runner.splitlines(True)}]}
(root/'V8_structured_notice_comparison.ipynb').write_text(json.dumps(book,ensure_ascii=False,indent=1))
manifest={'dataset_sha256':hashlib.sha256(csv_bytes).hexdigest(),'candidate_sha256':hashlib.sha256(new_source.encode()).hexdigest(),'files':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in ['structured_notice.py','adapter.py','colab_run.py']}}
(root/'source_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Built candidate:',manifest['candidate_sha256'],'runner characters:',len(runner))
