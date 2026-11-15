"""Build the merged notebook and a reproducible, isolated Colab comparison."""
import ast, base64, hashlib, json, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'merged_v5'
def read(name):return (OUT/name).read_text()
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def source(book,i):return ''.join(book['cells'][i]['source'])
def funcs(s,names):
    return '\n\n'.join(ast.get_source_segment(s,n) for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name in names)
base=json.loads((ROOT/'Public_Notice_Check_v4_tested.ipynb').read_text())
friend=json.loads((OUT/'teammate_v5_source.ipynb').read_text())
sem,rel,amb=[read(f) for f in ['semantic_checks.py','relation_checks.py','ambiguity_normalisation.py']]
header='''# Public Notice Check — Merged V5 candidate

Combines our V5 semantic evidence checks with the teammate's V5 wording fixes, and adds bounded checks for document relationships and proxy conditions.

**Evaluation:** the approved 60 cases are a reused regression suite. They are no longer an unseen holdout. No general accuracy claim follows from a perfect result here.

Run cells in order. Sections before the whole-notice checker retain the inherited starter experiments; the merged checker is installed in section 9. Section 11 embeds the approved CSV and runs the final merged checker with fixed thresholds (similarity 0.40, contradiction 0.65). The optional demo does not launch automatically.

The merge preserves event frequency and link destinations when normalising wording. Every added semantic warning includes evidence from both languages. Unsupported or ambiguous patterns are left to the existing models; this remains a finite grammar, not a general language reasoner.

Sources: [teammate V5](https://colab.research.google.com/drive/1zQgH25wQDPfQEKq7658q24PqS2GsXQH9) and our saved V5 candidate. Pretrained model weights are unchanged. Source notebooks have not been overwritten.
'''
if (OUT/'recorded_result.md').exists():
    title,body=header.split('\n\n',1)
    header=title+'\n\n'+read('recorded_result.md')+'\n'+body
(OUT/'cell0_header.md').write_text(header)
notes='''## Wording normalisation with fact preservation

Adapted from teammate V5: event frequency wording, half-price expressions, ordinals, futsal, non-negative words ending in 別, and language-specific links. The merged version keeps frequency and destination facts for comparison rather than simply deleting them. Numbers and conditions still produce warnings when they differ.
'''
(OUT/'cell18_notes.md').write_text(notes)
# An explicit, single checker definition keeps repeated execution predictable.
checker=source(base,29).replace('normalise_text(text, lang)', 'model_text(text, lang)')
checker=sem+'\n\n'+rel+'\n\n'+checker
integration='''
# Fixed production thresholds; no tuning on reference labels.
SIM_T, NLI_T = 0.40, 0.65
CHECKER_VERSION = "merged-v5-candidate"
RULE_SOURCE_HASHES = __HASHES__
SEMANTIC_RULES_SHA256 = RULE_SOURCE_HASHES["semantic_checks.py"]

def paired_evidence(zh,en):
    return semantic_evidence(zh,en)+ambiguity_evidence(zh,en)+relation_evidence(zh,en)

def evidence_reasons(zh,en):
    return [f"{x['category']} differs: Chinese {x['chinese_value']} [{x['chinese_span']}]; English {x['english_value']} [{x['english_span']}]"
            for x in paired_evidence(zh,en)]

def checker_flag(zh,en,sim=None,contra=None):
    sim = similarity(zh,en) if sim is None else sim
    contra = contradiction(zh,en) if contra is None else contra
    reasons = rule_reasons(zh,en)+model_reasons(sim,contra,SIM_T,NLI_T)+evidence_reasons(zh,en)
    return bool(reasons),list(dict.fromkeys(reasons))

_merged_base_check_notice = check_notice

def check_notice(chinese_text,english_text):
    result = _merged_base_check_notice(chinese_text,english_text)
    result["semantic_evidence"] = [paired_evidence(row.chinese,row.english)
        if row.chinese and row.english and row.chinese != "(whole notice)" else []
        for row in result.itertuples()]
    return result

print("Merged candidate loaded; thresholds:", SIM_T, NLI_T)
print("Rule source hashes:", RULE_SOURCE_HASHES)
'''
hashes={k:sha(read(k)) for k in ['semantic_checks.py','relation_checks.py','ambiguity_normalisation.py']}
checker+=integration.replace('__HASHES__',repr(hashes))
(OUT/'cell31_checker.py').write_text(checker)
benchmark=(ROOT/'candidate_v5/cell35_benchmark.py').read_text().replace('v5-candidate','merged-v5-candidate').replace('public_notice_v5_', 'public_notice_merged_').replace('"semantic_rules_sha256": SEMANTIC_RULES_SHA256,','"rule_source_hashes": RULE_SOURCE_HASHES,')
(OUT/'cell37_benchmark.py').write_text(benchmark)
bench_notes='''## Approved 60-case regression benchmark

This cell embeds the exact approved CSV (checksum verified), runs fresh inference and saves `public_notice_merged_predictions.jsonl` plus `public_notice_merged_run.json`. Labels and rationales are used only for scoring after predictions finish. The historical `holdout` column is retained for continuity; those cases have now informed development and are **not unseen**.
'''
(OUT/'cell36_notes.md').write_text(bench_notes)
demo=(ROOT/'candidate_v5/cell33_demo.py').read_text().replace('V5','Merged V5')
(OUT/'cell35_demo.py').write_text(demo)
notebook=json.loads(json.dumps(friend))
for i,s in [(0,header),(18,notes),(19,amb),(31,checker),(35,demo),(36,bench_notes),(37,benchmark)]:
    notebook['cells'][i]['source']=s.splitlines(True)
