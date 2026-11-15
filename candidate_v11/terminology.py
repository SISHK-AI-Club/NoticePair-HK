"""Bounded terminology for translation cross-checks, independent of notice wording.

This is a glossary, not an equivalence verdict or a supported-notice whitelist.
Terms not listed continue through normal contextual translation. No benchmark
identifiers, target wording, labels or gold rationales enter this step.
"""
import re
from opencc import OpenCC
_TO_SIMPLIFIED=OpenCC("t2s")

TERMS = {
    '榕樹':'banyan tree', '樟樹':'camphor tree', '洋紫荊':'orchid tree',
    '相思樹':'acacia tree', '松樹':'pine tree', '橡樹':'oak tree',
    '楓樹':'maple tree', '棕櫚樹':'palm tree', '木棉樹':'cotton tree',
    '柳樹':'willow tree', '銀杏樹':'ginkgo tree',
    '裝裱':'mounting artwork',
    '直向格式':'portrait format', '縱向格式':'portrait format',
    '橫向格式':'landscape format',
    '毫米':'millimetres', '厘米':'centimetres', '公斤':'kilograms',
    '港元':'Hong Kong dollars', '工作天':'working days', '曆日':'calendar days',
    '正本':'original document', '影印本':'photocopy',
    '業主立案法團':"owners' corporation", '業主法團':"owners' corporation",
    '非牟利':'nonprofit', '私隱':'privacy', '電郵':'email',
}
_PATTERN=re.compile('|'.join(map(re.escape,sorted(TERMS,key=len,reverse=True))))

def translation_source(chinese):
    # Anchor known technical terms before generation, so a mistranslated rare
    # word does not masquerade as disagreement with the supplied English.
    return _TO_SIMPLIFIED.convert(_PATTERN.sub(lambda m:' '+TERMS[m[0]]+' ',chinese))
