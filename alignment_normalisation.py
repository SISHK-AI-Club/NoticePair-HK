# Alignment and normalisation revision. Original model weights and thresholds.
from scipy.optimize import linear_sum_assignment
import unicodedata

SIM_T, NLI_T = 0.40, 0.30

def normalise_text(text, lang):
    text = unicodedata.normalize('NFKC', text)
    if lang == 'en':
        text = re.sub(r'\bnoon\b', '12 p.m.', text, flags=re.I)
        text = re.sub(r'\bmidnight\b', '12 a.m.', text, flags=re.I)
    return text

def numbers_en(text):
    text = normalise_text(text, 'en').lower()
    text = re.sub(r'\bone(?=\s+(?:was|were|is|has been|had been)\s+issued\b)', 'it', text)
    nums = {int(n) for n in re.findall(r'\d+', text)}
    words = {**EN_WORDS, 'both': 2, 'second': 2, 'first': 1}
    nums |= {v for k, v in words.items() if re.search(rf'\b{k}\b', text)}
    # Month names count only in explicit date phrases. Modal may reserve is excluded.
    for month, value in MONTHS.items():
        if re.search(rf'\b{month}\s+\d{{1,2}}\b|\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:of\s+)?{month}\b(?!\s+(?:reserve|apply|attend|submit|register|bring)\b)', text):
            nums.add(value)
    return nums

def numbers_zh(text):
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'(星期|週|周|禮拜)[一二三四五六日天]', '', text)
    text = re.sub(r'一併|一同|一起|一致|一般', '', text)
    return {int(n) for n in re.findall(r'\d+', text)} | {cn_to_int(n) for n in re.findall(rf'[{CN_NUM}]+', text)}

def negation_pair(zh, en):
    # Paired grammatical equivalents preserve the meaning of the complete clause.
    if re.search(r'\bunless\b', en, re.I):
        zh = zh.replace('除非', '')
    if re.search(r'\bunder\b|\bbelow\b|less than', en, re.I):
        zh = zh.replace('未滿', '')
    zh = zh.replace('不同', '').replace('不論', '').replace('不管', '')
    return bool(NEG_ZH.search(zh)), has_neg_en(en)

def clock_values(text, lang):
    text = normalise_text(text, lang)
    if lang == 'zh':
        text = re.sub(r'(上午|下午|中午|正午|晚上|凌晨)(\d{1,2})[時点點](至|到)(\d{1,2})[時点點]', lambda m: f'{m[1]}{m[2]}時{m[3]}{m[1]}{m[4]}時', text)
    values = []
    if lang == 'en':
        matches = re.findall(r'\b(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?', text, re.I)
        for hour, minute, half in matches:
            hour = int(hour)
            if 1 <= hour <= 12:
                values.append((hour % 12 + (12 if half.lower() == 'p' else 0)) * 60 + int(minute or 0))
    else:
        matches = re.findall(r'(上午|下午|中午|正午|晚上|凌晨)(\d{1,2})[時点點](?:(\d{1,2})分?)?', text)
        for half, hour, minute in matches:
            hour = int(hour)
            if hour <= 12:
                values.append((hour % 12 + (12 if half in ('下午','中午','正午','晚上') else 0)) * 60 + int(minute or 0))
    return set(values)

def rule_reasons(zh, en):
    reasons = []
    znum, enum = numbers_zh(zh), numbers_en(en)
    if znum != enum:
        reasons.append(f'numbers differ: {sorted(znum-enum)} only in Chinese; {sorted(enum-znum)} only in English')
    zclock, eclock = clock_values(zh, 'zh'), clock_values(en, 'en')
    if zclock and eclock and zclock != eclock:
        fmt = lambda values: ', '.join(f'{v//60:02d}:{v%60:02d}' for v in sorted(values))
        reasons.append(f'clock times differ: Chinese {fmt(zclock)}; English {fmt(eclock)}')
    zn, eneg = negation_pair(zh, en)
    if zn != eneg:
        reasons.append("one version says 'not/no/without' and the other doesn't")
    return reasons + date_role_reasons(zh, en)

def split_zh(text):
    # Keep conditions attached. Split independent availability statements after commas.
    return [s.strip() for s in re.split(r'(?<=[。！？；])|\n|(?<=，)(?=(?:不設|設有))', text) if s.strip()]

def split_en(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])|(?<=;)\s*|\n', text) if s.strip()]

def alignment_text(text, lang):
    text = normalise_text(text, lang)
    # Avoid choosing a different action solely because its number happens to match.
    text = re.sub(r'\d+', ' ', text)
    return text

def checker_flag(zh, en, sim=None, contra=None):
    model_zh, model_en = normalise_text(zh, 'zh'), normalise_text(en, 'en')
    sim = similarity(model_zh, model_en) if sim is None else sim
    contra = contradiction(model_zh, model_en) if contra is None else contra
    reasons = rule_reasons(zh, en) + model_reasons(sim, contra, SIM_T, NLI_T)
    return bool(reasons), reasons

def check_notice(chinese_text, english_text):
    zh, en = split_zh(chinese_text), split_en(english_text)
    if not zh or not en:
        return pd.DataFrame([{'status':'⚠️ Check','chinese':chinese_text,'english':english_text,'why':'Paste both versions first.'}])
    ez = labse.encode([alignment_text(s,'zh') for s in zh], convert_to_tensor=True, normalize_embeddings=True)
    ee = labse.encode([alignment_text(s,'en') for s in en], convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(ez, ee).cpu().numpy()
    # Global assignment prevents two unrelated source sentences reusing one target.
    ii, jj = linear_sum_assignment(-sims)
    matches = dict(zip(ii.tolist(), jj.tolist()))
    used, out = set(), []
    for i, z in enumerate(zh):
        j = matches.get(i)
        if j is None or sims[i,j] < 0.25:
            out.append({'status':'⚠️ Check','chinese':z,'english':'','why':'Needs review: no confident English counterpart'})
            continue
        used.add(j)
        flagged, reasons = checker_flag(z, en[j])
        out.append({'status':'⚠️ Check' if flagged else '✅ OK','chinese':z,'english':en[j],'why':'; '.join(reasons)})
    for j, e in enumerate(en):
        if j not in used:
            out.append({'status':'⚠️ Check','chinese':'','english':e,'why':'Needs review: no confident Chinese counterpart'})
    for reason in date_role_reasons(chinese_text, english_text):
        if not any(reason in row['why'] for row in out):
            out.append({'status':'⚠️ Check','chinese':'(whole notice)','english':'(whole notice)','why':reason})
    return pd.DataFrame(out)