for c in notebook['cells']:
    if c['cell_type']=='code':c.update(outputs=[],execution_count=None)
notebook['metadata'].pop('accelerator',None)
(OUT/'Public_Notice_Check_merged_candidate.ipynb').write_text(json.dumps(notebook,ensure_ascii=False,indent=1))
# Test rows come from development guards; these are not an unseen benchmark.
guards=[]
tree=ast.parse(read('test_merged_rules.py'))
for node in ast.walk(tree):
    if isinstance(node,ast.FunctionDef) and node.name in {'test_clean_normalisation','test_suppression_must_not_hide_errors','test_clean_relations','test_changed_relations'}:
        values=next(ast.literal_eval(n.value) for n in node.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pairs' for t in n.targets))
        for i,pair in enumerate(values,1):
            guards.append({'case_id':node.name+'_'+str(i),'chinese':pair[0],'english':pair[1], 'expected_status':'clean' if 'clean' in node.name else 'issue','split':'development_guard'})
(OUT/'development_guard_cases.json').write_text(json.dumps(guards,ensure_ascii=False,indent=2))
bundle={
 'base_rules':[source(base,i) for i in [10,11,13,15,17]],
 'model_functions':funcs(source(base,8),{'similarity','contradiction'}),
 'base_checker_functions':funcs(source(base,20),{'model_reasons','checker_flag'}),
 'base_whole_notice':source(base,29),
 'teammate_patch':source(friend,19),
 'ours_checker':(ROOT/'candidate_v5/cell29_checker.py').read_text(),
 'merged_normalisation':amb,'merged_checker':checker,
 'csv_base64':base64.b64encode((ROOT/'public_notice_benchmark.csv').read_bytes()).decode(),
 'guards':guards,'source_hashes':hashes,
 'teammate_notebook_sha256':hashlib.sha256((OUT/'teammate_v5_source.ipynb').read_bytes()).hexdigest(),
}
packed=base64.b64encode(zlib.compress(json.dumps(bundle,ensure_ascii=False).encode(),9)).decode()
harness=read('comparison_harness.py')
(OUT/'isolated_comparison_cell.py').write_text('''# Compare three frozen versions in separate namespaces using the loaded models.
# Original notebook functions remain untouched; results are written to new files.
import base64, zlib, json
merge_bundle = json.loads(zlib.decompress(base64.b64decode("'''+packed+'''")))
'''+harness)
print('Built notebook, comparison cell and',len(guards),'development guards.')
print('Rule hashes',hashes)
