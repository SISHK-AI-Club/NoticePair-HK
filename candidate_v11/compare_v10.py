"""Reproduce frozen V10 decisions using unchanged frozen neural signals.

No second neural pass: V11 retains the exact V10 signal extractor. The replay
is first verified on all 2,000 previously saved V10 predictions.
"""
import json,csv,hashlib,sys,argparse
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root.parent))
from candidate_v10.facts import normal,direct_evidence
old=root.parent/'candidate_v10';config=json.loads((old/'config.json').read_text())
manifest=json.loads((old/'frozen_manifest.json').read_text())
assert all(hashlib.sha256((old/f).read_bytes()).hexdigest()==h for f,h in manifest['files'].items())

def semantic(s):
 c=config
 if s.get('translation_quality',1)<c['translation_quality_min']:return False
 x=max(s['cross']);m=max(s['translated']);b=min(s['translated'])
 return ((b>=c['mt_bidirectional'] and x>=c['cross_support']) or
         (m>=c['mt_oneway'] and x>=c['cross_support']) or
         (s['similarity']<c['similarity_max'] and m>=c['mt_low_similarity'] and x>=c['cross_support']))

def replay(p,e,z):
 if p['coverage']!='complete_notice':return True
 s=p['signals'];facts=direct_evidence(normal(z),normal(e))
 for a in s['passages']:
  if a['similarity']>=config['fact_alignment_min']:facts+=direct_evidence(a['chinese_span'],a['english_span'])
 sem=semantic(s)
 supported=[a for a in s['passages'] if a['similarity']>=config['semantic_alignment_min'] and semantic(a)]
 if supported:sem=True
 elif len(s['passages'])>1 and not (min(s['cross'])>=config['whole_cross_min'] and min(s['translated'])>=config['whole_mt_min']):sem=False
 return bool(facts or sem)

def metrics(rows,preds):
 c=Counter()
 for g in rows:
  truth=g['expected_status']=='issue';pr=preds[g['case_id']]
  c['tp' if truth and pr else 'fn' if truth else 'fp' if pr else 'tn']+=1
 return {k:c[k] for k in ['tp','tn','fp','fn']}|dict(n=len(rows),accuracy=(c['tp']+c['tn'])/len(rows),recall=c['tp']/(c['tp']+c['fn']),false_alarm_rate=c['fp']/(c['fp']+c['tn']))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--gold');p.add_argument('--predictions');a=p.parse_args()
 records=json.loads((root/'dev_records.json').read_text())
 mismatches=[]
 for z in records:
  g=z['gold'];pr=z['prediction']
  if replay(pr,g['english'],g['chinese'])!=pr['flagged']:mismatches.append(g['case_id'])
 assert not mismatches,mismatches
 print('Frozen V10 decision replay matches all 2,000 original predictions.')
 if not a.gold:sys.exit()
 gold=list(csv.DictReader(open(a.gold,encoding='utf-8-sig')));pred=json.load(open(a.predictions));pm={r['case_id']:r for r in pred['results']}
 v10={g['case_id']:replay(pm[g['case_id']],g['english'],g['chinese']) for g in gold};v11={k:p['flagged'] for k,p in pm.items()}
 report=dict(method='Frozen V10 decisions replayed from identical neural signals produced by V11; replay verified on 2000 original V10 predictions.',v10_frozen_hash=manifest['candidate_sha256'],v11_frozen_hash=json.loads((root/'frozen_manifest.json').read_text())['source_bundle_sha256'],v10={},v11={})
 for name,pr in [('v10',v10),('v11',v11)]:
  for tier in ['overall','routine','difficult','edge']:report[name][tier]=metrics([g for g in gold if tier=='overall' or g['difficulty']==tier],pr)
 changes=Counter()
 for g in gold:
  cid=g['case_id'];truth=g['expected_status']=='issue'
  if v10[cid]==v11[cid]:continue
  changes[('fixed_' if v11[cid]==truth else 'regressed_')+('miss' if truth else 'false_alarm')]+=1
 report['changes']=dict(changes)
 out=Path(a.predictions).parent;(out/'v10_comparison.json').write_text(json.dumps(report,indent=2)+'\n')
 with (out/'v10_comparison.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['case_id','difficulty','issue_type','expected_status','v10_flagged','v11_flagged']);w.writeheader();w.writerows({k:g[k] for k in ['case_id','difficulty','issue_type','expected_status']}|dict(v10_flagged=v10[g['case_id']],v11_flagged=v11[g['case_id']]) for g in gold)
 print(json.dumps(report,indent=2))
