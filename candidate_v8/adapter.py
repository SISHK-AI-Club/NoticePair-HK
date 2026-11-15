"""Install V8 over a private frozen namespace, leaving original functions intact."""
from functools import lru_cache
_frozen_notice_check_v8 = check_notice

def _contextual_fallback_v8(chinese,english):
    out=_frozen_notice_check_v8(chinese,english)
    # The inherited date-role heuristic also covers replies and RSVPs. Use a
    # neutral label rather than asserting every deadline is an application.
    out['why']=out['why'].str.replace('application deadline differs:', 'deadline differs:', regex=False)
    return out

@lru_cache(maxsize=512)
def topic_scores_v8(zh,en):
    # Full propositions for NLI, not sentence fragments. Fixed V7 thresholds.
    return (similarity(zh,en), contradiction('本通知涉及'+zh+'。','This notice concerns the '+en+'.'))

def check_notice(chinese_text,english_text):
    parsed=structured_comparison(chinese_text,english_text)
    if parsed is None:
        out=_contextual_fallback_v8(chinese_text,english_text)
        out['decision_path']='frozen_fallback'
        return out
    z,e,evidence=parsed
    sim,contra=topic_scores_v8(z.topic,e.topic)
    # A supported structure does not establish equivalence of the event itself.
    reasons=[]
    subject_uncertain = sim<SIM_T or contra>NLI_T
    # Numeric identifiers in a title must survive semantic matching.
    if set(re.findall(r'\d+',z.topic)) != set(re.findall(r'\d+',e.topic)):
        evidence.append(dict(category='subject identifier',chinese_value=z.topic,english_value=e.topic,chinese_span=z.topic,english_span=e.topic))
    if subject_uncertain and not evidence:
        # Noun-phrase scores are not calibrated like complete notices. Do not
        # create a new alarm solely by removing context. Defer unresolved title
        # equivalence to the existing full-notice checker, preserving its limits.
        out=_contextual_fallback_v8(chinese_text,english_text)
        out['decision_path']='uncertain_subject_fallback'
        out['topic_similarity']=sim
        out['topic_contradiction']=contra
        return out
    for x in evidence:
        reasons.append(f"{x['category']} differs: English {x['english_value']}; Chinese {x['chinese_value']}. Evidence — English [{x['english_span']}]; Chinese [{x['chinese_span']}]")
    return pd.DataFrame([dict(status='⚠️ Check' if reasons else '✅ OK',chinese=chinese_text,english=english_text,why='; '.join(reasons),semantic_evidence=evidence,decision_path='structured_notice',notice_kind=z.kind,topic_similarity=sim,topic_contradiction=contra,english_facts=e.facts,chinese_facts=z.facts)])

CHECKER_VERSION='v8-structured-notice-candidate'
