"""Supported relation checks. Unrecognised constructions remain unresolved.

Developed on the reused 60-case suite and explicit contrast fixtures; not a
general parser and not evidence of general 100% translation accuracy.
"""
import re
import unicodedata

def relation_evidence(chinese,english):
    z=unicodedata.normalize('NFKC',chinese)
    e=unicodedata.normalize('NFKC',english).replace('’',"'")
    out=[]
    def single(patterns,t):
        hits=[(v,m.group()) for v,p in patterns for m in re.finditer(p,t,re.I)]
        return {'value':hits[0][0],'span':hits[0][1]} if len({v for v,_ in hits})==1 else None
    def compare(category,zf,ef):
        if zf and ef and zf['value']!=ef['value']:
            out.append({'category':category,'chinese_value':zf['value'],'english_value':ef['value'],
                        'chinese_span':zf['span'],'english_span':ef['span']})

    if re.search(r'住址證明',z) and re.search(r'\bproof\b',e,re.I):
        compare('parent relationship to proof',
                single([('named person',r'以家長名義(?:發出|簽發)|家長名下'),('issuer',r'由家長(?:簽發|發出)')],z),
                single([('named person',r"in (?:your |the )?parent(?:'s|s') name|issued (?:in|under) (?:your |the )?parent(?:'s|s') name"),
                        ('issuer',r'issued by (?:your |the )?parents?')],e))

    # Explicit proxy subject anchors "your ID" to the represented recipient,
    # and "their own ID" to the proxy. No free pronoun guessing elsewhere.
    if '代領人' in z and re.search(r'\b(?:the|your) proxy\b',e,re.I):
        for role,zowner,eowner in [('recipient',r'(?:收件人|領取人)的',r'(?:your|the recipient\x27s)'),
                                  ('proxy',r'代領人(?:本人)?的',r'(?:their own|the proxy\x27s own)')]:
            zp=[(form,zowner+r'(?:身分|身份)證明文件'+word) for form,word in [('original','正本'),('copy','副本')]]
            ep=[(form,r'\b'+word+r' of '+eowner+r' (?:ID|identity document)\b|\b'+eowner+r' '+word+r' (?:ID|identity document)\b')
                for form,word in [('original','original'),('copy','copy')]]
            compare(role+' ID document form',single(zp,z),single(ep,e))

    # Compare only explicitly supported complete collection conditions.
    if re.search(r'委託他人代領|代領',z) and re.search(r'\bproxy\b',e,re.I):
        compare('condition for proxy collection',
                single([('cannot collect',r'(?:如|若)未能親身取件'),
                        ('cannot attend original slot',r'(?:如|若)未能在原定時段親身取件')],z),
                single([('cannot collect',r"\bif you (?:cannot|can't|are unable to) collect (?:your |the )?(?:parcel|item|package)[.!?]?\s*$"),
                        ('cannot attend original slot',r"\bif you (?:cannot|can't|are unable to) collect (?:your |the )?(?:parcel|item|package) (?:at|during|in) (?:the |your )?(?:original|originally scheduled) (?:slot|time|collection slot|appointment)[.!?]?\s*$")],e))

    if '同行者' in z and '照顧者' in z and re.search(r'\bcompanions?\b',e,re.I) and re.search(r'\bcarers?\b',e,re.I):
        compare('carer requirement for companions',
                single([('both must be carers',r'兩名同行者均為其照顧者'),
                        ('one carer sufficient',r'其中一名同行者為其照顧者')],z),
                single([('both must be carers',r'\bboth companions are (?:their |your )?carers\b'),
                        ('one carer sufficient',r'\b(?:at least )?one companion is (?:their |your )?carer\b')],e))

    compare('registration timing for other eligible applicants',
            single([('registration allowed',r'其他合資格人士仍可報名'),
                    ('after priority period only',r'其他合資格人士須待優先階段結束後才可報名')],z),
            single([('registration allowed',r'\bOther eligible applicants can still register[.!?]?\s*$'),
                    ('after priority period only',r'\bOther eligible applicants (?:can|may) (?:only )?register (?:only )?after the priority (?:period|phase) ends[.!?]?\s*$')],e))
    return out
