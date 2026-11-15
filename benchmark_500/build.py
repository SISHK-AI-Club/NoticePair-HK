"""Generate a controlled benchmark with explicit construction families."""
import csv
import random
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
rng = random.Random(500)
events = {
    'school': [
        ('parent briefing','家長簡介會'), ('prize presentation','頒獎典禮'),
        ('student council forum','學生會論壇'), ('orientation session','迎新活動'),
        ('science exhibition','科學展覽'), ('reading workshop','閱讀工作坊'),
        ('school concert','學校音樂會'), ('career talk','升學及職業講座'),
        ('debate final','辯論決賽'), ('open day','學校開放日'),
        ('sports team briefing','校隊簡介會'), ('graduation rehearsal','畢業典禮綵排'),
    ],
    'government': [
        ('district service centre','地區服務中心'), ('public enquiry centre','公眾諮詢中心'),
        ('community exhibition centre','社區展覽中心'), ('heritage visitor centre','文物訪客中心'),
        ('municipal exhibition hall','市政展覽館'), ('civic information centre','市民資訊中心'),
        ('public resource centre','公共資源中心'), ('district cultural centre','地區文化中心'),
        ('recreation centre','康樂中心'), ('community hall','社區會堂'),
    ],
    'public_email': [
        ('membership renewal','會籍續期'), ('service consultation','服務諮詢'),
        ('venue booking','場地預訂'), ('equipment loan','器材借用'),
        ('facility tour','設施參觀'), ('community workshop','社區工作坊'),
        ('archive viewing','檔案閱覽'), ('studio induction','工作室簡介'),
        ('document collection','文件領取'), ('training session','培訓活動'),
    ],
    'instructions': [
        ('community exhibition','社區展覽'), ('volunteer briefing','義工簡介會'),
        ('book fair','書展'), ('recycling workshop','回收工作坊'),
        ('public consultation','公眾諮詢會'), ('art demonstration','藝術示範'),
        ('heritage workshop','文物工作坊'), ('community forum','社區論壇'),
        ('visitor orientation','訪客簡介會'), ('craft fair','手工藝市集'),
    ],
}
# Total and issue count by group. Half-case rounding is allocated across groups.
quotas = {
    'school': [(90,27),(45,14),(15,4)],
    'government': [(90,27),(45,13),(15,5)],
    'public_email': [(60,18),(30,9),(10,3)],
    'instructions': [(60,18),(30,9),(10,3)],
}
changes = {
    'staff_swap': (
        'reception staff check the list and volunteers distribute the materials',
        'volunteers check the list and reception staff distribute the materials',
        '接待職員負責核對名單，義工負責派發物資', '義工負責核對名單，接待職員負責派發物資',
        'The duties of reception staff and volunteers are swapped.'),
    'swap': (
        'class teachers check the list and prefects distribute the materials',
        'prefects check the list and class teachers distribute the materials',
        '班主任負責核對名單，領袖生負責派發物資', '領袖生負責核對名單，班主任負責派發物資',
        'The people responsible for checking the list and distributing materials are swapped.'),
    'exception': (
        'closed unless a staff member is on duty there', 'closed even when a staff member is on duty there',
        '除非有職員', '即使有職員',
        'The side door remains closed even when a staff member is on duty, removing the exception.'),
    'sequence': (
        'report to the hall after collecting your badge', 'report to the hall before collecting your badge',
        '先領取名牌，再到禮堂報到', '先到禮堂報到，再領取名牌',
        'The order of badge collection and reporting to the hall is reversed.'),
    'groups': (
        'Group visits must be booked in advance.', 'Group visits do not need advance booking.',
        '團體到訪須預約', '團體到訪毋須預約',
        'The advance booking requirement for groups is removed.'),
    'month': (
        'end of the month in which it was issued', 'end of the month after it was issued',
        '發出當月月底', '發出後下一個月的月底',
        'Receipt validity extends from the end of the issue month to the end of the following month.'),
    'account': (
        'submit your request after creating an account', 'submit your request before creating an account',
        '先開立帳戶，再提交申請', '先提交申請，再開立帳戶',
        'The order of account creation and request submission is reversed.'),
    'contact': (
        'without changing the name on your account', 'only after changing the name on your account',
        '毋須更改帳戶姓名', '但須先更改帳戶姓名',
        'Changing the account name becomes a prerequisite for updating the phone number.'),
}
clean_reasons = {
    'room':'Both identify room {a}.', 'hour':'Both specify the same time, {a} o’clock.',
    'day':'Both give day {a} of the stated month for the same action.',
    'counter':'Both direct readers to counter {a}.', 'desk':'Both direct readers to desk {a}.',
    'staff_swap':'Both assign list checking to reception staff and distribution to volunteers.',
    'swap':'Both assign list checking to class teachers and distribution to prefects.',
    'exception':'Both allow the side door to open only when a staff member is on duty there.',
    'sequence':'Both require collecting the badge before reporting to the hall.',
    'groups':'Both permit individual walk-ins and require groups to book.',
    'month':'Both end receipt validity at the end of the month of issue.',
    'account':'Both put account creation before request submission.',
    'contact':'Both permit changing the phone number while retaining the account name.',
    'correction':'Both supersede {b} with {a}.',
    'footnote':'Both retain general time {a} and the separate time {b} for the named group.',
}
templates = [line.split('|') for line in (root/'templates.txt').read_text().splitlines()]
def render(text, fields):
    return text.format(**fields).replace('\\n','\n')

