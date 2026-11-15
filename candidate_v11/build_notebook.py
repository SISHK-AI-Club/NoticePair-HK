"""Bundle the frozen V11 predictor into a portable Colab notebook."""
import base64,json
from pathlib import Path
r=Path(__file__).resolve().parent
manifest=json.loads((r/'frozen_manifest.json').read_text())
files={name:base64.b64encode((r/name).read_bytes()).decode() for name in [*manifest['files'],'frozen_manifest.json']}
install='!pip -q install sentence-transformers==5.7.0 transformers==5.22.1 sentencepiece==0.2.3 opencc-python-reimplemented==0.1.7 pandas scipy numpy\n'
load='''from pathlib import Path
import base64, json, sys, hashlib
folder=Path('/content/v11_checker')
folder.mkdir(exist_ok=True)
'''+f'payload={files!r}\n'+'''for name,data in payload.items():
    (folder/name).write_bytes(base64.b64decode(data))
manifest=json.loads((folder/'frozen_manifest.json').read_text())
for name,digest in manifest['files'].items():
    assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
sys.path.insert(0,'/content')
from v11_checker.engine import Checker
checker=Checker(cache='/content/v11_cache.json')
check_notice=checker.check_notice
print('Frozen V11 loaded. No V7 fallback.')
'''
example='''chinese_text='請於星期五提交表格。'
english_text='Please submit the form on Friday.'
check_notice(chinese_text, english_text)
'''
bench='''# Upload the INPUTS-ONLY CSV supplied in the benchmark bundle.
# Its three columns are case_id, english, chinese; keep the answer key separate.
from google.colab import files
import csv, io, subprocess, gc, torch
uploaded=files.upload()
assert len(uploaded)==1, 'Upload one inputs-only CSV.'
name, raw=next(iter(uploaded.items()))
rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
assert rows and set(rows[0])=={'case_id','english','chinese'}
input_path=Path('/content/v11_inputs.csv')
input_path.write_bytes(raw)
# Release interactive model memory before starting the frozen benchmark runner.
del check_notice, checker
gc.collect()
if torch.cuda.is_available(): torch.cuda.empty_cache()
subprocess.run([sys.executable,str(folder/'run.py'),'--inputs',str(input_path),
    '--output','/content/v11_predictions.json','--cache','/content/v11_cache.json',
    '--require-frozen'],check=True)
files.download('/content/v11_predictions.json')
'''
intro='''# V11 bilingual notice checker

V11 compares the information conveyed in both directions. Its frozen equivalence classifier uses contradiction, entailment, neutral, similarity and explicit-fact signals. A corroborated qualifier check helps identify missing conditions. No V7 fallback is called.

The score is a decision score, not a calibrated probability. A clean verdict means no discrepancy was found. The supplied report describes the fresh benchmark and its limitations.

The included source and pretrained model revisions are frozen. This notebook is a Colab-ready copy; the reported benchmark was executed in the local CPU runtime, not Colab. The NLLB component is a research model licensed CC-BY-NC-4.0. See https://huggingface.co/facebook/nllb-200-distilled-600M.
'''
cells=[dict(cell_type='markdown',metadata={},source=intro.splitlines(True))]
for src in [install,load,example,bench]:cells.append(dict(cell_type='code',metadata={},execution_count=None,outputs=[],source=src.splitlines(True)))
book=dict(nbformat=4,nbformat_minor=5,metadata=dict(kernelspec=dict(name='python3',display_name='Python 3'),colab=dict(name='Public_Notice_Check_V11_frozen.ipynb')),cells=cells)
(r/'Public_Notice_Check_V11_frozen.ipynb').write_text(json.dumps(book,ensure_ascii=False,indent=1))
# Verify every bundled byte against the frozen source, without loading models.
assert {k:base64.b64decode(v) for k,v in files.items()}=={k:(r/k).read_bytes() for k in files}
for c in cells[2:]:
 if c['cell_type']=='code':compile(''.join(c['source']),'<notebook>','exec')
print('Notebook payload and Python cells verified.')
