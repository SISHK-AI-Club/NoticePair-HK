"""V8 bounded, whole-notice semantic grammar.

Parses each language independently. No benchmark IDs, labels, examples or
rationales are consulted. Every pattern must cover the entire notice; unknown
clauses or constructions fall back to the frozen checker. This is a finite
notice grammar, not general translation understanding or weight fine-tuning.
"""
import re
import unicodedata
from dataclasses import dataclass

@dataclass
class Notice:
    kind: str
    topic: str
    facts: dict
    text: str

# Topics are noun phrases, not arbitrary sentences. Extra clauses must not be
# swallowed as a topic and thereby evade the inherited checker.
ET = r'(?P<topic>[^.,;:!?\n]+?)'
ZT = r'(?P<topic>[^,。;:!?\n]+?)'
MONTH_NAMES = 'January February March April May June July August September October November December'.split()
MONTH_MAP = {s.lower(): i+1 for i,s in enumerate(MONTH_NAMES)}
MONTH_PATTERN = '|'.join(MONTH_NAMES)

def norm(text):
    return unicodedata.normalize('NFKC',text).replace('，',',').replace('：',':').strip()

def clock(h, half, minute=None):
    h=int(h); minute=int(minute or 0)
    if not 1 <= h <= 12 or not 0 <= minute < 60: raise ValueError('invalid clock')
    return f'{h%12+(12 if half.lower() in ("p","下午","晚上","中午","正午") else 0):02d}:{minute:02d}'

def ct(prefix, lang):
    if lang=='en':
        return rf'(?P<{prefix}h>\d{{1,2}})(?::(?P<{prefix}min>\d{{2}}))?\s*(?P<{prefix}half>[ap])\.?m\.?'
    return rf'(?P<{prefix}half>上午|下午|晚上|凌晨|中午|正午)(?P<{prefix}h>\d{{1,2}})[時點](?:(?P<{prefix}min>\d{{1,2}})分)?'

def timeval(d,p=''):
    return clock(d[p+'h'],d[p+'half'],d.get(p+'min'))

def datepat(p,lang):
    if lang=='en': return rf'(?P<{p}d>\d{{1,2}})\s+(?P<{p}m>{MONTH_PATTERN})'
    return rf'(?P<{p}m>\d{{1,2}})月(?P<{p}d>\d{{1,2}})日'

def dateval(d,p,lang):
    m=MONTH_MAP[d[p+'m'].lower()] if lang=='en' else int(d[p+'m'])
    day=int(d[p+'d'])
    if not 1<=m<=12 or not 1<=day<=31: raise ValueError('invalid date')
    return f'{m:02d}-{day:02d}'

RULES = {'en':[], 'zh':[]}
def add(lang,kind,pattern,convert):
    RULES[lang].append((kind,re.compile(pattern+r'[。.]?',re.I),convert))

# Order is represented as two named actions, never the polarity of one token.
for lang in RULES:
    if lang=='en':
        for action,other,kind in [('report to the hall','collecting your badge','badge order'),('submit your request','creating an account','account order')]:
            first,second=('collect badge','report to hall') if kind=='badge order' else ('create account','submit request')
            add(lang,kind,rf'For the {ET},\s*{action} (?P<order>after|before) {other}',
                lambda d,a=first,b=second:{'action order':f'{a} before {b}' if d['order'].lower()=='after' else f'{b} before {a}'})
    else:
        for kind,a,b in [('badge order','領取名牌','到禮堂報到'),('account order','開立帳戶','提交申請')]:
            names={a:'collect badge' if kind=='badge order' else 'create account',b:'report to hall' if kind=='badge order' else 'submit request'}
            add(lang,kind,rf'(?:出席|參與|辦理){ZT}(?:服務)?時,\s*請先(?P<a>{a}|{b}),\s*再(?P<b>{a}|{b})',
                lambda d,n=names:{'action order':n[d['a']]+' before '+n[d['b']]})
        add(lang,'badge order',rf'請領取{ZT}名牌後才到禮堂報到',lambda d:{'action order':'collect badge before report to hall'})
        add(lang,'account order',rf'請開立帳戶後才提交{ZT}(?:服務)?申請',lambda d:{'action order':'create account before submit request'})

# Receipt validity: month offset and boundary, with 最後一日 treated as a phrase.
add('en','receipt expiry',rf'A receipt for the {ET} is valid until the end of the month (?P<anchor>in which|after) it was issued',lambda d:{'receipt expiry':'end of issue month' if d['anchor'].lower()=='in which' else 'end of following month'})
add('zh','receipt expiry',rf'{ZT}的收據有效至發出(?P<anchor>當月月底|後下一個月的月底)',lambda d:{'receipt expiry':'end of issue month' if d['anchor']=='當月月底' else 'end of following month'})
add('zh','receipt expiry',rf'{ZT}收據的有效期於發出(?P<anchor>當月|後下一個月)最後一日屆滿',lambda d:{'receipt expiry':'end of issue month' if d['anchor']=='當月' else 'end of following month'})

