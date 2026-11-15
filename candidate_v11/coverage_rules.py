"""Corroborated one-way information loss with an explicit extra qualifier.

Operator presence is never enough to flag a pair. Both original bilingual NLI
and translated NLI must support the same direction of information loss.
"""
import re

OPERATORS = [
    ('exception', r'\b(?:unless|except|excluding|exempt)\b', r'除非|除.{0,18}[外以]|豁免|例外|不包括'),
    ('additional requirement', r'\b(?:and|along with|as well as|including|with)\b', r'及|和|與|並|連同|包括|附有'),
]


def unsupported_details(signal, english, chinese):
    found = []
    if signal['translation_quality'] < .7:
        return found
    for direction in (0, 1):
        if not (signal['cross_neutral'][direction] >= .95
                and signal['neutral'][direction] >= .95
                and signal['cross_entailment'][1-direction] >= .85
                and signal['entailment'][1-direction] >= .85):
            continue
        for category, en_pattern, zh_pattern in OPERATORS:
            em = re.search(en_pattern, english, re.I)
            zm = re.search(zh_pattern, chinese)
            if not ((direction == 0 and em and not zm) or
                    (direction == 1 and zm and not em)):
                continue
            match = em if direction == 0 else zm
            text = english if direction == 0 else chinese
            detail = re.split(r'[。！？]|(?<=[.!?])\s+', text[match.start():])[0]
            language = 'English' if direction == 0 else 'Chinese'
            found.append(dict(kind='unsupported_detail', category=category,
                why=f'{language} includes “{detail}”. Both semantic comparisons indicate that this detail is not supported by the other version; check for an omitted or added condition.',
                detail_language=language, unsupported_detail=detail,
                english_span=english, chinese_span=chinese,
                machine_backtranslation=signal['translation'],
                evidence_direction=direction))
    return found
