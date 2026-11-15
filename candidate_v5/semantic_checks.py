"""Conservative evidence rules for HK bilingual notices.
No case IDs, benchmark labels or reference rationales are used.
Each rule abstains when it cannot resolve a supported feature on both sides.
This finite grammar is not a general semantic parser.
"""
import re
import unicodedata

ACTIONS = {
    'bring': (r'\bbring\b', r'攜同|攜帶|帶備|帶同'),
    'submit': (r'\bsubmit\b', r'提交|遞交|交回'),
    'upload': (r'\bupload\b', r'上載|上傳'),
    'reserve': (r'\b(?:reserve|book)\b', r'預留|預訂'),
    'reply': (r'\b(?:reply|respond)\b', r'回覆|回復'),
    'return': (r'\breturn\b', r'歸還'),
    'attend': (r'\battend\b', r'出席'),
    'pay': (r'\bpay\b', r'繳付|支付'),
    'register': (r'\bregister\b', r'報名|登記'),
}

def _norm(s):
    return unicodedata.normalize('NFKC', s).replace('’', "'")

def _hit(pattern, text):
    return re.search(pattern, text, re.I)

def _fact(value, match):
    return {'value': value, 'span': match.group(0)} if match else None

def _unique(patterns, text):
    found = [(value, m) for value, pattern in patterns for m in re.finditer(pattern, text, re.I)]
    if len({v for v, _ in found}) != 1:
        return None
    value, match = found[0]
    return _fact(value, match)

def _main_clause(text, lang):
    # Match the consequence, not a permission mentioned inside an exception.
    if lang == 'en':
        text = re.split(r'\bunless\b|\bonly if\b', text, maxsplit=1, flags=re.I)[0]
        if _hit(r'^\s*(?:if|when)\b', text) and ',' in text:
            text = text.split(',', 1)[1]
    else:
        if '否則' in text:
            text = text.split('否則', 1)[1]
        elif _hit(r'^\s*(?:如|若|假如)', text) and ',' in text:
            text = text.split(',', 1)[1]
    return text

def _modal_for_action(text, action_pattern, lang):
    actions = list(re.finditer(action_pattern, text, re.I))
    if len(actions) != 1:
        return None
    action = actions[0]
    prefix = text[:action.start()]
    prefix = re.split(r'[,;。]', prefix)[-1]
    patterns = ([("not required", r'\b(?:need not|do(?:es)? not (?:need|have) to|(?:is|are) not required to)\s*$'),
                 ("prohibited", r'\b(?:must not|cannot|can\x27t)\s*$'),
                 ("required", r'\b(?:must|need(?:s)? to|have to|has to|(?:is|are) required to)\s*$'),
                 ("permitted", r'\b(?:may|can|(?:is|are) allowed to)\s*$')]
                if lang == 'en' else
                [("not required", r'(?:毋須|無須|不必|不須)[^,。;]{0,12}$'),
                 ("prohibited", r'(?:不得|不可|禁止)[^,。;]{0,12}$'),
                 ("required", r'(?<![毋無不])(?:必須|須|必需)[^,。;]{0,12}$'),
                 ("permitted", r'(?<![不])(?:可以|可)[^,。;]{0,12}$')])
    for value, pattern in patterns:
        m = _hit(pattern, prefix)
        if m:
            return {'value': value, 'span': m.group(0) + action.group(0)}
    if lang == 'en' and _hit(r'^\s*(?:please\s+)?$', prefix):
        return {'value': 'required', 'span': text[:action.end()].strip()}
    if lang == 'zh' and _hit(r'^\s*請(?:於|在)?[^,。;]*$', prefix):
        return {'value': 'required', 'span': prefix.strip()+action.group(0)}
    return None