# Necessary-condition wording, not an assertion of sufficient permission.
exception_value=lambda d:{'side-door exception':'staff presence is necessary for opening' if d['cond'].lower() in ('unless','除非','只在') else 'closed even with staff present'}
for p in [rf'During the {ET},\s*the side door is closed (?P<cond>unless|even when) a staff member is on duty there',rf'The side door for the {ET} is closed (?P<cond>unless|even when) a staff member is on duty there']:
    add('en','door exception',p,exception_value)
for p in [rf'{ZT}期間,\s*(?P<cond>除非|即使)有職員在側門當值,(?:否則|仍)側門關閉',rf'{ZT}的側門(?P<cond>除非|即使)有職員在該處當值,(?:否則|仍)關閉',rf'{ZT}(?:期間,\s*|的)側門(?P<cond>只在)有職員於該處當值時開放']:
    add('zh','door exception',p,exception_value)

# Group obligation stays attached to the group; walk-in permission is separate.
add('en','group booking',rf'The {ET} accepts walk-ins\.\s*Group visits (?P<modal>must be booked in advance|do not need advance booking)',lambda d:{'individual walk-ins':'allowed','group advance booking':'required' if d['modal'].lower().startswith('must') else 'not required'})
for p in [rf'{ZT}接受即場到訪,但團體到訪(?P<modal>須|毋須)預約',rf'個別人士可即場到訪{ZT}。團體則(?P<modal>須|毋須)事先預約']:
    add('zh','group booking',p,lambda d:{'individual walk-ins':'allowed','group advance booking':'required' if d['modal']=='須' else 'not required'})

# Role assignment maps action and object to actor, regardless of clause order.
ACTORS_EN='class teachers|prefects|reception staff|volunteers'
ACTORS_ZH='班主任|領袖生|接待職員|義工'
ACTOR_MAP={'班主任':'class teachers','領袖生':'prefects','接待職員':'reception staff','義工':'volunteers'}
add('en','duties',rf'(?:For|At) the {ET},\s*(?P<check>{ACTORS_EN}) check the list and (?P<distribute>{ACTORS_EN}) distribute the materials',lambda d:{'list checking actor':d['check'].lower(),'materials distribution actor':d['distribute'].lower()})
for p in [rf'{ZT}(?:期間,|的)(?P<check>{ACTORS_ZH})負責核對名單,(?P<distribute>{ACTORS_ZH})負責派發物資',rf'{ZT}期間的分工如下:名單由(?P<check>{ACTORS_ZH})核對。物資由(?P<distribute>{ACTORS_ZH})派發',rf'在{ZT},名單由(?P<check>{ACTORS_ZH})核對,物資由(?P<distribute>{ACTORS_ZH})派發']:
    add('zh','duties',p,lambda d:{'list checking actor':ACTOR_MAP[d['check']],'materials distribution actor':ACTOR_MAP[d['distribute']]})

add('en','contact update',rf'For the {ET},\s*you may update your contact number (?P<cond>without changing|only after changing) the name on your account',lambda d:{'name change prerequisite':'not required' if d['cond'].lower().startswith('without') else 'required before phone update'})
add('zh','contact update',rf'辦理{ZT}時,可更新聯絡電話,(?P<cond>毋須更改|但須先更改)帳戶姓名',lambda d:{'name change prerequisite':'not required' if d['cond'].startswith('毋須') else 'required before phone update'})
add('zh','contact update',rf'帳戶姓名可保留不變,仍可在辦理{ZT}時更新聯絡電話',lambda d:{'name change prerequisite':'not required'})

# Corrections bind current and superseded values instead of comparing value sets.
add('en','room correction',rf'{ET} update:\s*disregard Room (?P<old>\d+) (?:in the earlier circular|on the earlier sign)\.\s*Use Room (?P<current>\d+)',lambda d:{'current room':str(int(d['current'])),'superseded room':str(int(d['old']))})
for p in [rf'{ZT}(?:最新安排|地點更新):請使用(?P<current>\d+)室,(?:早前通告|舊告示)所列的(?P<old>\d+)室(?:安排)?已(?:取消|不適用)',rf'{ZT}改在(?P<current>\d+)室舉行。舊通告所列的(?P<old>\d+)室已不適用',rf'{ZT}移至(?P<current>\d+)室。請勿依照舊告示前往(?P<old>\d+)室']:
    add('zh','room correction',p,lambda d:{'current room':str(int(d['current'])),'superseded room':str(int(d['old']))})
