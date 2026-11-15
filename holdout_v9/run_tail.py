checker = make_checker('v9_frozen_holdout', True)['check_notice']
results = []
started = datetime.now(timezone.utc).isoformat()
print('Running frozen V9 on',device,flush=True)
for i, case in enumerate(inputs,1):
    frame = checker(case['chinese'],case['english'])
    results.append(dict(case_id=case['case_id'], warnings=json.loads(frame.to_json(orient='records',force_ascii=False))))
    if i%50==0:
        print(f'{i}/1000 complete',flush=True)

counts = {tier:Counter() for tier in ('overall','routine','difficult','edge')}
paths = Counter()
for case, result in zip(references,results,strict=True):
    assert case['case_id']==result['case_id']
    flagged = any(w['why'] for w in result['warnings'])
    truth = case['expected_status']=='issue'
    outcome = ('T' if truth==flagged else 'F')+('P' if flagged else 'N')
    counts['overall'][outcome]+=1
    counts[case['difficulty']][outcome]+=1
    paths.update(set(w.get('decision_path','unknown') for w in result['warnings']))
for tier,c in counts.items():
    print(tier,dict(c),'accuracy',(c['TP']+c['TN'])/sum(c.values()))
print('Decision paths:',dict(paths))
metadata = dict(dataset_sha256=hashlib.sha256(raw).hexdigest(),
                candidate_sha256=hashlib.sha256(patch.encode()).hexdigest(),
                started=started,completed=datetime.now(timezone.utc).isoformat(),device=device,
                counts=counts,paths=paths)
output = json.dumps(dict(metadata=metadata,results=results),ensure_ascii=False)
Path('v9_unseen_1000_results.json').write_text(output)
export = base64.b64encode(zlib.compress(output.encode(),9)).decode()
display(HTML('<details><summary>Complete frozen V9 results export</summary><textarea id="v9-unseen-export" rows="5">'+export+'</textarea></details>'))
print('FROZEN V9 BENCHMARK COMPLETE',flush=True)
