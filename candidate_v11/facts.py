"""Small, context-independent bilingual facts. Never compare bare negation counts.

Only a uniquely resolved property in BOTH passages can establish a conflict.
These are checks, not a claim of exhaustive linguistic coverage.
"""
import re
import unicodedata
from collections import defaultdict
from decimal import Decimal


def normal(text):
    return unicodedata.normalize('NFKC', text).replace('’', "'").strip()

CN = dict(zip('零〇○一二兩三四五六七八九', [0,0,0,1,2,2,3,4,5,6,7,8,9]))
NU = {'十':10, '百':100, '千':1000, '萬':10000}
NUM = r'(?:\d+(?:[,.]\d+)*|[零〇○一二兩三四五六七八九十百千萬]+)'
ENNUM = dict(zip('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split(),range(21)))

def number(s):
    s=s.lower().replace(',','')
    if s in ENNUM:return Decimal(ENNUM[s])
    if re.fullmatch(r'\d+(?:\.\d+)?',s):return Decimal(s)
    if all(x in CN for x in s):return Decimal(''.join(str(CN[x]) for x in s))
    total=cur=section=0
    for x in s:
        if x in CN:cur=CN[x]
        elif x in NU:
            if NU[x]==10000:total+=(section+cur)*10000;section=cur=0
            else:section+=(cur or 1)*NU[x];cur=0
        else:raise ValueError(s)
    return Decimal(total+section+cur)

# Closed-value concepts; word-level boundaries avoid e.g. 'red' inside 'required'.
CONCEPTS = {
 'colour': [('red',r'red',r'紅色'),('blue',r'blue',r'藍色'),('green',r'green',r'綠色'),('yellow',r'yellow',r'黃色'),('black',r'black',r'黑色'),('white',r'white',r'白色'),('orange',r'orange',r'橙色'),('purple',r'purple',r'紫色')],
 'language': [('English',r'English',r'英文|英語'),('Chinese',r'Chinese',r'中文|漢語'),('Cantonese',r'Cantonese',r'粵語|廣東話'),('Mandarin',r'Mandarin|Putonghua',r'普通話|國語'),('Japanese',r'Japanese',r'日文|日語'),('Korean',r'Korean',r'韓文|韓語'),('French',r'French',r'法文|法語'),('Spanish',r'Spanish',r'西班牙文|西班牙語')],
 'orientation': [('portrait',r'portrait',r'直向|縱向'),('landscape',r'landscape',r'橫向')],
 'material': [('glass',r'glass',r'玻璃'),('plastic',r'plastic',r'塑膠|塑料|膠樽'),('metal',r'metal',r'金屬'),('aluminium',r'alumin(?:ium|um)',r'鋁'),('wood',r'wood(?:en)?',r'木製|木材'),('paper',r'paper',r'紙製|紙張')],
 'file format': [(x, x, x) for x in ['PDF','CSV','DOCX','XLSX','JPEG','PNG','ZIP']],
 'weekday': [(e,e+r's?',r'(?:星期|週|周)'+z) for e,z in zip(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],['一','二','三','四','五','六','[日天]'])],
 'frequency': [('daily',r'daily|every day',r'每日|每天'),('weekly',r'weekly|every week',r'每週|每星期|每周'),('monthly',r'monthly|every month',r'每月'),('quarterly',r'quarterly|every three months',r'每季|每三個月'),('yearly',r'yearly|annually|annual|every year',r'每年|一年一度')],
 'document form': [('original',r'original(?:s)?',r'正本|原件'),('copy',r'cop(?:y|ies)|photocop(?:y|ies)',r'副本|影印本')],
}

def evidence(category, z, e):
    return dict(category=category,chinese_value=str(z[0]),english_value=str(e[0]),chinese_span=z[1],english_span=e[1])

def unique(hits):
    values={x[0] for x in hits}
    return hits[0] if len(values)==1 else None


def concept_facts(text, lang):
    found={}
    for category, entries in CONCEPTS.items():
        hits=[]
        for value,ep,zp in entries:
            pat=r'\b(?:'+ep+r')\b' if lang=='en' else zp
            hits.extend((value,m[0]) for m in re.finditer(pat,text,re.I))
        f=unique(hits)
        if f:found[category]=f
    return found

# Quantity units include a dimension and conversion multiplier. Correct changes
# such as 1 m / 100 cm are equivalent; percentages in 百分比 are not the number 100.
UNITS=[
 ('length','1',r'm(?:etre|eter)s?|m',r'米|公尺'),
 ('length','.01',r'centim(?:etre|eter)s?|cm',r'厘米|公分'),
 ('length','.001',r'millim(?:etre|eter)s?|mm',r'毫米'),
 ('length','1000',r'kilom(?:etre|eter)s?|km',r'公里|千米'),
 ('mass','1',r'kilograms?|kg',r'公斤|千克'),('mass','.001',r'grams?|g',r'克|公克'),
 ('duration','1',r'minutes?|mins?',r'分鐘'),('duration','60',r'hours?|hrs?',r'小時'),
 ('days','1',r'days?',r'天|日'),('weeks','1',r'weeks?',r'星期|週|周'),
 ('age','1',r'years? old|years? of age',r'歲'),
 ('amount HKD','1',r'HKD|HK dollars?|Hong Kong dollars?',r'港元'),
 ('percentage','1',r'%|percent|per cent',r'%|巴仙'),
 ('pages','1',r'pages?',r'頁'),('floors','1',r'floors?',r'樓'),
 ('occurrences','1',r'times?',r'次'),
 ('count','1',r'people|persons?|pupils?|students?|participants?|copies|items?|forms?',r'人|名|個|份'),
]
MONTHS={x:i+1 for i,x in enumerate('January February March April May June July August September October November December'.split())}

def quantity_facts(text, lang):
    result=defaultdict(list)
    t=normal(text)
    num=NUM if lang=='zh' else r'(?:\d+(?:[,.]\d+)*|'+ '|'.join(ENNUM)+r')'
    for dimension,mult,ep,zp in UNITS:
        pat=(rf'({num})\s*(?:{zp})(?![a-z])' if lang=='zh' else rf'\b({num})\s*(?:{ep})(?![a-z])')
        for m in re.finditer(pat,t,re.I):
            # 二次 / 一般 / 百分比 cannot be mistaken for numeric quantities.
            result[dimension].append((str(number(m[1])*Decimal(mult)),m[0]))
    if lang=='en':
        for m in re.finditer(r'\bHK\$\s*(\d+(?:[,.]\d+)*)',t,re.I):result['amount HKD'].append((str(number(m[1])),m[0]))
        for m in re.finditer(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+('+'|'.join(MONTHS)+r')\b',t,re.I):result['date'].append((f'{MONTHS[m[2].title()]}-{int(m[1])}',m[0]))
        for m in re.finditer(r'\b('+'|'.join(MONTHS)+r')\s+(\d{1,2})(?:st|nd|rd|th)?\b',t,re.I):result['date'].append((f'{MONTHS[m[1].title()]}-{int(m[2])}',m[0]))
    else:
        for m in re.finditer(rf'({NUM})月({NUM})[日號]',t):result['date'].append((f'{number(m[1])}-{number(m[2])}',m[0]))
        # Dates are not durations. A date's 日 is removed from day quantities.
        result['days']=[q for q in result['days'] if not re.search(r'月'+re.escape(q[1]),t)]
    # Decimals are canonicalised for equality after SI conversion.
    for category, hits in result.items():
        if category!='date':result[category]=[(str(Decimal(v).normalize()),s) for v,s in hits]
    return dict(result)


def direct_evidence(chinese, english):
    z,e=normal(chinese),normal(english)
    out=[]
    for extractor in (concept_facts,quantity_facts):
        zf,ef=extractor(z,'zh'),extractor(e,'en')
        for category in sorted(zf.keys() & ef.keys()):
            a,b=zf[category],ef[category]
            if extractor==quantity_facts:
                # Sets of values cannot assign semantic roles; defer repeated
                # distinct quantities to contextual inference rather than guess.
                a,b=unique(a),unique(b)
            if a and b and a[0]!=b[0]:out.append(evidence(category,a,b))
    for category,pattern in [
        ('email address',r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}'),
        ('URL destination',r'https?://[^\s<>，。；）」]+'),
        ('reference identifier',r'(?<![A-Za-z\d])[A-Z]{1,5}[-/]\d{2,}(?:[-/]\d+)?')]:
        zs=[(m[0].rstrip('.,;)'),m[0]) for m in re.finditer(pattern,z)]
        es=[(m[0].rstrip('.,;)'),m[0]) for m in re.finditer(pattern,e)]
        a,b=unique(zs),unique(es)
        if a and b and a[0]!=b[0]:out.append(evidence(category,a,b))
    zc,ec=clock_facts(z,'zh'),clock_facts(e,'en')
    a,b=unique(zc),unique(ec)
    if a and b and a[0]!=b[0]:out.append(evidence('clock time',a,b))
    out.extend(boundary_evidence(z,e))
    out.extend(modality_evidence(z,e))
    return out


def boundary_evidence(z,e):
    out=[]
    # Position words only when used spatially, not the past tense of leave.
    en_directions=[(v,r'(?:(?:to|towards?|points?|pointing|facing|turn)\s+(?:the\s+)?'+pat+r'|'+pat+r'[- ]hand)') for v,pat in [('left','left'),('right','right'),('up','upwards?|up'),('down','downwards?|down')]]
    zh_directions=[('left',r'左(?:方|側|邊)'),('right',r'右(?:方|側|邊)'),('up',r'上(?:方|側|邊)'),('down',r'下(?:方|側|邊)')]
    zh=unique([(v,m[0]) for v,p in zh_directions for m in re.finditer(p,z)])
    en=unique([(v,m[0]) for v,p in en_directions for m in re.finditer(p,e,re.I)])
    if zh and en and zh[0]!=en[0]:out.append(evidence('spatial direction',zh,en))
    # Unit-only instructions can change even when there is no numeric value.
    for dim in ['length','mass']:
        zs=[];es=[]
        for d,mult,ep,zp in UNITS:
            if d!=dim:continue
            zs.extend((mult,m[0]) for m in re.finditer(r'(?:以|用|單位[為是:：])(?:'+zp+r')',z))
            es.extend((mult,m[0]) for m in re.finditer(r'\b(?:in|using)\s+(?:'+ep+r')\b',e,re.I))
        a,b=unique(zs),unique(es)
        if a and b and a[0]!=b[0]:out.append(evidence(dim+' unit',a,b))
    # Inclusive / exclusive boundaries must refer to the same explicit value.
    zn=NUM;en=r'\d+(?:\.\d+)?'
    zhpatterns=[('>=',rf'不少於({zn})|最少({zn})|({zn})(?:歲)?或以上'),('>',rf'超過({zn})|高於({zn})'),('<=',rf'不多於({zn})|最多({zn})|({zn})(?:歲)?或以下'),('<',rf'少於({zn})|未滿({zn})|低於({zn})')]
    enpatterns=[('>=',rf'\bat least ({en})|\b({en})(?: years?)? or (?:more|over|above)'),('>',rf'\bmore than ({en})|\babove ({en})'),('<=',rf'\bat most ({en})|\bno more than ({en})|\b({en})(?: years?)? or (?:less|under|below)'),('<',rf'\bless than ({en})|\bunder ({en})|\bbelow ({en})')]
    def limits(ps,t):
        found=[]
        for op,pat in ps:
            for m in re.finditer(pat,t,re.I):found.append(((op,str(number(next(g for g in m.groups() if g)))),m[0]))
        return unique(found)
    a,b=limits(zhpatterns,z),limits(enpatterns,e)
    if a and b and a[0][1]==b[0][1] and a[0][0]!=b[0][0]:out.append(evidence('inclusive/exclusive boundary',a,b))
    return out

# Optional versus required is material even when neither side is a logical
# contradiction. Only attach an explicit modal immediately before a shared action.
ACTIONS = {
 'submit': (r'submit|lodge|hand in',r'提交|遞交|交回'),
 'bring': (r'bring',r'攜帶|攜同|帶備|帶同'),
 'show': (r'show|present|produce',r'出示'),
 'pay': (r'pay',r'繳付|支付|繳交'),
 'register': (r'register|enrol|enroll',r'登記|報名'),
 'attend': (r'attend',r'出席'),
 'upload': (r'upload',r'上載|上傳'),
 'sign': (r'sign',r'簽署'),
 'retain': (r'keep|retain',r'保留'),
 'collect': (r'collect',r'領取|取件'),
 'reply': (r'reply|respond',r'回覆|回復'),
 'send': (r'send|forward',r'發送|寄送'),
 'use': (r'use',r'使用'),
 'enter': (r'enter',r'進入'),
 'cancel': (r'cancel',r'取消'),
 'replace': (r'replace',r'更換|取代'),
}

def modality_evidence(z,e):
    # Unresolved conditional scope is left to contextual inference, not reduced
    # to a document-wide bag of obligation tokens.
    if re.search(r'\b(?:if|unless|only|except|whether)\b',e,re.I) or re.search(r'如|若|除非|只有|僅|才|除外',z):return []
    out=[]
    em=[('optional',r'(?:need not|do(?:es)? not (?:need|have) to|(?:is|are) not required to)\s*$'),
        ('prohibited',r'(?:must not|may not|cannot|can\x27t|(?:is|are) not allowed to)\s*$'),
        ('required',r'(?<!not )(?:must|need to|have to|has to|(?:is|are) required to)\s*$'),
        ('permitted',r'(?:may|can|(?:is|are) allowed to)\s*$')]
    zm=[('optional',r'(?:無須|毋須|不必|不用)\s*$'),('prohibited',r'(?:不得|不可|禁止|不准)\s*$'),
        ('required',r'(?<![毋無不])(?:必須|須)\s*$'),('permitted',r'(?<![不])(?:可以|可)\s*$')]
    def fact(t,ap,patterns,lang):
        actions=list(re.finditer(r'\b(?:'+ap+r')\b' if lang=='en' else ap,t,re.I))
        if len(actions)!=1:return None
        a=actions[0];prefix=t[max(0,a.start()-60):a.start()]
        for value,pat in patterns:
            m=re.search(pat,prefix,re.I)
            if m:return value,m[0]+a[0]
        return None
    for name,(ep,zp) in ACTIONS.items():
        a,b=fact(z,zp,zm,'zh'),fact(e,ep,em,'en')
        # Optional vs permitted can be equivalent; neither establishes an obligation.
        if a and b and a[0]!=b[0] and not {a[0],b[0]}<={'optional','permitted'}:
            out.append(evidence('obligation to '+name,a,b))
    return out


def clock_facts(text,lang):
    found=[];occupied=[]
    if lang=='en':
        for m in re.finditer(r'\b(\d{1,2})(?:[:.](\d{2}))?\s*([ap])\.?m\.?',text,re.I):
            h,mn=int(m[1]),int(m[2] or 0)
            if 1<=h<=12 and mn<60:
                found.append((str((h%12+(12 if m[3].lower()=='p' else 0))*60+mn),m[0]));occupied.append(m.span())
        for val,p in [(720,r'\bnoon\b'),(0,r'\bmidnight\b')]:
            found.extend((str(val),m[0]) for m in re.finditer(p,text,re.I))
    else:
        for m in re.finditer(rf'(上午|下午|晚上|凌晨|中午)({NUM})(?:時|點|:)(?:({NUM})分?)?',text):
            h,mn=int(number(m[2])),int(number(m[3])) if m[3] else 0
            if 0<=h<=12 and mn<60:
                found.append((str((h%12+(12 if m[1] in ['下午','晚上','中午'] else 0))*60+mn),m[0]));occupied.append(m.span())
        for val,p in [(720,r'正午'),(0,r'午夜')]:found.extend((str(val),m[0]) for m in re.finditer(p,text))
    for m in re.finditer(r'(?<!\d)(\d{1,2}):(\d{2})(?!\d)',text):
        if any(m.start()<b and m.end()>a for a,b in occupied):continue
        h,mn=int(m[1]),int(m[2])
        if h<24 and mn<60:found.append((str(h*60+mn),m[0]))
    return found