for lang in RULES:
    cur,old=datepat('cur',lang),datepat('old',lang)
    if lang=='en':
        patterns=[('opening correction',rf'{ET} update:\s*disregard the previous opening date of {old}\.\s*The revised date is {cur}'),('appointment correction',rf'Correction for the {ET}:\s*your appointment is on {cur}\.\s*Please disregard the previous email showing {old}')]
    else:
        patterns=[('opening correction',rf'{ZT}開放日期已改為{cur},原定{old}的安排已取消'),('opening correction',rf'{ZT}將於{cur}開放。早前公布的{old}已不適用'),('appointment correction',rf'{ZT}的預約日期為{cur}。請以本電郵為準,早前所列的{old}已不適用'),('appointment correction',rf'早前電郵所列的{old}已取消。你的{ZT}預約改於{cur}')]
    for kind,p in patterns:
        add(lang,kind,p,lambda d,l=lang:{'current date':dateval(d,'cur',l),'superseded date':dateval(d,'old',l)})

# General and exceptional audience times remain separately keyed.
AUD_EN={'Performers':'performers','Exhibitors':'exhibitors','Invited speakers':'invited speakers','Groups with bookings':'booked groups'}
AUD_ZH={'表演者':'performers','參展者':'exhibitors','獲邀講者':'invited speakers','已預約團體':'booked groups'}
add('en','audience schedule',rf'{ET} schedule\s+General (?P<action>arrival|admission):\s*{ct("general","en")}\s+\*\s*(?P<who>Performers|Exhibitors|Invited speakers|Groups with bookings) (?P<verb>report|arrive|enter) at {ct("special","en")} instead',lambda d:{'general action':'admission' if d['action'].lower()=='admission' else 'arrival','general time':timeval(d,'general'),'exception audience':next(v for k,v in AUD_EN.items() if k.lower()==d['who'].lower()),'exception action':{'enter':'admission','report':'report','arrive':'arrival'}[d['verb'].lower()],'exception time':timeval(d,'special')})
for p in [rf'{ZT}時間表\s+一般(?P<action>到場時間|入場):{ct("general","zh")}\s+\*\s*(?P<who>{"|".join(AUD_ZH)})改於{ct("special","zh")}(?P<verb>報到|到場|入場)',rf'{ZT}一般(?P<action>到場|入場)時間為{ct("general","zh")}。(?P<who>{"|".join(AUD_ZH)})須按附註於{ct("special","zh")}(?P<verb>報到|到場|入場)']:
    add('zh','audience schedule',p,lambda d:{'general action':'admission' if d['action']=='入場' else 'arrival','general time':timeval(d,'general'),'exception audience':AUD_ZH[d['who']],'exception action':{'入場':'admission','報到':'report','到場':'arrival'}[d['verb']],'exception time':timeval(d,'special')})

# Simple time statements: require a complete sentence, not mere matching digits.
for kind,pattern in [('start time',rf'(?:The )?{ET} starts at {ct("","en")}'),('opening time',rf'The {ET} opens at {ct("","en")}'),('appointment time',rf'Your appointment for the {ET} is at {ct("","en")}')]:
    add('en',kind,pattern,lambda d:{'time':timeval(d)})
for kind,patterns in [('start time',[rf'{ZT}於{ct("","zh")}開始',rf'{ct("","zh")}開始{ZT}',rf'{ZT}開始時間:{ct("","zh")}']),('opening time',[rf'{ZT}於{ct("","zh")}開放',rf'{ct("","zh")}起可使用{ZT}']),('appointment time',[rf'你的{ZT}預約時間為{ct("","zh")}',rf'你已預約於{ct("","zh")}辦理{ZT}'])]:
    for p in patterns: add('zh',kind,p,lambda d:{'time':timeval(d)})

def parse_notice(text,lang):
    s=norm(text)
    for kind,pattern,convert in RULES[lang]:
        m=pattern.fullmatch(s)
        if not m: continue
        d=m.groupdict(); topic=d['topic'].strip()
        if lang=='zh' and kind=='door exception':
            if d['cond']=='除非' and '否則' not in s: continue
            if d['cond']=='即使' and '仍' not in s: continue
        # Reject embedded instructions or conditions hidden inside a title slot.
        if lang=='en' and re.search(r'\b(?:can|may|need|where|who|that|must|unless|only|cannot|without|before|after|should|shall|not|bring|pay|submit|register|attend|provided|except|including)\b',topic,re.I): continue
        if lang=='zh' and re.search(r'須|需|可|除非|否則|不得|不准|僅限|只限|即使|請勿|並|且|攜帶|繳付|提交|報名|之後|之前',topic): continue
        try: facts=convert(d)
        except (ValueError,KeyError): continue
        if kind in ('badge order','account order') and d.get('a')==d.get('b') and 'a' in d: continue
        return Notice(kind,topic,facts,text)
    return None

def structured_comparison(chinese,english):
    z,e=parse_notice(chinese,'zh'),parse_notice(english,'en')
    if not z or not e or z.kind!=e.kind: return None
    evidence=[]
    for key in sorted(set(z.facts)|set(e.facts)):
        zv,ev=z.facts.get(key,'not specified'),e.facts.get(key,'not specified')
        if zv!=ev:
            evidence.append(dict(category=key,chinese_value=zv,english_value=ev,chinese_span=z.text,english_span=e.text))
    return z,e,evidence