def semantic_evidence(chinese, english):
    """Return paired evidence for supported, non-equivalent semantic features."""
    zh, en = _norm(chinese), _norm(english)
    evidence = []
    def compare(category, z, e):
        if z and e and z['value'] != e['value']:
            evidence.append({'category': category, 'chinese_value': z['value'],
                             'english_value': e['value'], 'chinese_span': z['span'],
                             'english_span': e['span']})

    zm, em = _main_clause(zh, 'zh'), _main_clause(en, 'en')
    for action, (ep, zp) in ACTIONS.items():
        compare('obligation for '+action, _modal_for_action(zm,zp,'zh'), _modal_for_action(em,ep,'en'))

    # The approved exception is removed from both sides before comparing the
    # ordinary submission routes. An added paper option outside the exception
    # is a substantive change even when the document mentions paper elsewhere.
    if _hit(r'\bunless\b',en) and '否則' in zh and _hit(r'\bsubmit\b',em) and _hit(r'提交|遞交',zm):
        def channels(text, lang):
            patterns = [('online',r'\bonline\b'),('paper',r'\bpaper\b')] if lang=='en' else [('online',r'網上|線上'),('paper',r'紙本')]
            found = [(name,m.group(0)) for name,p in patterns for m in re.finditer(p,text,re.I)]
            return {'value': ', '.join(sorted({n for n,_ in found})), 'span': text.strip()} if found else None
        compare('submission options outside the approved exception',channels(zm,'zh'),channels(em,'en'))

    # Restricted eligibility: compare the role explicitly governed by "only".
    groups = {'members':(r'members?',r'會員'), 'volunteers':(r'volunteers?',r'義工|志願者'),
              'performers':(r'performers?',r'演出者'), 'residents':(r'residents?',r'居民')}
    eg = zg = None
    for value,(ep,zp) in groups.items():
        m = _hit(r'\bonly\s+('+ep+r')\b',en)
        if m: eg = _fact(value,m)
        m = _hit(r'(?:只有|只限)[^,。;]{0,35}(?:'+zp+r')(?=可|須|才|均|必)',zh)
        if m: zg = _fact(value,m)
    m = _hit(r'(?:所有|全體)參加者',zh)
    if m: zg = _fact('all participants',m)
    compare('eligible group',zg,eg)

    compare('day-count basis',
            _unique([('working days',r'工作[天日]'),('calendar days',r'曆日|日曆日')],zh),
            _unique([('working days',r'\b(?:working|business) days?\b'),('calendar days',r'\bcalendar days?\b')],en))
    compare('deadline starts at',
            _unique([('receipt',r'(?:收到|接獲)[^,。;]{0,20}後'),('issuance',r'(?:發出|寄出|簽發)後')],zh),
            _unique([('receipt',r'\bafter\s+(?:receiving|receipt of)\b'),('issuance',r'\bafter\s+(?:issuing|issuance of)|\b(?:issued|sent)\b[^,;]{0,12}\bafter\b')],en))

    # Explicit ordered boundary. Do not infer comparators from standalone 未/不.
    zn = r'[零〇一二兩三四五六七八九十百\d]+'
    compare('inclusive/exclusive threshold',
            _unique([('>=',zn+r'(?:號|歲)?或以上'),('>',r'高於'+zn+r'(?:號|歲)?')],zh),
            _unique([('>=',r'\b\d+(?:\s+years?)?\s+or\s+(?:higher|above|over)\b'),('>',r'\b(?:higher than|above)\s+(?:No\.\s*)?\d+\b')],en))
    # This compares a temporal direction only when the weekday anchor agrees.
    days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    zdays = '一二三四五六日'
    for idx, day in enumerate(days):
        zp = r'(?:星期|週|周|禮拜)'+zdays[idx]
        if _hit(zp,zh) and _hit(r'\b'+day+r'\b',en):
            compare('weekday deadline boundary',
                    _unique([('by',zp+r'或之前'),('after',zp+r'(?:之後|後)'),('before',zp+r'之前')],zh),
                    _unique([('by',r'\bby\s+'+day+r'\b'),('after',r'\bafter\s+'+day+r'\b'),('before',r'\bbefore\s+'+day+r'\b')],en))

    # Paired enumerations of the same supported documents: and/or changes requirements.
    documents=[(r'proof of address',r'住址證明'),(r'(?:a\s+)?student ID',r'學生證')]
    if all(_hit(ep,en) and _hit(zp,zh) for ep,zp in documents):
        compare('document combination',
                _unique([('both',r'住址證明(?:及|和|與)學生證'),('either',r'住址證明或學生證')],zh),
                _unique([('both',r'proof of address\s+and\s+(?:a\s+)?student ID'),('either',r'proof of address\s+or\s+(?:a\s+)?student ID')],en))

    compare('application limit applies per',
            _unique([('household',r'每(?:個|一個)?住戶'),('address',r'每(?:個|一個)?地址')],zh),
            _unique([('household',r'\bper household\b'),('address',r'\bper address\b')],en))
    # Compare the action's address condition. A shared-address subject plus
    # a different-address-only condition is narrower than shared-address permission.
    if _hit(r'分開(?:提交|遞交)',zh) and _hit(r'\b(?:submit|file) separate',en):
        zp = _hit(r'(?:只有|只限)[^,。;]{0,12}(?:住址|地址)不同',zh)
        ep = _hit(r'\bsharing an address\b|\b(?:at|with) the same address\b',en)
        if zp and ep and not _hit(r'\bdifferent addresses\b',en):
            compare('address condition for separate applications',_fact('different addresses required',zp),_fact('shared address permitted',ep))

    # Explicit session role, as distinct from a role mentioned in an antecedent.
    compare('role of required session',
            _unique([('new role',r'新崗位的(?:簡介會|培訓)'),('former role',r'(?:原有|舊)崗位的(?:簡介會|培訓)')],zh),
            _unique([('new role',r'\b(?:session|induction|training) for (?:their |the |your )?new role\b'),
                     ('former role',r'\b(?:session|induction|training) for (?:their |the |your )?(?:former|old|previous) role\b')],en))
    # Both versions must explicitly describe queue membership at a cutoff.
    if _hit(r'排隊|隊伍',zh) and _hit(r'\bqueue\b',en):
        compare('queue membership at cutoff',
                _unique([('already queued',r'\d+時已在排隊'),('join after cutoff',r'\d+時後才加入隊伍')],zh),
                _unique([('already queued',r'\balready in the queue at\b'),('join after cutoff',r'\b(?:join|joining) the queue after\b')],en))
    return evidence


def semantic_reasons(chinese, english):
    return [f"{x['category']} differs: Chinese {x['chinese_value']} [{x['chinese_span']}]; English {x['english_value']} [{x['english_span']}]"
            for x in semantic_evidence(chinese,english)]
