"""Reassemble the frozen, tested candidate from the saved cell sources.

This does not run inference or overwrite saved predictions. Changes to semantic
rules must also be integrated into cell29_checker.py and independently validated.
"""
import hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out=root/'candidate_v5'
base=json.loads((root/'Public_Notice_Check_v4_tested.ipynb').read_text())
sem=(out/'semantic_checks.py').read_text()
checker=(out/'cell29_checker.py').read_text()
assert sem in checker
assert hashlib.sha256(sem.encode()).hexdigest() in checker
for i,name in [(0,'cell0_header.md'),(29,'cell29_checker.py'),(33,'cell33_demo.py'),(34,'cell34_benchmark_notes.md'),(35,'cell35_benchmark.py')]:
    base['cells'][i]['source']=(out/name).read_text().splitlines(True)
for c in base['cells']:
    if c['cell_type']=='code':
        c['outputs']=[]
        c['execution_count']=None
base['metadata'].pop('accelerator',None)
(out/'Public_Notice_Check_v5_rebuilt.ipynb').write_text(json.dumps(base,ensure_ascii=False,indent=1))
print('Rebuilt notebook from the frozen tested sources; no models executed.')
