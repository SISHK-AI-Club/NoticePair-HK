"""Bounded lexical normalisation adapted from teammate V5.

Frequency and destination information are retained for explicit comparison.
Install after the V4 rule and model definitions in a fresh namespace.
"""
import re
import unicodedata
from urllib.parse import urlsplit, parse_qsl, urlencode

EN_ORDINALS = {'third':3, 'fourth':4, 'fifth':5, 'sixth':6, 'seventh':7,
               'eighth':8, 'ninth':9, 'tenth':10}
URL_RE = re.compile(r'(?<![a-z0-9_@.])(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?::\d+)?(?:/[^\s<>"「」『』，。；！？）)]*)?', re.I)
LOCALES = {'en','tc','sc','zh','zh-hk','zh-tw','zh-cn','en-hk','en-us','en-gb'}

def notice_urls(text):
    return [m.group(0).rstrip('.,;:!?') for m in URL_RE.finditer(unicodedata.normalize('NFKC', text))]

def canonical_url(value):
    u = urlsplit(value if '://' in value else 'https://'+value)
    parts = u.path.split('/')
    if len(parts)>1 and parts[1].lower() in LOCALES:
        parts.pop(1)
    query = [(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True)
             if not (k.lower() in {'lang','locale','language'} and v.lower() in LOCALES)]
    # Path, content identifiers and non-language query values remain significant.
    return (u.netloc.lower(), '/'.join(parts).rstrip('/'), urlencode(sorted(query)), u.fragment)

def without_urls(text):
    return URL_RE.sub('', text)

def link_evidence(zh,en):
    z,e=notice_urls(zh),notice_urls(en)
    if z and e and {canonical_url(x) for x in z}!={canonical_url(x) for x in e}:
        return [{'category':'link destination', 'chinese_value':str([canonical_url(x) for x in z]),
                 'english_value':str([canonical_url(x) for x in e]),
                 'chinese_span':' | '.join(z),'english_span':' | '.join(e)}]
    return []

def frequency_facts(text,lang):
    t=unicodedata.normalize('NFKC',text).lower()
    found=[]
    if lang=='zh':
        for m in re.finditer(r'([一兩二三四\d]+)年一度|每([一兩二三四\d]+)年',t):
            found.append((cn_to_int(m.group(1) or m.group(2)),m.group(0)))
        for m in re.finditer(r'每年|一年一度',t):found.append((1,m.group(0)))
    else:
        names={'annual':1,'annually':1,'yearly':1,'biennial':2,'biennially':2,
               'triennial':3,'triennially':3,'quadrennial':4,'quadrennially':4}
        for m in re.finditer(r'\b(?:'+ '|'.join(names) +r')\b',t):found.append((names[m.group()],m.group()))
        for m in re.finditer(r'\bevery (one|two|three|four|\d+) years?\b',t):
            value={'one':1,'two':2,'three':3,'four':4}.get(m.group(1))
            found.append((int(m.group(1)) if value is None else value,m.group()))
        for m in re.finditer(r'\bevery other year\b',t):found.append((2,m.group()))
    values={v for v,_ in found}
    return {'value':next(iter(values)),'span':found[0][1]} if len(values)==1 else None

def frequency_evidence(zh,en):
    z,e=frequency_facts(zh,'zh'),frequency_facts(en,'en')
    if z and e and z['value']!=e['value']:
        return [{'category':'event frequency (years between occurrences)',
                 'chinese_value':z['value'],'english_value':e['value'],
                 'chinese_span':z['span'],'english_span':e['span']}]
    return []

def lexical_text(text,lang):
    t=unicodedata.normalize('NFKC',text)
    if lang=='zh':
        t=re.sub(r'([一兩二三四\d]+)年一度|每([一兩二三四\d]+)年',
                 lambda m:f"每{cn_to_int(m.group(1) or m.group(2))}年",t)
        t=re.sub(r'每年', '每1年',t)
        t=re.sub(r'半費|半價','50%',t)
    else:
        freq={'annual':1,'annually':1,'yearly':1,'biennial':2,'biennially':2,
              'triennial':3,'triennially':3,'quadrennial':4,'quadrennially':4}
        t=re.sub(r'\b(?:'+ '|'.join(freq) +r')\b',lambda m:f"every {freq[m.group().lower()]} years",t,flags=re.I)
        t=re.sub(r'\bevery other year\b','every 2 years',t,flags=re.I)
        t=re.sub(r'\bevery (one|two|three|four) years?\b',
                 lambda m:f"every {dict(one=1,two=2,three=3,four=4)[m.group(1).lower()]} years",t,flags=re.I)
        t=re.sub(r'\bfutsal\b','5-a-side football',t,flags=re.I)
        t=re.sub(r'\bhalf[- ]price\b|\bhalf (?:the )?(?:normal |usual |standard )?(?:price|fee|fare)\b','50 percent',t,flags=re.I)
    return t

_merge_base_numbers_zh = getattr(numbers_zh, '_merge_original', numbers_zh)
_merge_base_numbers_en = getattr(numbers_en, '_merge_original', numbers_en)
_merge_base_negation_pair = getattr(negation_pair, '_merge_original', negation_pair)
_merge_base_similarity = getattr(similarity, '_merge_original', similarity)
_merge_base_contradiction = getattr(contradiction, '_merge_original', contradiction)

def numbers_zh(text):
    return _merge_base_numbers_zh(lexical_text(without_urls(text),'zh'))

def numbers_en(text):
    t=lexical_text(without_urls(text),'en')
    nums=_merge_base_numbers_en(t)
    nums|={v for k,v in EN_ORDINALS.items() if re.search(rf'\b{k}\b',t,re.I)}
    if re.search(r'\bfirst (?:quarter|floor|day|month|year)\b',t,re.I):nums.add(1)
    return nums

def negation_pair(zh,en):
    return _merge_base_negation_pair(re.sub(r'組別|識別|辨別','',zh),en)

def model_text(text,lang):
    return lexical_text(without_urls(normalise_text(text,lang)),lang).strip()

def similarity(zh,en):
    z,e=model_text(zh,'zh'),model_text(en,'en')
    return 1.0 if not z and not e else _merge_base_similarity(z,e)

def contradiction(zh,en):
    z,e=model_text(zh,'zh'),model_text(en,'en')
    return 0.0 if not z and not e else _merge_base_contradiction(z,e)

def ambiguity_evidence(zh,en):
    return frequency_evidence(zh,en)+link_evidence(zh,en)

# Re-running this cell must not wrap a wrapper and recurse indefinitely.
for _wrapped, _original in [(numbers_zh, _merge_base_numbers_zh),
                            (numbers_en, _merge_base_numbers_en),
                            (negation_pair, _merge_base_negation_pair),
                            (similarity, _merge_base_similarity),
                            (contradiction, _merge_base_contradiction)]:
    _wrapped._merge_original = _original
