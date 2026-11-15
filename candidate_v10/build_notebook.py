"""Bundle the exact frozen checker into an importable Colab notebook."""
import base64,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
files={p.name:base64.b64encode(p.read_bytes()).decode() for p in [root/f for f in ['engine.py','facts.py','terminology.py','config.json','run.py','frozen_manifest.json']]}
install='!pip -q install sentence-transformers==5.7.0 transformers==5.22.1 sentencepiece pandas scipy opencc-python-reimplemented==0.1.7\n'
load='''from pathlib import Path
import base64, json, sys, hashlib
folder=Path('/content/v10')
folder.mkdir(exist_ok=True)
'''+f'payload={files!r}\n'+'''for name,data in payload.items():
    (folder/name).write_bytes(base64.b64decode(data))
manifest=json.loads((folder/'frozen_manifest.json').read_text())
for name,digest in manifest['files'].items():
    assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
sys.path.insert(0,str(folder))
from engine import Checker
checker=Checker(cache='/content/v10_cache.json')
check_notice=checker.check_notice
print('Frozen V10 loaded. V7 is not imported or called.')
'''
example='''# Replace these example strings with your notice.
chinese_text='請於星期五提交表格。'
english_text='Please submit the form on Friday.'
check_notice(chinese_text,english_text)
'''
bench='''# Upload the separately supplied v10_runner_inputs.csv to /content first.
# This cell runs predictions only; ground-truth labels are not supplied to the checker.
import csv
inputs=list(csv.DictReader(open('/content/v10_runner_inputs.csv',encoding='utf-8-sig')))
assert set(inputs[0])=={'case_id','english','chinese'}
results=[]
for i in range(0,len(inputs),50):
    results.extend(checker.predict_many(inputs[i:i+50]))
    print(len(results),'/',len(inputs))
Path('/content/v10_predictions.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('Predictions saved. Join the answer key only after prediction is complete.')
'''
cells=[dict(cell_type='markdown',metadata={},source=['# V10 contextual notice checker\n','Frozen local pretrained-model prototype. It compares complete contexts and explicit bilingual facts, with a sentence-by-sentence translation cross-check. No V7 fallback is used. A clean result means no discrepancy was found, not that a translation is certified.\n','The NLLB component is a research model under CC-BY-NC-4.0; see the project README and model card for deployment limitations.\n'])]
for src in [install,load,example,bench]:cells.append(dict(cell_type='code',metadata={},execution_count=None,outputs=[],source=src.splitlines(True)))
book=dict(nbformat=4,nbformat_minor=5,metadata=dict(kernelspec=dict(name='python3',display_name='Python 3'),colab=dict(name='Public_Notice_Check_V10_frozen.ipynb')),cells=cells)
(root/'Public_Notice_Check_V10_frozen.ipynb').write_text(json.dumps(book,ensure_ascii=False,indent=1))
print('Built frozen V10 Colab notebook')
