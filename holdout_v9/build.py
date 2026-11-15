import base64
import csv
import hashlib
import json
import random
import re
import zlib
from collections import Counter, defaultdict
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parent
rng = random.Random(97143)

def read(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig', newline='')))

old = read(root/'holdout_1000/v8_holdout_1000.csv')
keys = ('domain', 'difficulty', 'source_language', 'expected_status')
quotas = Counter(tuple(row[k] for k in keys) for row in old)
groups = defaultdict(list)
for number, line in enumerate((out/'families.tsv').read_text().splitlines(), 1):
    domain, tier, topic, en, zh, *options = line.split('|')
    pairs = [tuple(x.split('/', 1)) if '/' in x else (x, x) for x in options]
    groups[domain,tier].append((number,topic,en,zh,pairs))

contexts = [
    ('Revision notice','修訂通知'),
    ('For circulation','供傳閱'),
    ('Text for publication','刊登文本'),
    ('Update for readers','讀者須知'),
    ('Operational circular','工作通告'),
    ('Information sheet','資料單張'),
    ('Current instructions','現行指引'),
    ('Notice extract','通告節錄'),
]
rows = []
used = Counter()
schedule = []
for (domain,tier,source,status), quota in sorted(quotas.items()):
    families = groups[domain,tier]
    for i in range(quota):
        schedule.append((domain,tier,source,status,families[i % len(families)]))
rng.shuffle(schedule)
for domain,tier,source,status,scenario in schedule:
    family, topic, en_pattern, zh_pattern, values = scenario
    count = used[family]
    used[family] += 1
    original = count % len(values)
    alternative = (original + 1 + count // len(values) % (len(values)-1)) % len(values)
    en_value = values[alternative if status=='issue' and source=='zh' else original][0]
    zh_value = values[alternative if status=='issue' and source=='en' else original][1]
    en_body = en_pattern.format(a=en_value)
    zh_body = zh_pattern.format(a=zh_value)
    en_title,zh_title = contexts[count % len(contexts)]
    reference = f'S{family:02d}-{count+1:03d}'
    layouts = [
        (f'{en_title} ({reference})\n{en_body}', f'{zh_title}（{reference}）\n{zh_body}'),
        (f'{en_body}\nPublication reference: {reference}', f'{zh_body}\n刊登編號：{reference}'),
        (f'[{reference}] {en_body}', f'【{reference}】{zh_body}'),
        (f'{en_title}\n{en_body}\n[{reference}]', f'{zh_title}\n{zh_body}\n【{reference}】'),
    ]
    en,zh = layouts[count % len(layouts)]
    reason = (f'{topic}: English specifies {en_value!r}; Chinese specifies {zh_value!r}.'
              if status=='issue' else f'{topic}: Both versions convey the same value, {en_value!r} / {zh_value!r}.')
    rows.append(dict(family_id=f'fresh-{family:02d}',split='holdout',domain=domain,
                     topic=topic,difficulty=tier,source_language=source,english=en,chinese=zh,
                     expected_status=status,english_evidence=en_value,chinese_evidence=zh_value,
                     expected_issue_or_clean_rationale=reason,severity='material' if status=='issue' else 'none'))
rng.shuffle(rows)
rows = [dict(case_id=f'J{i:04d}', **row) for i,row in enumerate(rows,1)]
assert len(rows)==1000
assert Counter(tuple(r[k] for k in keys) for r in rows)==quotas
for lang in ('english','chinese'):
    assert len({r[lang] for r in rows})==1000
    for previous in (old,read(root/'benchmark_500/formal_bilingual_benchmark_500.csv')):
        assert not ({r[lang] for r in rows}&{r[lang] for r in previous})

with (out/'v9_unseen_1000.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer = csv.DictWriter(f,fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

raw = (out/'v9_unseen_1000.csv').read_bytes()
digest = hashlib.sha256(raw).hexdigest()
prior = (root/'candidate_v9/colab_run.py').read_text()
header = prior[:prior.index("baseline=make_checker")]
b64 = base64.b64encode(zlib.compress(raw,9)).decode()
header = re.sub(r"(?m)^raw=.*$",f"raw=zlib.decompress(base64.b64decode('{b64}'))",header)
header = re.sub(r"(?m)^assert hashlib.sha256\(raw\).*$",f"assert hashlib.sha256(raw).hexdigest()=='{digest}'",header)
header = header.replace('# V9 development comparison: reused 1000-case dataset.','# Frozen V9 on 1,000 unseen synthetic notices.').replace('# Frozen V8 and revised V9 run fresh with identical loaded model objects and thresholds.','')
runner = header + (out/'run_tail.py').read_text()
(out/'colab_run.py').write_text(runner)
book = dict(nbformat=4,nbformat_minor=5,metadata=dict(accelerator='GPU',kernelspec=dict(name='python3',display_name='Python 3')),cells=[dict(id='v9holdout',cell_type='code',metadata={},source=runner.splitlines(True),execution_count=None,outputs=[])])
(out/'V9_unseen_1000.ipynb').write_text(json.dumps(book,ensure_ascii=False))
print(digest, len(used), Counter(r['difficulty'] for r in rows))
