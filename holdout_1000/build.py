import base64, csv, hashlib, json, random, re, zlib
from collections import Counter, defaultdict
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parent
rng = random.Random(806734)
def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))

prior = read_csv(root/'benchmark_500/formal_bilingual_benchmark_500.csv')
keys = ('domain','difficulty','source_language','expected_status')
quotas = Counter(tuple(row[k] for k in keys) for row in prior)
scenarios = defaultdict(list)
for line in (out/'scenarios.txt').read_text().splitlines():
    if line.startswith('#') or not line.strip():
        continue
    tier, *spec = line.replace(r'\n','\n').split('|')
    scenarios[tier].append(spec)
contexts = {
    'school': [('Media equipment desk','媒體器材服務處'),('Student activities office','學生活動處'),('School library services','學校圖書館服務'),('Campus facilities office','校園設施處'),('Parent liaison desk','家長聯絡處'),('Continuing education unit','持續教育組')],
    'government': [('District service kiosk','地區服務站'),('Public records counter','公共紀錄櫃位'),('Community facility office','社區設施辦事處'),('Municipal archive desk','市政檔案服務處'),('Civic centre reception','市民中心接待處'),('Resident services unit','居民服務組')],
    'public_email': [('Visitor support','訪客服務'),('Exhibition enquiries','展覽查詢'),('Member services','會員服務'),('Bookings team','預約組'),('Parcel enquiries','包裹查詢'),('Community programme desk','社區活動服務處')],
    'instructions': [('Storage and returns','寄存及退還'),('Visitor information','訪客須知'),('Service counter guide','櫃位服務指南'),('On-site instructions','現場指引'),('Operations desk','運作服務處'),('Access and collection','進出及領取')],
}
formats = [
    ('{h}\n{body}', '{h}\n{body}'),
    ('{body}\n— {h}', '{h} 敬啟\n{body}'),
    ('From: {h}\n\n{body}', '發訊單位：{h}\n\n{body}'),
    ('[{h}]\n\n{body}', '【{h}】\n\n{body}'),
    ('{h}\n────────\n{body}', '{body}\n────────\n{h}'),
    ('{body}\nIssued by {h}', '{h}發布\n{body}'),
]
rows = []
for domain in contexts:
    for tier, pool in scenarios.items():
        assignments = [(language,status) for (d,t,language,status),n in quotas.items() if (d,t)==(domain,tier) for _ in range(2*n)]
        rng.shuffle(assignments)
        choices = [(s,c,f) for s in range(len(pool)) for c in range(len(contexts[domain])) for f in range(len(formats))]
        # Rotate through all structures before reusing any.
        rng.shuffle(choices)
        buckets = defaultdict(list)
        for choice in choices:
            buckets[choice[0]].append(choice)
        choices = [buckets[s][i] for i in range(len(contexts[domain])*len(formats)) for s in rng.sample(range(len(pool)),len(pool))]
        for (language,status),(s,c,f) in zip(assignments,choices,strict=False):
            topic, en, zh, ec, ew, zc, zw = pool[s]
            a,b = rng.sample(range(2,89),2)
            values = dict(a=a,b=b,n=rng.randint(4,29))
            ec,ew,zc,zw = [value.format(**values) for value in (ec,ew,zc,zw)]
            ev = ew if status=='issue' and language=='zh' else ec
            zv = zw if status=='issue' and language=='en' else zc
            english = formats[f][0].format(h=contexts[domain][c][0],body=en.format(v=ev,**values))
            chinese = formats[f][1].format(h=contexts[domain][c][1],body=zh.format(v=zv,**values))
            rationale = f'{topic}: English specifies {ev!r} and Chinese specifies {zv!r}.'
            rows.append(dict(family_id=f'{tier}-{s+1:02d}',split='holdout',domain=domain,topic=topic,difficulty=tier,
                source_language=language,english=english,chinese=chinese,expected_status=status,english_evidence=ev,
                chinese_evidence=zv,expected_issue_or_clean_rationale=rationale,severity='material' if status=='issue' else 'none'))
rng.shuffle(rows)
rows = [dict(case_id=f'H{i:04d}',**row) for i,row in enumerate(rows,1)]
assert len(rows)==1000
assert Counter(tuple(row[k] for k in keys) for row in rows)=={k:2*n for k,n in quotas.items()}
for column in ('english','chinese'):
    normalize = lambda s: re.sub(r'\W+','',s.casefold())
    assert not {normalize(r[column]) for r in rows} & {normalize(r[column]) for r in prior}
    assert len({r[column] for r in rows})==1000,column
dataset = out/'v8_holdout_1000.csv'
with dataset.open('w',encoding='utf-8-sig',newline='') as file:
    writer=csv.DictWriter(file,fieldnames=rows[0])
    writer.writeheader()
    writer.writerows(rows)
raw=dataset.read_bytes()
prior_runner=(root/'candidate_v8/colab_run.py').read_text()
encoded=base64.b64encode(zlib.compress(raw,9)).decode()
runner=re.sub(r"raw=zlib.decompress\(base64.b64decode\('[^']+'\)\)",f"raw=zlib.decompress(base64.b64decode('{encoded}'))",prior_runner,count=1)
runner=re.sub(r"assert hashlib.sha256\(raw\).hexdigest\(\)=='[^']+'",f"assert hashlib.sha256(raw).hexdigest()=='{hashlib.sha256(raw).hexdigest()}'",runner,count=1)
runner=runner.replace('approved 500 cases are now reused development data','new synthetic holdout').replace('V8 development comparison','V8 held-out comparison').replace('reused development benchmark; not held out for V8','fresh synthetic holdout for frozen V8')
runner=runner.replace('==500','==1000').replace('/500','/1000').replace('500 notices','1000 notices').replace('v8_500','v8_holdout_1000')
(out/'colab_run.py').write_text(runner)
book=json.loads((root/'candidate_v8/V8_structured_notice_comparison.ipynb').read_text())
cell=next(cell for cell in book['cells'] if cell['cell_type']=='code')
cell.update(source=runner.splitlines(True),outputs=[],execution_count=None)
book['cells']=[cell]
(out/'V8_holdout_1000.ipynb').write_text(json.dumps(book,ensure_ascii=False))
print(len(rows), Counter(r['difficulty'] for r in rows),len(set(r['family_id'] for r in rows)),hashlib.sha256(raw).hexdigest())
