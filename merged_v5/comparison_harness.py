import contextlib, io, csv, hashlib, time, platform, importlib.metadata, zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

merge_original_state=(check_notice,checker_flag,SIM_T,NLI_T)
merge_payload=base64.b64decode(merge_bundle['csv_base64'])
assert hashlib.sha256(merge_payload).hexdigest()=='eadcf4d7c6149e9656be2522f63977c25cb62fa6d0a206046ad96e8de746dfc1'
merge_cases=list(csv.DictReader(io.StringIO(merge_payload.decode('utf-8-sig'))))
assert len(merge_cases)==60
merge_inputs={k:globals()[k] for k in ['re','pd','np','torch','labse','util','nli_tok','nli_model','device','CONTRA']}
merge_namespaces={}
for version in ['teammate_v5','our_v5','merged_v5']:
    ns=dict(merge_inputs)
    with contextlib.redirect_stdout(io.StringIO()):
        exec(merge_bundle['model_functions'],ns)
        for s in merge_bundle['base_rules']:exec(s,ns)
        exec(merge_bundle['base_checker_functions'],ns)
        ns.update(SIM_T=0.4,NLI_T=0.65)
        if version=='teammate_v5':
            exec(merge_bundle['teammate_patch'],ns)
            exec(merge_bundle['base_whole_notice'],ns)
        elif version=='our_v5':exec(merge_bundle['ours_checker'],ns)
        else:
            exec(merge_bundle['merged_normalisation'],ns)
            exec(merge_bundle['merged_checker'],ns)
    merge_namespaces[version]=ns
merge_out=Path('merged_comparison');merge_out.mkdir(exist_ok=True)
merge_meta={'run_at_utc':datetime.now(timezone.utc).isoformat(), 'device':str(device),
 'dataset_sha256':hashlib.sha256(merge_payload).hexdigest(), 'similarity_threshold':0.4,'contradiction_threshold':0.65,
 'python':platform.python_version(),'packages':{p:importlib.metadata.version(p) for p in ['torch','transformers','sentence-transformers']},
 'source_hashes':merge_bundle['source_hashes'],'teammate_notebook_sha256':merge_bundle['teammate_notebook_sha256'],
 'model_ids':{'embedding':'sentence-transformers/LaBSE','nli':NLI_NAME},
 'evaluation_type':'reused 60-case regression + development guard examples; neither is an unseen holdout'}
merge_results={}
for version,ns in merge_namespaces.items():
    for dataset,cases in [('approved60',merge_cases),('development_guards',merge_bundle['guards'])]:
        results=[]
        path=merge_out/(version+'_'+dataset+'_predictions.jsonl')
        print('Running',version,dataset,len(cases),'cases;',device,flush=True)
        with path.open('w',encoding='utf-8') as sink:
            for n,c in enumerate(cases,1):
                start=time.perf_counter();r={'case_id':c['case_id']}
                try:r['rows']=ns['check_notice'](c['chinese'],c['english']).to_dict('records')
                except Exception as exc:r['error']=repr(exc)
                r['seconds']=round(time.perf_counter()-start,3)
                sink.write(json.dumps(r,ensure_ascii=False)+'\n');sink.flush();results.append(r)
                if n%10==0:print(version,dataset,n,'/',len(cases),flush=True)
        merge_results[(version,dataset)]=results
assert not any('error' in r for results in merge_results.values() for r in results),'Execution errors; inspect files before scoring.'
# Consult reference labels only after ALL inference is finished.
merge_metrics=[]
for (version,dataset),results in merge_results.items():
    cases=merge_cases if dataset=='approved60' else merge_bundle['guards'];by_id={c['case_id']:c for c in cases}
    for split in (['all','dev','holdout'] if dataset=='approved60' else ['all']):
        counts=Counter();missed=[];false_alarms=[]
        for r in results:
            c=by_id[r['case_id']]
            if split!='all' and c['split']!=split:continue
            truth=c['expected_status']=='issue';predicted=any(x['why'] for x in r['rows'])
            counts[('T' if truth==predicted else 'F')+('P' if predicted else 'N')]+=1
            if truth and not predicted:missed.append(c['case_id'])
            if not truth and predicted:false_alarms.append(c['case_id'])
        m={'version':version,'dataset':dataset,'split':split,**{k:counts[k] for k in ['TP','FN','FP','TN']}}
        m.update(accuracy=(m['TP']+m['TN'])/sum(counts.values()),recall=m['TP']/(m['TP']+m['FN']),missed=missed,false_alarms=false_alarms)
        merge_metrics.append(m)
merge_meta['metrics']=merge_metrics
(merge_out/'run_metadata.json').write_text(json.dumps(merge_meta,ensure_ascii=False,indent=2))
assert (check_notice,checker_flag,SIM_T,NLI_T)==merge_original_state
with zipfile.ZipFile('merged_comparison_results.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(merge_out.glob('*')):archive.write(path,path.name)
print('\nCOMPARISON COMPLETE. Original functions and thresholds unchanged.')
print('Reused regression suite; not unseen accuracy.')
display(pd.DataFrame(merge_metrics)[['version','dataset','split','TP','FN','FP','TN','accuracy','recall']])
print('Saved: merged_comparison_results.zip')