def replace_once(text, old, new):
    assert text.count(old) == 1, (text, old)
    return text.replace(old, new, 1)

def corrupt(kind, en, zh, direction, fields):
    a,b = fields['a'], fields['b']
    if kind in changes:
        old_en,new_en,old_zh,new_zh,reason = changes[kind]
        if kind == 'exception':
            old_zh = '除非有職員' if '除非有職員' in zh else old_zh
            new_zh = '即使有職員'
            if '，否則' in zh:
                zh = zh.replace('，否則','，仍') if direction=='en' else zh
        return (en,replace_once(zh,old_zh,new_zh),reason) if direction=='en' else (replace_once(en,old_en,new_en),zh,reason)
    if kind in ('correction','footnote'):
        en = en.translate(str.maketrans({str(a):str(b),str(b):str(a)})) if direction=='zh' else en
        zh = zh.translate(str.maketrans({str(a):str(b),str(b):str(a)})) if direction=='en' else zh
        reason = f'The superseded value {b} and replacement {a} are swapped.' if kind=='correction' else f'The general time {a} and the named group’s time {b} are swapped.'
        return en,zh,reason
    reason = f'The translated {kind} changes from {a} to {b}.'
    if kind == 'day':
        return (en,replace_once(zh,f'{a}日',f'{b}日'),reason) if direction=='en' else (
            replace_once(en,f'on {a} ',f'on {b} ') if f'on {a} ' in en else replace_once(en,f'by {a} ',f'by {b} '),zh,reason)
    return (en,replace_once(zh,str(a),str(b)),reason) if direction=='en' else (replace_once(en,str(a),str(b)),zh,reason)

rows=[]
for domain, groups in quotas.items():
    for tier,(total,nissue) in zip(('routine','difficult','edge'),groups):
        pool=[t for t in templates if t[:2]==[domain,tier]]
        slots=[]
        for status,n in [('issue',nissue),('clean',total-nissue)]:
            en_count = round(n*.6)
            # Balance rounding between clean and issue when both counts end in .5.
            if status=='clean': en_count = round(total*.6)-round(nissue*.6)
            slots.extend((status,d) for d in ['en']*en_count+['zh']*(n-en_count))
        rng.shuffle(slots)
        used=set()
        for status,direction in slots:
            eligible=[]
            for template in pool:
                kind=template[-1]
                choices=events[domain]
                if domain=='public_email':
                    if template[2]=='Footnote': choices=choices[4:6]+choices[9:]
                    if template[2]=='Correction' or template[2]=='Time': choices=choices[1:]
                for event,zh_event in choices:
                    for a in (range(1,6) if domain=='government' and kind=='hour' else range(1,10) if tier!='difficult' else range(1,3)):
                        key=(template[2],event,a) if tier!='difficult' else (template[2],event)
                        if key not in used: eligible.append((key,template,event,zh_event,a))
            key,template,event,zh_event,a=rng.choice(eligible)
            used.add(key)
            _,_,topic,en_text,zh_text,alternate,kind=template
            b=rng.choice([v for v in range(1,10) if v!=a])
            if domain=='government' and kind=='hour':
                a,b = (a-1)%5+7,(b-1)%5+7
                if a==b: b=12
            fields=dict(event=event,zh=zh_event,a=a,b=b)
            if status=='clean' and (rng.random()<.6 or direction=='zh'):
                zh_text=alternate
            en,zh=render(en_text,fields),render(zh_text,fields)
            rationale=clean_reasons[kind].format(**fields)
            if status=='issue':
                en,zh,rationale=corrupt(kind,en,zh,direction,fields)
            rows.append(dict(family_id=f'{domain}-{tier}-{pool.index(template)+1}',
                split='holdout',domain=domain,topic=topic,difficulty=tier,source_language=direction,
                english=en,chinese=zh,expected_status=status,english_evidence=en,chinese_evidence=zh,
                expected_issue_or_clean_rationale=rationale,
                severity='high' if status=='issue' and kind in {'correction','footnote'} else
                    'material' if status=='issue' else 'none'))
rng.shuffle(rows)
rows=[dict(case_id=f'F{i:03}',**row) for i,row in enumerate(rows,1)]
assert len(rows)==len({(r['english'],r['chinese']) for r in rows})==500
assert Counter(r['expected_status'] for r in rows)=={'clean':350,'issue':150}
assert Counter(r['source_language'] for r in rows)=={'en':300,'zh':200}
with (root/'formal_bilingual_benchmark_500.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
with (root/'review_all_500.md').open('w',encoding='utf-8') as f:
    f.write('# Formal bilingual benchmark · 500 cases\n\n')
    for r in rows:
        f.write(f"### {r['case_id']} · {r['domain']} · {r['difficulty']} · {r['expected_status']} · source {r['source_language']}\n\n")
        f.write(f"**English**\n\n{r['english']}\n\n**Chinese**\n\n{r['chinese']}\n\n")
        f.write(f"**Rationale** · {r['expected_issue_or_clean_rationale']}\n\n")
print(Counter((r['domain'],r['difficulty'],r['expected_status']) for r in rows))
